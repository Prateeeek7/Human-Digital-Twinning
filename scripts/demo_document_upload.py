"""
Demo script showing how to use document parsing with API.
"""

import requests
import json
from pathlib import Path


def demo_prescription_upload():
    """Demo prescription upload."""
    print("="*70)
    print("Prescription Upload Demo")
    print("="*70)
    
    print("\nTo upload a prescription:")
    print("1. Start API: uvicorn pdt.api.main:app --reload")
    print("2. Run this command:")
    print("\n   curl -X POST 'http://localhost:8000/documents/upload-prescription' \\")
    print("     -F 'file=@prescription.jpg' \\")
    print("     -F 'get_recommendations=true'")
    
    print("\nOr use Python requests:")
    print("""
    import requests
    
    with open('prescription.jpg', 'rb') as f:
        response = requests.post(
            'http://localhost:8000/documents/upload-prescription',
            files={'file': f},
            data={'get_recommendations': 'true'}
        )
    
    result = response.json()
    print(result['medications'])
    print(result['recommendations'])
    """)


def demo_lab_report_upload():
    """Demo lab report upload."""
    print("\n" + "="*70)
    print("Lab Report Upload Demo")
    print("="*70)
    
    print("\nTo upload a lab report:")
    print("1. Start API: uvicorn pdt.api.main:app --reload")
    print("2. Run this command:")
    print("\n   curl -X POST 'http://localhost:8000/documents/upload-lab-report' \\")
    print("     -F 'file=@lab_report.pdf' \\")
    print("     -F 'get_recommendations=true'")
    
    print("\nOr use Python requests:")
    print("""
    import requests
    
    with open('lab_report.pdf', 'rb') as f:
        response = requests.post(
            'http://localhost:8000/documents/upload-lab-report',
            files={'file': f},
            data={'get_recommendations': 'true'}
        )
    
    result = response.json()
    print(result['lab_values'])
    print(result['patient_features'])
    print(result['recommendations'])
    """)


def demo_text_extraction():
    """Demo text extraction only."""
    print("\n" + "="*70)
    print("Text Extraction Demo")
    print("="*70)
    
    print("\nTo extract text only (no parsing):")
    print("\n   curl -X POST 'http://localhost:8000/documents/extract-text' \\")
    print("     -F 'file=@document.jpg'")
    
    print("\nThis returns the raw extracted text for review.")


if __name__ == "__main__":
    demo_prescription_upload()
    demo_lab_report_upload()
    demo_text_extraction()
    
    print("\n" + "="*70)
    print("Setup Instructions")
    print("="*70)
    print("\n1. Install OCR dependencies:")
    print("   pip install pytesseract pdf2image Pillow")
    print("\n2. Install Tesseract:")
    print("   brew install tesseract  # macOS")
    print("   sudo apt-get install tesseract-ocr  # Linux")
    print("\n3. Start API server:")
    print("   uvicorn pdt.api.main:app --reload")
    print("\n4. Upload documents using the examples above")
    print("\nSee DOCUMENT_PARSING_GUIDE.md for complete documentation")



