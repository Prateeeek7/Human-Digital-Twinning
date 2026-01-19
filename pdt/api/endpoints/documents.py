"""
API endpoints for document upload and parsing (prescriptions, lab reports).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdt.utils.ocr import DocumentOCR
from pdt.utils.prescription_parser import PrescriptionParser
from pdt.utils.lab_report_parser import LabReportParser
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize parsers (lazy loading)
_ocr = None
_prescription_parser = None
_lab_parser = None
_recommender = None


def get_ocr() -> Optional[DocumentOCR]:
    """Get or initialize OCR engine."""
    global _ocr
    if _ocr is None:
        try:
            _ocr = DocumentOCR(use_easyocr=False)  # Use Tesseract by default
        except Exception as e:
            # OCR not available
            return None
    return _ocr


def get_prescription_parser() -> PrescriptionParser:
    """Get or initialize prescription parser."""
    global _prescription_parser
    if _prescription_parser is None:
        _prescription_parser = PrescriptionParser()
    return _prescription_parser


def get_lab_parser() -> LabReportParser:
    """Get or initialize lab report parser."""
    global _lab_parser
    if _lab_parser is None:
        _lab_parser = LabReportParser()
    return _lab_parser


def get_recommender() -> Optional[PersonalizedMedicationRecommender]:
    """Get recommender if available."""
    global _recommender
    if _recommender is None:
        model_path = Path("models/personalized_medication_recommender.pkl")
        if model_path.exists():
            _recommender = PersonalizedMedicationRecommender()
            _recommender.load(str(model_path))
    return _recommender


@router.post("/upload-prescription")
async def upload_prescription(
    file: UploadFile = File(...),
    get_recommendations: bool = False
):
    """
    Upload and parse prescription image/PDF.
    
    Args:
        file: Prescription image or PDF file
        get_recommendations: Whether to get medication recommendations
        
    Returns:
        Parsed prescription data and optionally recommendations
    """
    try:
        # Read file
        file_bytes = await file.read()
        file_type = file.content_type
        
        # Determine file type
        if 'pdf' in file_type.lower() or file.filename.endswith('.pdf'):
            doc_type = 'pdf'
        else:
            doc_type = 'image'
        
        # Extract text using OCR
        ocr = get_ocr()
        if ocr is None:
            raise HTTPException(
                status_code=503,
                detail="OCR not available. Install dependencies: pip install pytesseract pdf2image Pillow"
            )
        text = ocr.extract_text_from_bytes(file_bytes, doc_type)
        
        # Parse prescription
        parser = get_prescription_parser()
        parsed = parser.parse(text)
        
        result = {
            'status': 'success',
            'file_name': file.filename,
            'extracted_text': text,
            'parsed_prescription': parsed,
            'medications': parser.get_medication_list(parsed),
            'medication_details': parser.get_medication_details(parsed)
        }
        
        # Get recommendations if requested
        if get_recommendations:
            recommender = get_recommender()
            if recommender:
                # Try to extract patient info from prescription
                patient_info = parsed.get('patient_info', {})
                
                # Validate model is trained before attempting recommendations
                if not recommender.is_trained:
                    result['recommendations'] = {
                        'error': 'Model is not trained. Cannot provide recommendations. Please train the model first.',
                        'available': False
                    }
                else:
                    try:
                        # Get recommendations
                        recommendations = recommender.get_recommendations(
                            patient_info=patient_info,
                            current_medications=result['medications'],
                            time_horizon_days=90
                        )
                        result['recommendations'] = recommendations
                    except ValueError as e:
                        result['recommendations'] = {
                            'error': str(e),
                            'available': False,
                            'message': 'Insufficient patient data extracted from prescription for recommendations'
                        }
                    except Exception as e:
                        result['recommendations'] = {
                            'error': f'Error generating recommendations: {str(e)}',
                            'available': False
                        }
            else:
                result['recommendations'] = {
                    'error': 'Recommendation model not available. Model file not found.',
                    'available': False
                }
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prescription: {str(e)}"
        )


@router.post("/upload-lab-report")
async def upload_lab_report(
    file: UploadFile = File(...),
    get_recommendations: bool = False
):
    """
    Upload and parse lab report image/PDF.
    
    Args:
        file: Lab report image or PDF file
        get_recommendations: Whether to get medication recommendations
        
    Returns:
        Parsed lab values and optionally recommendations
    """
    try:
        # Read file
        file_bytes = await file.read()
        file_type = file.content_type
        
        # Determine file type
        if 'pdf' in file_type.lower() or file.filename.endswith('.pdf'):
            doc_type = 'pdf'
        else:
            doc_type = 'image'
        
        # Extract text using OCR
        ocr = get_ocr()
        if ocr is None:
            raise HTTPException(
                status_code=503,
                detail="OCR not available. Install dependencies: pip install pytesseract pdf2image Pillow"
            )
        text = ocr.extract_text_from_bytes(file_bytes, doc_type)
        
        # Parse lab report
        parser = get_lab_parser()
        parsed = parser.parse(text)
        
        result = {
            'status': 'success',
            'file_name': file.filename,
            'extracted_text': text,
            'parsed_lab_report': parsed,
            'lab_values': parsed.get('lab_values', {}),
            'patient_features': parser.get_patient_features(parsed)
        }
        
        # Get recommendations if requested
        if get_recommendations:
            recommender = get_recommender()
            if recommender:
                # Get patient features from lab report
                patient_features = result['patient_features']
                
                # Validate model is trained before attempting recommendations
                if not recommender.is_trained:
                    result['recommendations'] = {
                        'error': 'Model is not trained. Cannot provide recommendations. Please train the model first.',
                        'available': False
                    }
                else:
                    try:
                        # Get recommendations
                        recommendations = recommender.get_recommendations(
                            patient_info=patient_features,
                            current_medications=None,
                            time_horizon_days=90
                        )
                        result['recommendations'] = recommendations
                    except ValueError as e:
                        result['recommendations'] = {
                            'error': str(e),
                            'available': False,
                            'message': 'Insufficient patient data extracted from lab report for recommendations'
                        }
                    except Exception as e:
                        result['recommendations'] = {
                            'error': f'Error generating recommendations: {str(e)}',
                            'available': False
                        }
            else:
                result['recommendations'] = {
                    'error': 'Recommendation model not available. Model file not found.',
                    'available': False
                }
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing lab report: {str(e)}"
        )


@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract raw text from image/PDF (no parsing).
    
    Args:
        file: Image or PDF file
        
    Returns:
        Extracted text
    """
    try:
        file_bytes = await file.read()
        file_type = file.content_type
        
        if 'pdf' in file_type.lower() or file.filename.endswith('.pdf'):
            doc_type = 'pdf'
        else:
            doc_type = 'image'
        
        ocr = get_ocr()
        if ocr is None:
            raise HTTPException(
                status_code=503,
                detail="OCR not available. Install dependencies: pip install pytesseract pdf2image Pillow"
            )
        text = ocr.extract_text_from_bytes(file_bytes, doc_type)
        
        return {
            'status': 'success',
            'file_name': file.filename,
            'extracted_text': text
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if document processing service is available."""
    try:
        ocr = get_ocr()
        return {
            "status": "healthy",
            "ocr_available": True,
            "prescription_parser_available": True,
            "lab_parser_available": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

