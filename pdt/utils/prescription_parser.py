"""
Prescription Parser - Extract medications, dosages, and frequencies from text.
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime


class PrescriptionParser:
    """Parse prescription text to extract structured medication information."""
    
    def __init__(self):
        """Initialize prescription parser."""
        # Common medication patterns
        self.medication_patterns = [
            # Generic names
            r'\b(?:lisinopril|enalapril|captopril|ramipril|quinapril)\b',
            r'\b(?:losartan|valsartan|candesartan|irbesartan|telmisartan)\b',
            r'\b(?:sacubitril|entresto|valsartan/sacubitril)\b',
            r'\b(?:metoprolol|carvedilol|bisoprolol|atenolol|propranolol)\b',
            r'\b(?:furosemide|bumetanide|torsemide|hydrochlorothiazide)\b',
            r'\b(?:spironolactone|eplerenone)\b',
            r'\b(?:digoxin|digitoxin)\b',
            r'\b(?:warfarin|apixaban|rivaroxaban|dabigatran)\b',
            r'\b(?:aspirin|clopidogrel|ticagrelor)\b',
            r'\b(?:atorvastatin|simvastatin|rosuvastatin|pravastatin)\b',
            r'\b(?:amiodarone|diltiazem|verapamil)\b',
        ]
        
        # Dosage patterns
        self.dosage_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mg|MG|mcg|MCG|g|G|ml|ML|units|U)',
            r'(\d+(?:\.\d+)?)\s*(?:tablet|tab|cap|capsule|pill)',
        ]
        
        # Frequency patterns
        self.frequency_patterns = [
            r'(?:once|twice|thrice|three times|four times)\s*(?:daily|a day|per day)',
            r'\d+\s*(?:times|X)\s*(?:daily|per day|a day)',
            r'(?:every|q)\s*\d+\s*(?:hours|hrs|h)',
            r'(?:before|after)\s*(?:breakfast|lunch|dinner|meals)',
            r'(?:morning|evening|night|bedtime)',
            r'(?:as needed|prn|when required)',
        ]
        
        # Medication category mapping
        self.medication_categories = {
            'lisinopril': 'ace_inhibitor',
            'enalapril': 'ace_inhibitor',
            'captopril': 'ace_inhibitor',
            'ramipril': 'ace_inhibitor',
            'quinapril': 'ace_inhibitor',
            'losartan': 'arb',
            'valsartan': 'arb',
            'candesartan': 'arb',
            'irbesartan': 'arb',
            'telmisartan': 'arb',
            'sacubitril': 'arni',
            'entresto': 'arni',
            'metoprolol': 'beta_blocker',
            'carvedilol': 'beta_blocker',
            'bisoprolol': 'beta_blocker',
            'atenolol': 'beta_blocker',
            'propranolol': 'beta_blocker',
            'furosemide': 'diuretic',
            'bumetanide': 'diuretic',
            'torsemide': 'diuretic',
            'hydrochlorothiazide': 'diuretic',
            'spironolactone': 'aldosterone_antagonist',
            'eplerenone': 'aldosterone_antagonist',
            'digoxin': 'digoxin',
            'digitoxin': 'digoxin',
            'warfarin': 'anticoagulant',
            'apixaban': 'anticoagulant',
            'rivaroxaban': 'anticoagulant',
            'dabigatran': 'anticoagulant',
        }
    
    def parse(self, prescription_text: str) -> Dict[str, Any]:
        """
        Parse prescription text.
        
        Args:
            prescription_text: Raw prescription text from OCR
            
        Returns:
            Dictionary with parsed information
        """
        # Normalize text
        text = self._normalize_text(prescription_text)
        
        # Extract medications
        medications = self._extract_medications(text)
        
        # Extract patient info if available
        patient_info = self._extract_patient_info(text)
        
        # Extract date if available
        date = self._extract_date(text)
        
        return {
            'medications': medications,
            'patient_info': patient_info,
            'date': date,
            'raw_text': prescription_text,
            'normalized_text': text
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for parsing."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase for matching
        text_lower = text.lower()
        return text
    
    def _extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """Extract medications from text."""
        medications = []
        text_lower = text.lower()
        
        # Find all medication matches
        for pattern in self.medication_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                med_name = match.group(0).lower()
                
                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                # Extract dosage
                dosage = self._extract_dosage(context)
                
                # Extract frequency
                frequency = self._extract_frequency(context)
                
                # Get medication category
                category = self.medication_categories.get(med_name, med_name)
                
                medications.append({
                    'name': med_name,
                    'category': category,
                    'dosage': dosage,
                    'frequency': frequency,
                    'context': context.strip()
                })
        
        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_medications = []
        for med in medications:
            key = med['name']
            if key not in seen:
                seen.add(key)
                unique_medications.append(med)
        
        return unique_medications
    
    def _extract_dosage(self, text: str) -> Optional[str]:
        """Extract dosage from text."""
        for pattern in self.dosage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _extract_frequency(self, text: str) -> Optional[str]:
        """Extract frequency from text."""
        for pattern in self.frequency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient information if available."""
        info = {}
        
        # Age
        age_match = re.search(r'\b(?:age|aged)\s*:?\s*(\d+)', text, re.IGNORECASE)
        if age_match:
            info['age'] = int(age_match.group(1))
        
        # Name (simple pattern)
        name_match = re.search(r'(?:patient|name)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if name_match:
            info['name'] = name_match.group(1)
        
        return info
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        # Common date patterns
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def get_medication_list(self, parsed: Dict[str, Any]) -> List[str]:
        """Get list of medication categories from parsed prescription."""
        return [med['category'] for med in parsed.get('medications', [])]
    
    def get_medication_details(self, parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get detailed medication information."""
        return parsed.get('medications', [])



