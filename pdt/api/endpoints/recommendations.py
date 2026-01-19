"""
API endpoints for medication recommendations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Load model (lazy loading)
_recommender = None


def get_recommender() -> PersonalizedMedicationRecommender:
    """Get or load the recommender model."""
    global _recommender
    if _recommender is None:
        model_path = Path("models/personalized_medication_recommender.pkl")
        if not model_path.exists():
            raise HTTPException(
                status_code=503,
                detail="Model not found. Please train the model first."
            )
        _recommender = PersonalizedMedicationRecommender()
        _recommender.load(str(model_path))
    return _recommender


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
    blood_pressure: Optional[str] = None  # "120/80" format
    
    # Labs
    ejection_fraction: Optional[float] = Field(None, ge=0.0, le=1.0, description="Ejection fraction (0-1)")
    creatinine: Optional[float] = None
    sodium: Optional[float] = None
    cholesterol: Optional[float] = None
    
    # Comorbidities
    diabetes: Optional[bool] = None
    high_blood_pressure: Optional[bool] = None
    hypertension: Optional[bool] = None
    high_cholesterol: Optional[bool] = None
    anaemia: Optional[bool] = None
    smoking: Optional[bool] = None
    
    # Additional fields
    class Config:
        extra = "allow"  # Allow additional fields


class MedicationRecommendationRequest(BaseModel):
    """Request for medication recommendations."""
    patient_info: PatientInfo
    current_medications: Optional[List[str]] = None
    time_horizon_days: int = Field(90, ge=1, le=365, description="Prediction time horizon in days")


class TreatmentScenario(BaseModel):
    """Treatment scenario for comparison."""
    medications: List[str]
    dosages: Optional[Dict[str, float]] = None


class TreatmentComparisonRequest(BaseModel):
    """Request for treatment scenario comparison."""
    patient_info: PatientInfo
    scenarios: List[TreatmentScenario]


@router.post("/medications", response_model=Dict[str, Any])
async def get_medication_recommendations(request: MedicationRecommendationRequest):
    """
    Get personalized medication recommendations for a patient.
    
    Returns:
        - recommendations: List of recommended medications with scores
        - optimal_combination: Best medication combination
        - baseline_prediction: Predicted outcomes without new medications
        - summary: Summary of recommendations
    """
    try:
        recommender = get_recommender()
        
        # Validate model is trained
        if not recommender.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model is not trained. Please train the model first before requesting recommendations."
            )
        
        # Convert patient info to dict
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        # Validate minimum required data
        if not patient_dict.get('age') or patient_dict.get('age') is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: age. Please provide patient age for accurate recommendations."
            )
        
        if not patient_dict.get('ejection_fraction') or patient_dict.get('ejection_fraction') is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: ejection_fraction. Please provide ejection fraction for accurate recommendations."
            )
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            patient_info=patient_dict,
            current_medications=request.current_medications,
            time_horizon_days=request.time_horizon_days
        )
        
        return recommendations
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Convert ValueError to HTTP 400 (Bad Request)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Other errors become 500
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/compare-scenarios", response_model=List[Dict[str, Any]])
async def compare_treatment_scenarios(request: TreatmentComparisonRequest):
    """
    Compare different treatment scenarios.
    
    Returns:
        List of scenario comparisons sorted by expected benefit.
    """
    try:
        recommender = get_recommender()
        
        # Validate model is trained
        if not recommender.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model is not trained. Please train the model first before comparing scenarios."
            )
        
        # Validate scenarios are provided
        if not request.scenarios or len(request.scenarios) == 0:
            raise HTTPException(
                status_code=400,
                detail="No scenarios provided. Please provide at least one treatment scenario to compare."
            )
        
        # Validate each scenario has medications
        for i, scenario in enumerate(request.scenarios):
            if not scenario.medications or len(scenario.medications) == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Scenario {i+1} has no medications. Please add medications to each scenario."
                )
        
        # Convert patient info to dict
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        # Validate minimum required patient data
        if not patient_dict.get('age') or patient_dict.get('age') is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: age. Please provide patient age for accurate comparison."
            )
        
        # Convert scenarios
        scenarios = []
        for scenario in request.scenarios:
            scenarios.append({
                'medications': scenario.medications,
                'dosages': scenario.dosages or {}
            })
        
        # Compare scenarios
        comparisons = recommender.compare_treatment_scenarios(
            patient_info=patient_dict,
            scenarios=scenarios
        )
        
        if not comparisons or len(comparisons) == 0:
            raise HTTPException(
                status_code=500,
                detail="No comparison results generated. This may indicate an issue with the model or input data."
            )
        
        return comparisons
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Convert ValueError to HTTP 400 (Bad Request)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Other errors become 500
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if recommendation service is available."""
    try:
        recommender = get_recommender()
        return {
            "status": "healthy",
            "model_loaded": recommender.is_trained
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }



