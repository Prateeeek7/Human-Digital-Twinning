"""
API endpoints for temporal data extraction from multi-page PDFs.
Clinical-grade endpoints for bulk document processing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdt.utils.temporal_pdf_parser import TemporalPDFParser
from pdt.data.clinical_patient_database import ClinicalPatientDatabase
import pandas as pd

router = APIRouter(prefix="/temporal-data", tags=["temporal-data"])

# Initialize components (lazy loading)
_temporal_parser = None
_clinical_db = None


def get_temporal_parser() -> TemporalPDFParser:
    """Get or initialize temporal PDF parser."""
    global _temporal_parser
    if _temporal_parser is None:
        _temporal_parser = TemporalPDFParser(use_easyocr=False)  # Use Tesseract for speed
    return _temporal_parser


def get_clinical_db() -> ClinicalPatientDatabase:
    """Get or initialize clinical database."""
    global _clinical_db
    if _clinical_db is None:
        _clinical_db = ClinicalPatientDatabase()
    return _clinical_db


class BulkUploadRequest(BaseModel):
    """Request for bulk PDF upload."""
    patient_id: str = Field(..., description="Patient identifier")
    reference_date: Optional[str] = Field(None, description="Reference date for relative dates (ISO format)")
    auto_import: bool = Field(True, description="Automatically import extracted data to database")


class TemporalDataResponse(BaseModel):
    """Response model for temporal data extraction."""
    patient_id: str
    document_metadata: Dict[str, Any]
    extraction_quality: Dict[str, Any]
    lab_values_count: int
    vitals_count: int
    date_range: Optional[Dict[str, str]]
    imported: bool


@router.post("/upload-pdf", response_model=TemporalDataResponse)
async def upload_multi_page_pdf(
    file: UploadFile = File(...),
    patient_id: str = None,
    reference_date: Optional[str] = None,
    auto_import: bool = True,
    background_tasks: BackgroundTasks = None
):
    """
    Upload and parse multi-page PDF for temporal data extraction.
    
    This endpoint:
    - Processes PDFs with 100s of pages
    - Extracts lab values with dates
    - Extracts vital signs with dates
    - Links values to timestamps
    - Optionally imports to clinical database
    
    Args:
        file: PDF file (can be 100s of pages)
        patient_id: Patient identifier (required if auto_import=True)
        reference_date: Reference date for relative dates (ISO format)
        auto_import: Automatically import extracted data to database
        
    Returns:
        Extraction results with quality metrics
    """
    if auto_import and not patient_id:
        raise HTTPException(
            status_code=400,
            detail="patient_id is required when auto_import=True"
        )
    
    # Parse reference date
    ref_date = None
    if reference_date:
        try:
            ref_date = datetime.fromisoformat(reference_date.replace('Z', '+00:00'))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid reference_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
    
    # Save uploaded file temporarily
    file_bytes = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
    try:
        # Parse PDF
        parser = get_temporal_parser()
        result = parser.parse_multi_page_pdf(
            pdf_path=tmp_path,
            patient_id=patient_id,
            reference_date=ref_date
        )
        
        # Import to database if requested
        imported = False
        if auto_import and patient_id:
            clinical_db = get_clinical_db()
            
            # Convert DataFrames to lists
            lab_data = []
            if not result['temporal_lab_values'].empty:
                for _, row in result['temporal_lab_values'].iterrows():
                    lab_data.append({
                        'date': row['date'].isoformat() if pd.notna(row['date']) else None,
                        'lab_name': row['lab_name'],
                        'value': row['value'],
                        'unit': row.get('unit'),
                        'page_number': row.get('page_number'),
                        'context': row.get('context', ''),
                        'source': 'pdf_extraction'
                    })
            
            vital_data = []
            if not result['temporal_vitals'].empty:
                for _, row in result['temporal_vitals'].iterrows():
                    vital_data.append({
                        'date': row['date'].isoformat() if pd.notna(row['date']) else None,
                        'vital_name': row['vital_name'],
                        'value': row['value'],
                        'unit': row.get('unit'),
                        'source': 'pdf_extraction'
                    })
            
            # Bulk insert
            labs_inserted = clinical_db.add_lab_values_bulk(patient_id, lab_data)
            vitals_inserted = clinical_db.add_vitals_bulk(patient_id, vital_data)
            
            # Save document metadata
            clinical_db.save_document_metadata(
                patient_id=patient_id,
                document_type='lab_report',
                file_name=file.filename,
                file_path=None,  # Don't store file path for security
                total_pages=result['document_metadata']['total_pages'],
                extraction_quality=result['extraction_quality']['extraction_completeness'],
                extraction_metadata=result['extraction_quality']
            )
            
            imported = True
        
        # Prepare response
        response_data = {
            'patient_id': patient_id or 'unknown',
            'document_metadata': result['document_metadata'],
            'extraction_quality': result['extraction_quality'],
            'lab_values_count': len(result['temporal_lab_values']),
            'vitals_count': len(result['temporal_vitals']),
            'date_range': result['document_metadata'].get('date_range'),
            'imported': imported
        }
        
        if imported:
            response_data['imported_counts'] = {
                'labs': labs_inserted,
                'vitals': vitals_inserted
            }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/patient/{patient_id}/labs")
async def get_patient_labs(
    patient_id: str,
    lab_names: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get time-series lab values for a patient.
    
    Args:
        patient_id: Patient identifier
        lab_names: Comma-separated list of lab names to filter
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
    """
    try:
        clinical_db = get_clinical_db()
        
        # Parse parameters
        lab_list = None
        if lab_names:
            lab_list = [name.strip() for name in lab_names.split(',')]
        
        start_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        end_dt = None
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get data
        df = clinical_db.get_lab_values_timeseries(
            patient_id=patient_id,
            lab_names=lab_list,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Convert to JSON
        if df.empty:
            return {
                'patient_id': patient_id,
                'lab_values': [],
                'count': 0
            }
        
        # Convert to list of dicts
        lab_values = []
        for _, row in df.iterrows():
            lab_values.append({
                'timestamp': row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                'lab_name': row['lab_name'],
                'value': float(row['value']) if pd.notna(row['value']) else None,
                'unit': row.get('unit'),
                'flag': row.get('flag'),
                'validated': bool(row.get('validated', False))
            })
        
        return {
            'patient_id': patient_id,
            'lab_values': lab_values,
            'count': len(lab_values),
            'date_range': {
                'earliest': df['timestamp'].min().isoformat() if not df.empty else None,
                'latest': df['timestamp'].max().isoformat() if not df.empty else None
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving lab values: {str(e)}"
        )


@router.get("/patient/{patient_id}/vitals")
async def get_patient_vitals(
    patient_id: str,
    vital_names: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get time-series vital signs for a patient."""
    try:
        clinical_db = get_clinical_db()
        
        vital_list = None
        if vital_names:
            vital_list = [name.strip() for name in vital_names.split(',')]
        
        start_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        end_dt = None
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        df = clinical_db.get_vitals_timeseries(
            patient_id=patient_id,
            vital_names=vital_list,
            start_date=start_dt,
            end_date=end_dt
        )
        
        if df.empty:
            return {
                'patient_id': patient_id,
                'vitals': [],
                'count': 0
            }
        
        vitals = []
        for _, row in df.iterrows():
            vitals.append({
                'timestamp': row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                'vital_name': row['vital_name'],
                'value': float(row['value']) if pd.notna(row['value']) else None,
                'unit': row.get('unit'),
                'validated': bool(row.get('validated', False))
            })
        
        return {
            'patient_id': patient_id,
            'vitals': vitals,
            'count': len(vitals),
            'date_range': {
                'earliest': df['timestamp'].min().isoformat() if not df.empty else None,
                'latest': df['timestamp'].max().isoformat() if not df.empty else None
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving vitals: {str(e)}"
        )


@router.get("/patient/{patient_id}/summary")
async def get_patient_summary(patient_id: str):
    """Get comprehensive patient summary with data counts."""
    try:
        clinical_db = get_clinical_db()
        summary = clinical_db.get_patient_summary(patient_id)
        
        if not summary.get('exists'):
            raise HTTPException(
                status_code=404,
                detail=f"Patient {patient_id} not found"
            )
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving patient summary: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if temporal data service is available."""
    try:
        parser = get_temporal_parser()
        db = get_clinical_db()
        return {
            "status": "healthy",
            "temporal_parser_available": True,
            "clinical_database_available": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
