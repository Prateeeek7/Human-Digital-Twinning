"""
Test document parsing (prescription and lab report).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdt.utils.ocr import DocumentOCR
from pdt.utils.prescription_parser import PrescriptionParser
from pdt.utils.lab_report_parser import LabReportParser


def test_prescription_parsing():
    """Test prescription text parsing."""
    print("="*70)
    print("Testing Prescription Parser")
    print("="*70)
    
    # Sample prescription text (simulated OCR output)
    sample_text = """
    PRESCRIPTION
    
    Patient: John Doe
    Age: 65
    Date: 12/21/2024
    
    Medications:
    1. Lisinopril 10 mg once daily
    2. Metoprolol 25 mg twice daily
    3. Furosemide 40 mg once daily
    4. Spironolactone 25 mg once daily
    
    Take as directed.
    """
    
    parser = PrescriptionParser()
    parsed = parser.parse(sample_text)
    
    print("\nParsed Prescription:")
    print(f"  Medications found: {len(parsed['medications'])}")
    print(f"  Patient info: {parsed['patient_info']}")
    print(f"  Date: {parsed['date']}")
    
    print("\nMedication Details:")
    for med in parsed['medications']:
        print(f"  - {med['name']} ({med['category']})")
        print(f"    Dosage: {med['dosage']}")
        print(f"    Frequency: {med['frequency']}")
    
    print("\nMedication List (for recommendations):")
    med_list = parser.get_medication_list(parsed)
    print(f"  {med_list}")
    
    return parsed


def test_lab_report_parsing():
    """Test lab report text parsing."""
    print("\n" + "="*70)
    print("Testing Lab Report Parser")
    print("="*70)
    
    # Sample lab report text (simulated OCR output)
    sample_text = """
    LABORATORY REPORT
    
    Patient: John Doe
    Age: 65
    Date: 12/21/2024
    
    Test Results:
    Ejection Fraction: 35%
    Creatinine: 1.2 mg/dL
    Sodium: 140 mEq/L
    BNP: 450 pg/mL
    Hemoglobin: 14.5 g/dL
    Total Cholesterol: 180 mg/dL
    Glucose: 95 mg/dL
    """
    
    parser = LabReportParser()
    parsed = parser.parse(sample_text)
    
    print("\nParsed Lab Report:")
    print(f"  Lab values found: {len(parsed['lab_values'])}")
    print(f"  Patient info: {parsed['patient_info']}")
    print(f"  Date: {parsed['date']}")
    
    print("\nLab Values:")
    for lab_name, lab_data in parsed['lab_values'].items():
        print(f"  - {lab_name}: {lab_data['value']} {lab_data.get('unit', '')}")
    
    print("\nPatient Features (for model):")
    features = parser.get_patient_features(parsed)
    print(f"  {features}")
    
    return parsed


def test_ocr_simulation():
    """Test OCR functionality (simulated - requires actual image/PDF)."""
    print("\n" + "="*70)
    print("OCR Testing (Simulated)")
    print("="*70)
    
    print("\nNote: To test actual OCR:")
    print("  1. Install Tesseract: brew install tesseract (macOS)")
    print("  2. Install dependencies: pip install pytesseract pdf2image Pillow")
    print("  3. Use API endpoint: POST /documents/upload-prescription")
    
    try:
        ocr = DocumentOCR(use_easyocr=False)
        print("\n✓ OCR engine initialized (Tesseract)")
    except Exception as e:
        print(f"\n✗ OCR not available: {e}")
        print("  Install Tesseract first")


if __name__ == "__main__":
    # Test prescription parsing
    prescription = test_prescription_parsing()
    
    # Test lab report parsing
    lab_report = test_lab_report_parsing()
    
    # Test OCR (simulated)
    test_ocr_simulation()
    
    print("\n" + "="*70)
    print("Testing Complete")
    print("="*70)
    print("\nTo use with actual images/PDFs:")
    print("  1. Start API: uvicorn pdt.api.main:app --reload")
    print("  2. Upload file: POST /documents/upload-prescription")
    print("  3. Get recommendations: Set get_recommendations=true")



