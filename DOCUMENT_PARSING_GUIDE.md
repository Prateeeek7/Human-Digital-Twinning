# Document Parsing Guide - Prescriptions & Lab Reports

## Overview

The system can now extract text from prescription images/PDFs and lab reports, parse the information, and automatically get medication recommendations.

## Features

1. **OCR Text Extraction**: Extract text from images (JPG, PNG) and PDFs
2. **Prescription Parsing**: Extract medications, dosages, frequencies
3. **Lab Report Parsing**: Extract lab values (EF, creatinine, BNP, etc.)
4. **Automatic Integration**: Get medication recommendations directly from parsed documents

## Setup

### 1. Install OCR Dependencies

```bash
# Install Python packages
pip install pytesseract pdf2image Pillow

# Install Tesseract OCR (macOS)
brew install tesseract

# Install Tesseract OCR (Linux)
sudo apt-get install tesseract-ocr

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Optional: EasyOCR (More Accurate, Slower)

```bash
pip install easyocr
```

EasyOCR is more accurate but slower and requires more memory. Tesseract is recommended for most use cases.

## Usage

### API Endpoints

#### 1. Upload Prescription

```bash
curl -X POST "http://localhost:8000/documents/upload-prescription" \
  -F "file=@prescription.jpg" \
  -F "get_recommendations=true"
```

**Response:**
```json
{
  "status": "success",
  "file_name": "prescription.jpg",
  "extracted_text": "...",
  "parsed_prescription": {
    "medications": [
      {
        "name": "lisinopril",
        "category": "ace_inhibitor",
        "dosage": "10 mg",
        "frequency": "once daily"
      }
    ],
    "patient_info": {"age": 65},
    "date": "12/21/2024"
  },
  "medications": ["ace_inhibitor", "beta_blocker"],
  "recommendations": {
    "top_recommendation": {...},
    "optimal_combination": {...}
  }
}
```

#### 2. Upload Lab Report

```bash
curl -X POST "http://localhost:8000/documents/upload-lab-report" \
  -F "file=@lab_report.pdf" \
  -F "get_recommendations=true"
```

**Response:**
```json
{
  "status": "success",
  "file_name": "lab_report.pdf",
  "extracted_text": "...",
  "parsed_lab_report": {
    "lab_values": {
      "ejection_fraction": {"value": 0.35, "unit": "%"},
      "creatinine": {"value": 1.2, "unit": "mg/dL"},
      "sodium": {"value": 140.0, "unit": "mEq/L"}
    }
  },
  "patient_features": {
    "ejection_fraction": 0.35,
    "creatinine": 1.2,
    "sodium": 140.0
  },
  "recommendations": {...}
}
```

#### 3. Extract Text Only (No Parsing)

```bash
curl -X POST "http://localhost:8000/documents/extract-text" \
  -F "file=@document.jpg"
```

### Python Usage

```python
from pdt.utils.ocr import DocumentOCR
from pdt.utils.prescription_parser import PrescriptionParser
from pdt.utils.lab_report_parser import LabReportParser

# Initialize
ocr = DocumentOCR()
prescription_parser = PrescriptionParser()
lab_parser = LabReportParser()

# Extract text from image
text = ocr.extract_text_from_image("prescription.jpg")

# Parse prescription
parsed = prescription_parser.parse(text)
medications = prescription_parser.get_medication_list(parsed)

# Parse lab report
lab_text = ocr.extract_text_from_pdf("lab_report.pdf")
lab_parsed = lab_parser.parse(lab_text)
features = lab_parser.get_patient_features(lab_parsed)
```

## Supported Medications

The prescription parser recognizes:

- **ACE Inhibitors**: lisinopril, enalapril, captopril, ramipril, quinapril
- **ARB**: losartan, valsartan, candesartan, irbesartan, telmisartan
- **ARNI**: sacubitril, entresto
- **Beta Blockers**: metoprolol, carvedilol, bisoprolol, atenolol, propranolol
- **Diuretics**: furosemide, bumetanide, torsemide, hydrochlorothiazide
- **Aldosterone Antagonists**: spironolactone, eplerenone
- **Digoxin**: digoxin, digitoxin
- **Anticoagulants**: warfarin, apixaban, rivaroxaban, dabigatran
- **Statins**: atorvastatin, simvastatin, rosuvastatin, pravastatin

## Supported Lab Values

The lab report parser extracts:

- **Cardiac**: Ejection Fraction, BNP, Troponin
- **Metabolic**: Creatinine, Sodium, Potassium, Glucose, BUN
- **Hematology**: Hemoglobin, Hematocrit, WBC, Platelets
- **Lipids**: Total Cholesterol, LDL, HDL, Triglycerides
- **Liver**: ALT, AST
- **Other**: CPK, TSH

## Parsing Examples

### Prescription Text Example

```
PRESCRIPTION

Patient: John Doe
Age: 65
Date: 12/21/2024

Medications:
1. Lisinopril 10 mg once daily
2. Metoprolol 25 mg twice daily
3. Furosemide 40 mg once daily
```

**Parsed Output:**
- Medications: ace_inhibitor, beta_blocker, diuretic
- Dosages: 10 mg, 25 mg, 40 mg
- Frequencies: once daily, twice daily

### Lab Report Text Example

```
LABORATORY REPORT

Ejection Fraction: 35%
Creatinine: 1.2 mg/dL
Sodium: 140 mEq/L
BNP: 450 pg/mL
```

**Parsed Output:**
- ejection_fraction: 0.35
- creatinine: 1.2
- sodium: 140.0
- bnp: 450.0

## Integration with Recommendation System

When you upload a document with `get_recommendations=true`:

1. **Prescription**: Uses extracted medications as current medications
2. **Lab Report**: Uses extracted lab values as patient features
3. **Combined**: Can use both for complete patient profile

The system automatically:
- Checks for drug interactions
- Provides personalized recommendations
- Optimizes medication combinations
- Predicts treatment effects

## Testing

### Test Parsers (No OCR Required)

```bash
python scripts/test_document_parsing.py
```

This tests the parsing logic without requiring OCR setup.

### Test with API

1. Start API server:
```bash
uvicorn pdt.api.main:app --reload
```

2. Upload a file:
```bash
curl -X POST "http://localhost:8000/documents/upload-prescription" \
  -F "file=@your_prescription.jpg" \
  -F "get_recommendations=true"
```

## Troubleshooting

### OCR Not Available

If you see "OCR not available":
1. Install Tesseract: `brew install tesseract` (macOS)
2. Install Python packages: `pip install pytesseract pdf2image Pillow`
3. Restart the API server

### Poor OCR Accuracy

1. Use higher resolution images (300+ DPI)
2. Ensure good image quality (clear, well-lit)
3. Try EasyOCR: `pip install easyocr` (slower but more accurate)
4. Pre-process images (contrast, brightness)

### Parsing Errors

1. Check extracted text: Use `/documents/extract-text` endpoint
2. Verify text format matches expected patterns
3. Review parser patterns in `pdt/utils/prescription_parser.py` and `pdt/utils/lab_report_parser.py`

## File Structure

```
pdt/utils/
├── ocr.py                    # OCR text extraction
├── prescription_parser.py    # Prescription parsing
└── lab_report_parser.py      # Lab report parsing

pdt/api/endpoints/
└── documents.py              # Document upload API
```

## Next Steps

1. **Improve Parsing**: Add more medication patterns and lab tests
2. **Better OCR**: Use specialized medical OCR models
3. **Validation**: Add confidence scores for extracted values
4. **Multi-language**: Support non-English documents
5. **Structured Forms**: Parse specific form formats (e.g., HL7)

## Notes

- OCR accuracy depends on image quality
- Parsing relies on text patterns - may need adjustment for different formats
- All extracted values should be verified by clinicians
- The system is designed to assist, not replace clinical judgment



