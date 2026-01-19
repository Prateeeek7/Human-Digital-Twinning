"""
API endpoints for medication database and combination predictions.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdt.data.medication_database import MedicationDatabase
from pdt.models.treatment.combination_success_predictor import CombinationSuccessPredictor
from pdt.models.treatment.enhanced_recommender import EnhancedMedicationRecommender
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

router = APIRouter(prefix="/medications", tags=["medications"])

# Initialize components (lazy loading)
_medication_db = None
_combination_predictor = None
_enhanced_recommender = None


def get_medication_db() -> MedicationDatabase:
    """Get or initialize medication database."""
    global _medication_db
    if _medication_db is None:
        _medication_db = MedicationDatabase()
    return _medication_db


def get_combination_predictor() -> CombinationSuccessPredictor:
    """Get or initialize combination predictor."""
    global _combination_predictor
    if _combination_predictor is None:
        _combination_predictor = CombinationSuccessPredictor(get_medication_db())
    return _combination_predictor


def get_enhanced_recommender() -> EnhancedMedicationRecommender:
    """Get or initialize enhanced recommender."""
    global _enhanced_recommender
    if _enhanced_recommender is None:
        # Try to load base recommender
        base_recommender = None
        model_path = Path("models/personalized_medication_recommender.pkl")
        if model_path.exists():
            base_recommender = PersonalizedMedicationRecommender()
            base_recommender.load(str(model_path))
        
        _enhanced_recommender = EnhancedMedicationRecommender(
            base_recommender=base_recommender,
            medication_db=get_medication_db(),
            combination_predictor=get_combination_predictor()
        )
    return _enhanced_recommender


class PatientInfo(BaseModel):
    """Patient information."""
    age: Optional[float] = None
    sex: Optional[str] = None
    ejection_fraction: Optional[float] = None
    systolic_bp: Optional[float] = None
    heart_rate: Optional[float] = None
    creatinine: Optional[float] = None
    diabetes: Optional[bool] = None
    high_blood_pressure: Optional[bool] = None
    weight: Optional[float] = None


class CombinationRequest(BaseModel):
    """Request for combination success prediction."""
    patient_info: PatientInfo
    medications: List[str] = Field(..., description="List of medication names")
    dosages: Optional[Dict[str, float]] = Field(None, description="Optional dosages (normalized 0-1)")


class CompareCombinationsRequest(BaseModel):
    """Request for comparing multiple combinations."""
    patient_info: PatientInfo
    combinations: List[Dict[str, Any]] = Field(..., description="List of combinations with medications and dosages")


@router.get("/search")
async def search_medications(
    query: str = Query(..., description="Search query (drug name)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """Search medications by name."""
    try:
        db = get_medication_db()
        results = db.search_medications(query, limit=limit)
        return {
            'query': query,
            'count': len(results),
            'medications': results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching medications: {str(e)}")


@router.get("/category/{category}")
async def get_medications_by_category(category: str):
    """Get medications by category."""
    try:
        db = get_medication_db()
        medications = db.get_medications_by_category(category)
        return {
            'category': category,
            'count': len(medications),
            'medications': medications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting medications: {str(e)}")


@router.get("/{medication_name}")
async def get_medication(medication_name: str):
    """Get medication details by name."""
    try:
        db = get_medication_db()
        medication = db.get_medication(name=medication_name)
        if not medication:
            raise HTTPException(status_code=404, detail=f"Medication '{medication_name}' not found")
        return medication
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting medication: {str(e)}")


@router.post("/predict-combination")
async def predict_combination_success(request: CombinationRequest):
    """
    Predict success rate for a medication combination.
    
    Returns:
        - success_rate: 0-1 probability of success
        - expected_outcomes: Predicted outcomes
        - risk_factors: Identified risk factors
        - interactions: Drug interactions
    """
    try:
        predictor = get_combination_predictor()
        
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        prediction = predictor.predict_success_rate(
            patient_params=patient_dict,
            medications=request.medications,
            dosages=request.dosages
        )
        
        return prediction
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting combination success: {str(e)}")


@router.post("/compare-combinations")
async def compare_combinations(request: CompareCombinationsRequest):
    """
    Compare multiple medication combinations.
    
    Returns:
        List of combinations sorted by success rate
    """
    try:
        predictor = get_combination_predictor()
        
        patient_dict = request.patient_info.dict(exclude_none=True)
        
        comparisons = predictor.compare_combinations(
            patient_params=patient_dict,
            combinations=request.combinations
        )
        
        return {
            'patient_info': patient_dict,
            'combinations_compared': len(comparisons),
            'comparisons': comparisons
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing combinations: {str(e)}")


@router.post("/recommendations/enhanced")
async def get_enhanced_recommendations(
    patient_info: PatientInfo,
    current_medications: Optional[List[str]] = None,
    time_horizon_days: int = 90
):
    """
    Get enhanced medication recommendations with specific drugs and dosages.
    
    Returns:
        - specific_recommendations: List of specific drugs with dosages
        - optimal_combinations: Best combinations with success rates
        - summary: Summary of recommendations
    """
    try:
        recommender = get_enhanced_recommender()
        
        patient_dict = patient_info.dict(exclude_none=True)
        
        recommendations = recommender.get_recommendations(
            patient_info=patient_dict,
            current_medications=current_medications,
            time_horizon_days=time_horizon_days
        )
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting enhanced recommendations: {str(e)}")


@router.post("/load-hf-medications")
async def load_heart_failure_medications():
    """
    Load common heart failure medications into database.
    This will query RxNorm API and may take a few minutes.
    """
    try:
        db = get_medication_db()
        count = db.load_heart_failure_medications()
        return {
            'status': 'success',
            'medications_loaded': count,
            'message': f'Loaded {count} heart failure medications'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading medications: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if medication service is available."""
    try:
        db = get_medication_db()
        predictor = get_combination_predictor()
        return {
            "status": "healthy",
            "medication_database_available": True,
            "combination_predictor_available": True,
            "predictor_trained": predictor.is_trained
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
