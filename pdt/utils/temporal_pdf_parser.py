"""
Temporal PDF Parser - Extract time-series medical data from multi-page PDFs.
Clinical-grade parser for extracting lab values, vitals, and medications with dates.

This module is designed for first-stage clinical trials and includes:
- Multi-page PDF processing (100s of pages)
- Date extraction and normalization
- Value-to-date linking
- Time-series data structure
- Clinical validation
"""

import re
import io
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from pdt.utils.ocr import DocumentOCR
from pdt.utils.lab_report_parser import LabReportParser


class TemporalPDFParser:
    """
    Clinical-grade parser for extracting temporal medical data from multi-page PDFs.
    
    Features:
    - Processes 100s of pages efficiently
    - Extracts dates in multiple formats
    - Links lab values to dates
    - Creates time-series data structures
    - Validates data for clinical use
    """
    
    def __init__(self, use_easyocr: bool = False):
        """
        Initialize temporal PDF parser.
        
        Args:
            use_easyocr: Use EasyOCR for better accuracy (slower)
        """
        self.ocr = DocumentOCR(use_easyocr=use_easyocr)
        self.lab_parser = LabReportParser()
        
        # Date patterns for extraction
        self.date_patterns = [
            # Standard formats
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',  # MM/DD/YYYY or DD-MM-YYYY
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY-MM-DD
            # Written formats
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{2,4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{2,4})\b',
            # Relative dates
            r'\b(\d+)\s+(day|week|month|year)s?\s+ago\b',
            r'\b(last|previous)\s+(day|week|month|year)\b',
            # Report headers
            r'Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Report\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Collection\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        # Month abbreviations
        self.month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # Lab value patterns (expanded from base parser)
        self.lab_patterns = {
            # Cardiac markers
            'ejection_fraction': [r'ejection\s+fraction', r'ef\s*[:=]', r'lvef', r'lv\s+ef'],
            'bnp': [r'brain\s+natriuretic\s+peptide', r'bnp', r'nt-probnp', r'nt\s+pro\s+bnp'],
            'nt_probnp': [r'nt-probnp', r'nt\s+pro\s+bnp'],
            'troponin': [r'troponin', r'hs-troponin', r'high\s+sensitivity\s+troponin', r'troponin\s+i', r'troponin\s+t'],
            'ck_mb': [r'ck-mb', r'creatine\s+kinase\s+mb', r'ckmb'],
            
            # Basic metabolic panel
            'creatinine': [r'creatinine', r'serum\s+creatinine', r'scr', r'creat'],
            'egfr': [r'egfr', r'estimated\s+glomerular\s+filtration\s+rate', r'gfr'],
            'sodium': [r'sodium', r'serum\s+sodium', r'na\s*\+', r'na\+'],
            'potassium': [r'potassium', r'serum\s+potassium', r'k\s*\+', r'k\+'],
            'chloride': [r'chloride', r'cl\s*\-', r'cl\-'],
            'bicarbonate': [r'bicarbonate', r'hco3', r'co2'],
            'glucose': [r'glucose', r'blood\s+glucose', r'fasting\s+glucose', r'fbs', r'random\s+glucose'],
            'bun': [r'blood\s+urea\s+nitrogen', r'bun', r'urea'],
            'calcium': [r'calcium', r'serum\s+calcium', r'ca\s*\+', r'ca\+'],
            'phosphorus': [r'phosphorus', r'phosphate', r'phos'],
            'magnesium': [r'magnesium', r'mg\s*\+', r'mg\+'],
            
            # Complete blood count
            'hemoglobin': [r'hemoglobin', r'hb', r'hgb'],
            'hematocrit': [r'hematocrit', r'hct', r'pcv'],
            'wbc': [r'white\s+blood\s+cell', r'wbc', r'leukocyte', r'white\s+cell\s+count'],
            'rbc': [r'red\s+blood\s+cell', r'rbc', r'erythrocyte'],
            'platelet': [r'platelet', r'plt', r'thrombocyte', r'platelet\s+count'],
            'mcv': [r'mcv', r'mean\s+corpuscular\s+volume'],
            'mch': [r'mch', r'mean\s+corpuscular\s+hemoglobin'],
            'mchc': [r'mchc', r'mean\s+corpuscular\s+hemoglobin\s+concentration'],
            'rdw': [r'rdw', r'red\s+cell\s+distribution\s+width'],
            'neutrophil': [r'neutrophil', r'neut', r'absolute\s+neutrophil'],
            'lymphocyte': [r'lymphocyte', r'lymph', r'absolute\s+lymphocyte'],
            'monocyte': [r'monocyte', r'mono', r'absolute\s+monocyte'],
            'eosinophil': [r'eosinophil', r'eos', r'absolute\s+eosinophil'],
            'basophil': [r'basophil', r'baso', r'absolute\s+basophil'],
            
            # Lipid panel
            'cholesterol': [r'total\s+cholesterol', r'cholesterol', r'tc'],
            'ldl': [r'ldl', r'low\s+density\s+lipoprotein', r'ldl-c'],
            'hdl': [r'hdl', r'high\s+density\s+lipoprotein', r'hdl-c'],
            'triglycerides': [r'triglyceride', r'tg', r'trig'],
            'non_hdl_cholesterol': [r'non-hdl\s+cholesterol', r'non\s+hdl'],
            
            # Liver function
            'alt': [r'alt', r'alanine\s+aminotransferase', r'sgpt'],
            'ast': [r'ast', r'aspartate\s+aminotransferase', r'sgot'],
            'alkaline_phosphatase': [r'alkaline\s+phosphatase', r'alk\s+phos', r'alp'],
            'bilirubin_total': [r'total\s+bilirubin', r'bilirubin', r'tbili'],
            'bilirubin_direct': [r'direct\s+bilirubin', r'conjugated\s+bilirubin', r'dbili'],
            'bilirubin_indirect': [r'indirect\s+bilirubin', r'unconjugated\s+bilirubin'],
            'albumin': [r'albumin'],
            'total_protein': [r'total\s+protein', r'protein'],
            'pt': [r'prothrombin\s+time', r'pt'],
            'inr': [r'inr', r'international\s+normalized\s+ratio'],
            'aptt': [r'aptt', r'ptt', r'activated\s+partial\s+thromboplastin\s+time'],
            
            # Thyroid function
            'tsh': [r'tsh', r'thyroid\s+stimulating\s+hormone'],
            't3': [r't3', r'triiodothyronine', r'free\s+t3', r'ft3'],
            't4': [r't4', r'thyroxine', r'free\s+t4', r'ft4'],
            
            # Inflammatory markers
            'crp': [r'c-reactive\s+protein', r'crp', r'hs-crp', r'high\s+sensitivity\s+crp'],
            'esr': [r'esr', r'erythrocyte\s+sedimentation\s+rate', r'sed\s+rate'],
            'ferritin': [r'ferritin'],
            'vitamin_d': [r'vitamin\s+d', r'25-oh\s+vitamin\s+d', r'25ohd'],
            'b12': [r'vitamin\s+b12', r'b12', r'cyanocobalamin'],
            'folate': [r'folate', r'folic\s+acid'],
            
            # Other important markers
            'cpk': [r'creatine\s+phosphokinase', r'cpk', r'ck'],
            'ldh': [r'ldh', r'lactate\s+dehydrogenase'],
            'uric_acid': [r'uric\s+acid', r'urate'],
            'lactate': [r'lactate', r'lactic\s+acid'],
            'procalcitonin': [r'procalcitonin', r'pct'],
            'd_dimer': [r'd-dimer', r'ddimer'],
        }
        
        # Vital signs patterns
        self.vital_patterns = {
            'systolic_bp': [r'systolic\s+bp', r'sbp', r'systolic\s+blood\s+pressure', r'systolic'],
            'diastolic_bp': [r'diastolic\s+bp', r'dbp', r'diastolic\s+blood\s+pressure', r'diastolic'],
            'heart_rate': [r'heart\s+rate', r'hr', r'pulse', r'pulse\s+rate'],
            'respiratory_rate': [r'respiratory\s+rate', r'rr', r'respiration\s+rate'],
            'temperature': [r'temperature', r'temp', r'body\s+temp'],
            'oxygen_saturation': [r'oxygen\s+saturation', r'spo2', r'o2\s+sat', r'sat'],
            'weight': [r'weight', r'wt', r'body\s+weight'],
            'bmi': [r'bmi', r'body\s+mass\s+index'],
        }
    
    def parse_multi_page_pdf(
        self,
        pdf_path: str,
        patient_id: Optional[str] = None,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Parse multi-page PDF and extract temporal medical data.
        
        Args:
            pdf_path: Path to PDF file
            patient_id: Optional patient identifier
            reference_date: Reference date for relative dates (defaults to today)
            
        Returns:
            Dictionary with:
            - temporal_lab_values: DataFrame with date, lab_name, value, unit
            - temporal_vitals: DataFrame with date, vital_name, value
            - document_metadata: Information about the document
            - extraction_quality: Quality metrics
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        print(f"Processing PDF: {pdf_path}")
        print(f"Reference date: {reference_date.strftime('%Y-%m-%d')}")
        
        # Extract text from all pages
        all_pages_text = self._extract_all_pages(pdf_path)
        
        print(f"Extracted text from {len(all_pages_text)} pages")
        
        # Extract temporal data
        temporal_labs = []
        temporal_vitals = []
        document_dates = []
        
        for page_num, page_text in enumerate(all_pages_text, 1):
            # Extract dates from this page
            page_dates = self._extract_dates_from_text(page_text, reference_date)
            document_dates.extend([(page_num, d) for d in page_dates])
            
            # Extract lab values with dates
            page_labs = self._extract_lab_values_with_dates(
                page_text, page_num, page_dates, reference_date
            )
            temporal_labs.extend(page_labs)
            
            # Extract vitals with dates
            page_vitals = self._extract_vitals_with_dates(
                page_text, page_num, page_dates, reference_date
            )
            temporal_vitals.extend(page_vitals)
        
        # Create DataFrames
        labs_df = self._create_temporal_dataframe(temporal_labs, 'lab')
        vitals_df = self._create_temporal_dataframe(temporal_vitals, 'vital')
        
        # Determine primary document date
        primary_date = self._determine_primary_date(document_dates, reference_date)
        
        # Calculate extraction quality metrics
        quality_metrics = self._calculate_quality_metrics(
            temporal_labs, temporal_vitals, document_dates
        )
        
        return {
            'patient_id': patient_id,
            'temporal_lab_values': labs_df,
            'temporal_vitals': vitals_df,
            'document_metadata': {
                'pdf_path': pdf_path,
                'total_pages': len(all_pages_text),
                'primary_date': primary_date.isoformat() if primary_date else None,
                'date_range': self._get_date_range(document_dates),
                'extraction_timestamp': datetime.now().isoformat()
            },
            'extraction_quality': quality_metrics
        }
    
    def _extract_all_pages(self, pdf_path: str) -> List[str]:
        """Extract text from all pages of PDF."""
        try:
            text = self.ocr.extract_text_from_pdf(pdf_path)
            # Split by page markers if present
            pages = text.split('--- Page')
            if len(pages) > 1:
                # Remove page markers and clean
                pages = [p.split('---\n', 1)[-1].strip() if '---\n' in p else p.strip() 
                        for p in pages[1:]]  # Skip first empty part
            else:
                # Try to split by common page break patterns
                pages = re.split(r'\n\s*\n\s*\n', text)
            
            return [p.strip() for p in pages if p.strip()]
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_dates_from_text(
        self,
        text: str,
        reference_date: datetime
    ) -> List[datetime]:
        """Extract all dates from text."""
        dates = []
        text_lower = text.lower()
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = match.group(0)
                    parsed_date = self._parse_date(date_str, reference_date)
                    if parsed_date:
                        dates.append(parsed_date)
                except Exception:
                    continue
        
        # Remove duplicates and sort
        dates = sorted(list(set(dates)))
        return dates
    
    def _parse_date(self, date_str: str, reference_date: datetime) -> Optional[datetime]:
        """Parse date string to datetime object."""
        date_str = date_str.strip()
        
        # Handle relative dates
        if 'ago' in date_str.lower():
            match = re.search(r'(\d+)\s+(day|week|month|year)s?\s+ago', date_str.lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                if unit == 'day':
                    return reference_date - timedelta(days=amount)
                elif unit == 'week':
                    return reference_date - timedelta(weeks=amount)
                elif unit == 'month':
                    return reference_date - relativedelta(months=amount)
                elif unit == 'year':
                    return reference_date - relativedelta(years=amount)
        
        if 'last' in date_str.lower() or 'previous' in date_str.lower():
            match = re.search(r'(last|previous)\s+(day|week|month|year)', date_str.lower())
            if match:
                unit = match.group(2)
                if unit == 'day':
                    return reference_date - timedelta(days=1)
                elif unit == 'week':
                    return reference_date - timedelta(weeks=1)
                elif unit == 'month':
                    return reference_date - relativedelta(months=1)
                elif unit == 'year':
                    return reference_date - relativedelta(years=1)
        
        # Try standard date parsing
        try:
            # Try dateutil parser first
            parsed = date_parser.parse(date_str, default=reference_date)
            # Validate reasonable date range (not too far in past/future)
            if parsed.year >= 1900 and parsed.year <= reference_date.year + 1:
                return parsed
        except Exception:
            pass
        
        # Try manual parsing for common formats
        # MM/DD/YYYY or DD-MM-YYYY
        match = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
        if match:
            part1, part2, part3 = match.groups()
            year = int(part3)
            if year < 100:
                year += 2000 if year < 50 else 1900
            
            # Try both MM/DD and DD/MM
            try:
                return datetime(year, int(part1), int(part2))
            except ValueError:
                try:
                    return datetime(year, int(part2), int(part1))
                except ValueError:
                    pass
        
        return None
    
    def _extract_lab_values_with_dates(
        self,
        text: str,
        page_num: int,
        page_dates: List[datetime],
        reference_date: datetime
    ) -> List[Dict[str, Any]]:
        """Extract lab values and link them to dates."""
        results = []
        text_lower = text.lower()
        
        # Use the most recent date on page, or reference date
        page_date = page_dates[-1] if page_dates else reference_date
        
        for lab_name, patterns in self.lab_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                for match in matches:
                    # Get context around match
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    # Extract value
                    value = self._extract_value_from_context(context, lab_name)
                    
                    if value is not None:
                        # Try to find date near this value
                        value_date = self._find_date_near_value(context, page_dates, reference_date)
                        
                        # Extract unit
                        unit = self._extract_unit(context)
                        
                        # Validate value
                        if self._validate_lab_value(lab_name, value):
                            results.append({
                                'date': value_date.isoformat(),
                                'lab_name': lab_name,
                                'value': float(value),
                                'unit': unit,
                                'page_number': page_num,
                                'context': context.strip()[:200]  # Limit context length
                            })
                        break  # Found value, move to next lab
        
        return results
    
    def _extract_vitals_with_dates(
        self,
        text: str,
        page_num: int,
        page_dates: List[datetime],
        reference_date: datetime
    ) -> List[Dict[str, Any]]:
        """Extract vital signs and link them to dates."""
        results = []
        text_lower = text.lower()
        
        page_date = page_dates[-1] if page_dates else reference_date
        
        for vital_name, patterns in self.vital_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    value = self._extract_value_from_context(context, vital_name)
                    
                    if value is not None:
                        value_date = self._find_date_near_value(context, page_dates, reference_date)
                        unit = self._extract_unit(context)
                        
                        if self._validate_vital_value(vital_name, value):
                            results.append({
                                'date': value_date.isoformat(),
                                'vital_name': vital_name,
                                'value': float(value),
                                'unit': unit,
                                'page_number': page_num,
                                'context': context.strip()[:200]
                            })
                        break
        
        return results
    
    def _extract_value_from_context(self, context: str, name: str) -> Optional[float]:
        """Extract numeric value from context."""
        # Patterns to find values
        patterns = [
            r':\s*(\d+(?:\.\d+)?)',
            r'=\s*(\d+(?:\.\d+)?)',
            r'\s+(\d+(?:\.\d+)?)\s*(?:mg/dl|mg/dL|mmol/L|mEq/L|ng/ml|ng/mL|pg/ml|pg/mL|%|units|bpm|mmhg|°f|°c)',
            r'\s+(\d+(?:\.\d+)?)\s*$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Special handling for percentages (ejection fraction)
                    if name == 'ejection_fraction' and value > 1 and value <= 100:
                        value = value / 100.0
                    return value
                except ValueError:
                    continue
        
        return None
    
    def _extract_unit(self, context: str) -> Optional[str]:
        """Extract unit from context."""
        unit_patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg/dl|mg/dL|mmol/L|mEq/L|ng/ml|ng/mL|pg/ml|pg/mL|%|units|bpm|mmhg|°f|°c)',
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(2).lower()
        
        return None
    
    def _find_date_near_value(
        self,
        context: str,
        page_dates: List[datetime],
        reference_date: datetime
    ) -> datetime:
        """Find the date closest to a value in context."""
        # Look for dates in context
        context_dates = self._extract_dates_from_text(context, reference_date)
        
        if context_dates:
            return context_dates[-1]  # Most recent date in context
        
        if page_dates:
            return page_dates[-1]  # Most recent date on page
        
        return reference_date
    
    def _validate_lab_value(self, lab_name: str, value: float) -> bool:
        """Validate lab value is within reasonable clinical range."""
        # Define reasonable ranges for common labs
        ranges = {
            'ejection_fraction': (0.15, 0.80),
            'creatinine': (0.3, 15.0),
            'sodium': (100, 160),
            'potassium': (2.0, 8.0),
            'glucose': (40, 600),
            'hemoglobin': (5.0, 25.0),
            'wbc': (0.5, 100.0),
            'platelet': (10, 2000),
        }
        
        if lab_name in ranges:
            min_val, max_val = ranges[lab_name]
            return min_val <= value <= max_val
        
        # For unknown labs, allow reasonable range
        return 0 < value < 10000
    
    def _validate_vital_value(self, vital_name: str, value: float) -> bool:
        """Validate vital sign value is within reasonable range."""
        ranges = {
            'systolic_bp': (50, 250),
            'diastolic_bp': (30, 150),
            'heart_rate': (30, 200),
            'respiratory_rate': (8, 40),
            'temperature': (90, 110),  # Fahrenheit
            'oxygen_saturation': (70, 100),
            'weight': (20, 500),  # kg
            'bmi': (10, 60),
        }
        
        if vital_name in ranges:
            min_val, max_val = ranges[vital_name]
            return min_val <= value <= max_val
        
        return True
    
    def _create_temporal_dataframe(
        self,
        data: List[Dict[str, Any]],
        data_type: str
    ) -> pd.DataFrame:
        """Create DataFrame from temporal data."""
        if not data:
            # Return empty DataFrame with proper columns
            if data_type == 'lab':
                return pd.DataFrame(columns=['date', 'lab_name', 'value', 'unit', 'page_number', 'context'])
            else:
                return pd.DataFrame(columns=['date', 'vital_name', 'value', 'unit', 'page_number', 'context'])
        
        df = pd.DataFrame(data)
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        return df
    
    def _determine_primary_date(
        self,
        document_dates: List[Tuple[int, datetime]],
        reference_date: datetime
    ) -> Optional[datetime]:
        """Determine the primary document date."""
        if not document_dates:
            return None
        
        # Use most recent date
        dates = [d[1] for d in document_dates]
        return max(dates)
    
    def _get_date_range(self, document_dates: List[Tuple[int, datetime]]) -> Optional[Dict[str, str]]:
        """Get date range from document."""
        if not document_dates:
            return None
        
        dates = [d[1] for d in document_dates]
        return {
            'earliest': min(dates).isoformat(),
            'latest': max(dates).isoformat()
        }
    
    def _calculate_quality_metrics(
        self,
        temporal_labs: List[Dict],
        temporal_vitals: List[Dict],
        document_dates: List[Tuple[int, datetime]]
    ) -> Dict[str, Any]:
        """Calculate extraction quality metrics."""
        total_labs = len(temporal_labs)
        total_vitals = len(temporal_vitals)
        total_dates = len(set(d[1] for d in document_dates))
        
        # Count labs with dates
        labs_with_dates = sum(1 for lab in temporal_labs if lab.get('date'))
        vitals_with_dates = sum(1 for vital in temporal_vitals if vital.get('date'))
        
        return {
            'total_lab_values_extracted': total_labs,
            'total_vitals_extracted': total_vitals,
            'total_dates_found': total_dates,
            'labs_with_dates': labs_with_dates,
            'vitals_with_dates': vitals_with_dates,
            'date_coverage_labs': labs_with_dates / total_labs if total_labs > 0 else 0,
            'date_coverage_vitals': vitals_with_dates / total_vitals if total_vitals > 0 else 0,
            'extraction_completeness': 'high' if total_labs > 10 and total_dates > 0 else 'medium' if total_labs > 0 else 'low'
        }
