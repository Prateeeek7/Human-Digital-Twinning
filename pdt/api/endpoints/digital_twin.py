"""
API endpoints for Patient Digital Twin functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdt.models.treatment.digital_twin_recommender import DigitalTwinRecommender
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

router = APIRouter(prefix="/digital-twin", tags=["digital-twin"])

# Load models (lazy loading)
_digital_twin_recommender = None
_base_recommender = None


def get_digital_twin_recommender() -> DigitalTwinRecommender:
    """Get or load the digital twin recommender."""
    global _digital_twin_recommender, _base_recommender
    
    if _digital_twin_recommender is None:
        # Load base recommender
        if _base_recommender is None:
            model_path = Path("models/personalized_medication_recommender.pkl")
            if not model_path.exists():
                raise HTTPException(
                    status_code=503,
                    detail="Base model not found. Please train the model first."
                )
            _base_recommender = PersonalizedMedicationRecommender()
            _base_recommender.load(str(model_path))
        
        # Initialize digital twin recommender
        _digital_twin_recommender = DigitalTwinRecommender(base_recommender=_base_recommender)
    
    return _digital_twin_recommender


# Request/Response models
class PatientInfo(BaseModel):
    """Patient information."""
    age: Optional[float] = None
    sex: Optional[str] = None
    gender: Optional[str] = None
    
    # Vitals
    heart_rate: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    blood_pressure: Optional[str] = None
    
    # Labs
    ejection_fraction: Optional[float] = Field(None, ge=0.0, le=1.0)
    creatinine: Optional[float] = None
    sodium: Optional[float] = None
    cholesterol: Optional[float] = None
    end_diastolic_volume: Optional[float] = None
    
    # Comorbidities
    diabetes: Optional[bool] = None
    high_blood_pressure: Optional[bool] = None
    hypertension: Optional[bool] = None
    high_cholesterol: Optional[bool] = None
    anaemia: Optional[bool] = None
    smoking: Optional[bool] = None
    
    class Config:
        extra = "allow"


class InitializePatientRequest(BaseModel):
    """Request to initialize a patient in the digital twin system."""
    patient_id: str
    patient_info: PatientInfo


class DigitalTwinRecommendationRequest(BaseModel):
    """Request for digital twin recommendations."""
    patient_id: str
    patient_info: PatientInfo
    current_medications: Optional[List[str]] = None
    time_horizon_days: int = Field(90, ge=1, le=365)
    use_mechanistic: bool = True


class OutcomeUpdateRequest(BaseModel):
    """Request to update digital twin with observed outcome."""
    patient_id: str
    outcome_type: str = "treatment_response"
    observed_outcome: Dict[str, Any]


@router.post("/initialize")
async def initialize_patient(request: InitializePatientRequest):
    """
    Initialize a new patient in the digital twin system.
    
    This calibrates patient-specific parameters and sets up the digital twin.
    """
    try:
        recommender = get_digital_twin_recommender()
        
        # Convert patient info to dict
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        # Initialize patient
        result = recommender.initialize_patient(
            patient_id=request.patient_id,
            patient_info=patient_dict
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing patient: {str(e)}")


@router.post("/recommendations")
async def get_digital_twin_recommendations(request: DigitalTwinRecommendationRequest):
    """
    Get personalized recommendations using the patient's digital twin.
    
    This uses:
    - Patient-specific calibrated mechanistic model parameters
    - ML models trained on population data
    - Combined predictions for personalized recommendations
    """
    try:
        recommender = get_digital_twin_recommender()
        
        # Convert patient info to dict
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            patient_id=request.patient_id,
            patient_info=patient_dict,
            current_medications=request.current_medications,
            time_horizon_days=request.time_horizon_days,
            use_mechanistic=request.use_mechanistic
        )
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/update-outcome")
async def update_digital_twin_from_outcome(request: OutcomeUpdateRequest):
    """
    Update the patient's digital twin based on observed outcome.
    
    This compares predicted vs observed outcomes and updates
    patient-specific parameters to improve future predictions.
    """
    try:
        recommender = get_digital_twin_recommender()
        
        # Update from outcome
        result = recommender.update_from_outcome(
            patient_id=request.patient_id,
            observed_outcome=request.observed_outcome,
            outcome_type=request.outcome_type
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating digital twin: {str(e)}")


@router.get("/status/{patient_id}")
async def get_digital_twin_status(patient_id: str):
    """
    Get the status of a patient's digital twin.
    
    Returns:
    - Calibration status
    - Prediction accuracy
    - Number of data points
    - Calibration quality
    """
    try:
        recommender = get_digital_twin_recommender()
        
        status = recommender.get_patient_digital_twin_status(patient_id)
        
        return status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/history")
async def add_patient_history_entry(
    patient_id: str,
    vitals: Optional[Dict[str, Any]] = None,
    labs: Optional[Dict[str, Any]] = None,
    medications: Optional[List[str]] = None
):
    """
    Add a history entry for a patient.
    
    This stores time-series data that can be used for:
    - Calibrating patient-specific parameters
    - Tracking patient progression
    - Improving predictions
    """
    try:
        recommender = get_digital_twin_recommender()
        
        recommender.patient_db.add_history_entry(
            patient_id=patient_id,
            vitals=vitals,
            labs=labs,
            medications=medications
        )
        
        # Re-calibrate if enough data points
        history = recommender.patient_db.get_patient_history(patient_id)
        if len(history) >= 3:
            # Re-calibrate
            calibrated_params = recommender.calibrator.calibrate_windkessel(history)
            recommender.patient_db.save_calibrated_parameters(
                patient_id,
                'windkessel',
                calibrated_params,
                'history_based_recalibration'
            )
        
        return {
            "success": True,
            "message": "History entry added",
            "n_history_points": len(history) + 1
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding history: {str(e)}")


@router.get("/history/{patient_id}")
async def get_patient_history(patient_id: str):
    """Get patient history."""
    try:
        recommender = get_digital_twin_recommender()
        
        history = recommender.patient_db.get_patient_history(patient_id)
        
        # Convert to list of dicts
        history_list = history.to_dict('records')
        
        return {
            "patient_id": patient_id,
            "n_entries": len(history_list),
            "history": history_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if digital twin service is available."""
    try:
        recommender = get_digital_twin_recommender()
        return {
            "status": "healthy",
            "base_model_loaded": recommender.base_recommender is not None and recommender.base_recommender.is_trained,
            "service": "digital_twin"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

