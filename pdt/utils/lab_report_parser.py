"""
Lab Report Parser - Extract lab values from text.
"""

import re
from typing import List, Dict, Optional, Any


class LabReportParser:
    """Parse lab report text to extract structured lab values."""
    
    def __init__(self):
        """Initialize lab report parser."""
        # Lab test patterns
        self.lab_patterns = {
            # Cardiac markers
            'ejection_fraction': [
                r'ejection\s+fraction',
                r'ef\s*:',
                r'left\s+ventricular\s+ejection\s+fraction',
                r'lvef'
            ],
            'bnp': [
                r'brain\s+natriuretic\s+peptide',
                r'bnp',
                r'nt-probnp',
                r'nt\s+pro\s+bnp'
            ],
            'troponin': [
                r'troponin',
                r'hs-troponin',
                r'high\s+sensitivity\s+troponin'
            ],
            
            # Basic metabolic panel
            'creatinine': [
                r'creatinine',
                r'serum\s+creatinine',
                r'scr'
            ],
            'sodium': [
                r'sodium',
                r'serum\s+sodium',
                r'na\s*\+'
            ],
            'potassium': [
                r'potassium',
                r'serum\s+potassium',
                r'k\s*\+'
            ],
            'glucose': [
                r'glucose',
                r'blood\s+glucose',
                r'fasting\s+glucose',
                r'fbs'
            ],
            'bun': [
                r'blood\s+urea\s+nitrogen',
                r'bun',
                r'urea'
            ],
            
            # Complete blood count
            'hemoglobin': [
                r'hemoglobin',
                r'hb',
                r'hgb'
            ],
            'hematocrit': [
                r'hematocrit',
                r'hct',
                r'pcv'
            ],
            'wbc': [
                r'white\s+blood\s+cell',
                r'wbc',
                r'leukocyte'
            ],
            'platelet': [
                r'platelet',
                r'plt',
                r'thrombocyte'
            ],
            
            # Lipid panel
            'cholesterol': [
                r'total\s+cholesterol',
                r'(?<![a-z])cholesterol(?!crit)',  # avoid Plateletcrit / Haematocrit
                r'\bTC\b'
            ],
            'ldl': [
                r'ldl',
                r'low\s+density\s+lipoprotein',
                r'ldl-c'
            ],
            'hdl': [
                r'hdl',
                r'high\s+density\s+lipoprotein',
                r'hdl-c'
            ],
            'triglycerides': [
                r'triglyceride',
                r'\bTG\b',
                r'\btrig\b'
            ],
            
            # Liver function
            'alt': [
                r'alt',
                r'alanine\s+aminotransferase',
                r'sgpt'
            ],
            'ast': [
                r'ast',
                r'aspartate\s+aminotransferase',
                r'sgot'
            ],
            
            # Other
            'cpk': [
                r'creatine\s+(?:phospho)?kinase',
                r'\bCPK\b',
                r'\bCK\b(?!\s*D)'
            ],
            'tsh': [
                r'tsh',
                r'thyroid\s+stimulating\s+hormone'
            ]
        }
        
        # Value extraction patterns
        self.value_patterns = [
            r'(\d+(?:\.\d+)?)',  # Simple number
            r'(\d+(?:\.\d+)?)\s*(?:mg/dl|mg/dL|mmol/L|mEq/L|ng/ml|ng/mL|pg/ml|pg/mL|%|units)',
        ]
    
    def parse(self, lab_text: str) -> Dict[str, Any]:
        """
        Parse lab report text.
        
        Args:
            lab_text: Raw lab report text from OCR
            
        Returns:
            Dictionary with parsed lab values
        """
        # Normalize text
        text = self._normalize_text(lab_text)
        
        # Extract lab values
        lab_values = self._extract_lab_values(text)
        
        # Extract patient info if available
        patient_info = self._extract_patient_info(text)
        
        # Extract date if available
        date = self._extract_date(text)
        
        return {
            'lab_values': lab_values,
            'patient_info': patient_info,
            'date': date,
            'raw_text': lab_text,
            'normalized_text': text
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for parsing."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _extract_lab_values(self, text: str) -> Dict[str, Any]:
        """Extract lab values from text."""
        lab_values = {}
        text_lower = text.lower()
        
        for lab_name, patterns in self.lab_patterns.items():
            for pattern in patterns:
                # Search for lab name
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                for match in matches:
                    # Get context around match — wider window for tabular reports
                    start = match.start()
                    end = min(len(text), match.end() + 150)
                    context = text[start:end]
                    
                    # Extract value
                    value = self._extract_value_from_context(context, lab_name)
                    
                    if value is not None:
                        lab_values[lab_name] = {
                            'value': value,
                            'unit': self._extract_unit(context),
                            'context': context.strip()
                        }
                        break  # Found value, move to next lab
        
        return lab_values
    
    def _extract_value_from_context(self, context: str, lab_name: str) -> Optional[float]:
        """Extract numeric value from context.

        Handles both colon-separated (lab: 1.2) and tabular
        (Test Name   1.2   g/dL   ref) formats seen in Indian lab reports.
        """
        patterns = [
            # Colon / equals separated  →  Haemoglobin: 13.7
            r':\s*(\d+(?:\.\d+)?)',
            r'=\s*(\d+(?:\.\d+)?)',
            # Tabular — value followed by a unit  →  13.7 g/dL
            r'(\d+(?:\.\d+)?)\s*(?:g/dL|gm/dl|g/dl|mg/dL|mg/dl|mmol/L|mEq/L|mEq/l|'
            r'ng/mL|ng/ml|pg/mL|pg/ml|%|U/L|u/L|IU/L|iu/l|fL|fl|fl\b|10\^3/uL|'
            r'10\*3/uL|10\'3/uL|10.3/uL|10\xb03/uL|10\xb3/uL|IU/mL|ng/dL|uIU/mL|mU/L|units)',
            # Tabular — plain whitespace-separated number (last resort)
            r'\s+(\d+(?:\.\d+)?)\s',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Ejection fraction is stored as fraction (0–1), not percentage
                    if lab_name == 'ejection_fraction' and value > 1:
                        value = value / 100.0
                    # Sanity-check: reject implausibly large numbers for most labs
                    if value > 100000:
                        continue
                    return value
                except ValueError:
                    continue
        
        return None
    
    def _extract_unit(self, context: str) -> Optional[str]:
        """Extract unit from context."""
        unit_patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg/dl|mg/dL|mmol/L|mEq/L|ng/ml|ng/mL|pg/ml|pg/mL|%|units)',
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(2)
        
        return None
    
    def _extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient information if available."""
        info = {}
        
        # Age
        age_match = re.search(r'\b(?:age|aged)\s*:?\s*(\d+)', text, re.IGNORECASE)
        if age_match:
            info['age'] = int(age_match.group(1))
        
        # Name
        name_match = re.search(r'(?:patient|name)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if name_match:
            info['name'] = name_match.group(1)
        
        return info
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def get_patient_features(self, parsed: Dict[str, Any]) -> Dict[str, float]:
        """Convert parsed lab values to patient features for model."""
        features = {}
        lab_values = parsed.get('lab_values', {})
        
        # Map lab values to feature names
        mapping = {
            'ejection_fraction': 'ejection_fraction',
            'creatinine': 'creatinine',
            'sodium': 'sodium',
            'cholesterol': 'cholesterol',
            'glucose': 'glucose',
            'hemoglobin': 'hemoglobin',
            'cpk': 'cpk',
        }
        
        for lab_name, feature_name in mapping.items():
            if lab_name in lab_values:
                value = lab_values[lab_name].get('value')
                if value is not None:
                    features[feature_name] = float(value)
        
        return features



