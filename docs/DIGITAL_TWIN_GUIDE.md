# Patient Digital Twin System - Implementation Guide

## Overview

The Patient Digital Twin system transforms the platform from a "personalized recommendation system" into a **true Patient Digital Twin** that learns and adapts to each individual patient over time.

## Key Features

### 1. Patient-Specific Calibration
- **Mechanistic Model Calibration**: Calibrates cardiovascular model parameters (resistance R, compliance C) to individual patient data
- **ML Feature Calibration**: Adjusts ML model features based on patient-specific distributions
- **Automatic Re-calibration**: Updates parameters as more patient data becomes available

### 2. Outcome-Based Learning
- **Prediction Tracking**: Stores all predictions made for each patient
- **Outcome Comparison**: Compares predicted vs observed outcomes
- **Parameter Updates**: Automatically adjusts patient-specific parameters when predictions don't match reality
- **Continuous Improvement**: Gets better at predicting for that specific patient over time

### 3. Mechanistic Model Integration
- **Windkessel Model**: Uses cardiovascular physiology models with patient-specific parameters
- **Combined Predictions**: Fuses ML predictions with mechanistic model insights
- **Physiological Interpretability**: Provides explainable predictions based on cardiac physiology

### 4. Patient History Database
- **Time-Series Storage**: Stores patient vitals, labs, and medications over time
- **Prediction History**: Tracks all predictions and their outcomes
- **Calibration History**: Maintains history of parameter calibrations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Patient Digital Twin System                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │  Base ML Model   │      │  Patient Database│         │
│  │ (Population)     │      │  (SQLite)        │         │
│  └────────┬─────────┘      └────────┬─────────┘         │
│           │                          │                   │
│           └──────────┬───────────────┘                   │
│                      │                                   │
│           ┌──────────▼──────────┐                       │
│           │ Patient Calibrator  │                       │
│           │  - Calibrate R, C   │                       │
│           │  - Update from      │                       │
│           │    outcomes         │                       │
│           └──────────┬──────────┘                       │
│                      │                                   │
│           ┌──────────▼──────────┐                       │
│           │ Mechanistic Model   │                       │
│           │ (Windkessel)        │                       │
│           │  - Patient-specific │                       │
│           │    parameters       │                       │
│           └──────────┬──────────┘                       │
│                      │                                   │
│           ┌──────────▼──────────┐                       │
│           │ Digital Twin        │                       │
│           │ Recommender         │                       │
│           │  - Combines ML +    │                       │
│           │    Mechanistic      │                       │
│           │  - Patient-specific │                       │
│           │    predictions      │                       │
│           └─────────────────────┘                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## How It Works

### Step 1: Patient Initialization
When a new patient is added:
1. Patient information is stored in the database
2. If enough history exists (≥3 data points), mechanistic parameters are calibrated
3. Patient-specific model is initialized

### Step 2: Getting Recommendations
When requesting recommendations:
1. Base ML model (trained on population) provides initial recommendations
2. Patient-specific calibrated parameters are retrieved
3. Mechanistic model uses calibrated parameters to compute physiological features
4. ML and mechanistic predictions are combined
5. Final personalized recommendations are returned

### Step 3: Outcome Learning
When outcomes are observed:
1. Observed outcomes are stored in the database
2. Previous predictions are retrieved
3. Prediction errors are computed
4. Patient-specific parameters are updated based on errors
5. Future predictions become more accurate for this patient

## API Endpoints

### Initialize Patient
```http
POST /digital-twin/initialize
{
  "patient_id": "patient_001",
  "patient_info": {
    "age": 65,
    "sex": "M",
    "ejection_fraction": 0.35,
    ...
  }
}
```

### Get Digital Twin Recommendations
```http
POST /digital-twin/recommendations
{
  "patient_id": "patient_001",
  "patient_info": {...},
  "current_medications": ["ace_inhibitor"],
  "time_horizon_days": 90,
  "use_mechanistic": true
}
```

### Update from Outcome
```http
POST /digital-twin/update-outcome
{
  "patient_id": "patient_001",
  "outcome_type": "treatment_response",
  "observed_outcome": {
    "ejection_fraction": 0.40,
    "systolic_bp": 130
  }
}
```

### Get Digital Twin Status
```http
GET /digital-twin/status/{patient_id}
```

### Add Patient History
```http
POST /digital-twin/history?patient_id={patient_id}
{
  "vitals": {"systolic_bp": 140, "heart_rate": 85},
  "labs": {"ejection_fraction": 0.35},
  "medications": ["beta_blocker"]
}
```

## Usage Example

```python
from pdt.models.treatment.digital_twin_recommender import DigitalTwinRecommender
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender

# Load base model
base_recommender = PersonalizedMedicationRecommender()
base_recommender.load("models/personalized_medication_recommender.pkl")

# Initialize digital twin
digital_twin = DigitalTwinRecommender(base_recommender=base_recommender)

# Initialize patient
patient_id = "patient_001"
patient_info = {
    'age': 65,
    'ejection_fraction': 0.35,
    'systolic_bp': 140,
    ...
}

digital_twin.initialize_patient(patient_id, patient_info)

# Get recommendations
recommendations = digital_twin.get_recommendations(
    patient_id=patient_id,
    patient_info=patient_info,
    use_mechanistic=True
)

# After treatment, update with outcomes
observed_outcome = {
    'ejection_fraction': 0.40,
    'systolic_bp': 130
}

digital_twin.update_from_outcome(
    patient_id=patient_id,
    observed_outcome=observed_outcome
)
```

## Differences from Previous System

### Before (Personalized Recommendations)
- ✅ Uses patient features to get recommendations from general model
- ❌ No patient-specific model calibration
- ❌ No learning from individual outcomes
- ❌ No mechanistic model integration
- ❌ Same model for all patients

### After (Patient Digital Twin)
- ✅ Patient-specific parameter calibration
- ✅ Learns from individual patient outcomes
- ✅ Mechanistic models with patient-specific parameters
- ✅ Continuous improvement per patient
- ✅ Each patient has their own "digital twin"

## Benefits

1. **True Personalization**: Each patient gets a model calibrated to their specific physiology
2. **Continuous Learning**: The digital twin improves as more data is collected
3. **Better Predictions**: Patient-specific calibration leads to more accurate predictions
4. **Interpretability**: Mechanistic models provide physiological explanations
5. **Adaptive**: Automatically adjusts when predictions don't match reality

## Files Created

- `pdt/data/patient_database.py` - Patient database and history management
- `pdt/models/treatment/patient_calibration.py` - Patient-specific calibration logic
- `pdt/models/treatment/digital_twin_recommender.py` - Main digital twin recommender
- `pdt/api/endpoints/digital_twin.py` - API endpoints for digital twin
- `scripts/demo_digital_twin.py` - Demo script showing the system

## Next Steps

1. **Run the demo**: `python scripts/demo_digital_twin.py`
2. **Test API endpoints**: Use the FastAPI docs at `/docs`
3. **Integrate with frontend**: Update UI to use digital twin endpoints
4. **Collect outcomes**: Implement outcome tracking in clinical workflow
5. **Monitor performance**: Track prediction accuracy improvements over time

## Database Schema

The system uses SQLite with the following tables:
- `patients` - Patient information
- `patient_history` - Time-series patient data
- `predictions` - Model predictions
- `outcomes` - Observed outcomes
- `calibrated_parameters` - Patient-specific parameters

Database location: `data/patients.db`

