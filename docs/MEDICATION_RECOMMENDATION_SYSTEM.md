# Personalized Medication Recommendation System

## Overview

The Personalized Medication Recommendation System is a complete solution for recommending optimal medications for heart failure patients based on their individual characteristics, predicting treatment effects, and comparing different treatment scenarios.

## System Architecture

### Phase 1: Medication Recommendation Engine
- **MedicationRecommender**: Learns from patient characteristics to recommend appropriate medications
- **DrugInteractionChecker**: Identifies potential drug-drug interactions
- Trained on 253,680+ patients from combined datasets

### Phase 2: Treatment Effect Prediction
- **TreatmentEffectPredictor**: Predicts patient response to specific medications
- Forecasts trajectories for:
  - Ejection Fraction (EF)
  - Mortality Risk
  - Readmission Risk
  - Blood Pressure
  - Heart Rate
- Generates time-series trajectories over 90-day horizons

### Phase 3: Treatment Optimization
- **DosageOptimizer**: Finds optimal medication dosages
- Optimizes medication combinations
- Considers multiple objectives (maximize benefit, minimize risk, balance)

### Phase 4: API and Interface
- RESTful API endpoints for recommendations
- Treatment scenario comparison
- Real-time predictions

## Features

### 1. Personalized Recommendations
- Analyzes patient demographics, vitals, labs, and comorbidities
- Recommends medications based on clinical guidelines and learned patterns
- Provides recommendation scores and expected benefits

### 2. Drug Interaction Checking
- Checks for severe, moderate, and mild interactions
- Warns about contraindications
- Ensures safe medication combinations

### 3. Treatment Effect Prediction
- Predicts how patient will respond to medications
- Forecasts changes in:
  - Ejection Fraction
  - Blood Pressure
  - Heart Rate
  - Mortality Risk
  - Readmission Risk
- Generates longitudinal trajectories

### 4. Dosage Optimization
- Finds optimal dosages for individual medications
- Optimizes medication combinations
- Considers patient-specific factors

### 5. Treatment Comparison
- Compare multiple treatment scenarios
- Rank by expected benefit
- Identify best combination

## Usage

### Training the System

```bash
python scripts/train_medication_recommender.py
```

This will:
1. Load the combined dataset (253,680+ patients)
2. Train medication recommendation models
3. Train treatment effect prediction models
4. Save the complete system to `models/personalized_medication_recommender.pkl`

### Using the System (Python)

```python
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

# Load model
recommender = PersonalizedMedicationRecommender()
recommender.load('models/personalized_medication_recommender.pkl')

# Patient information
patient = {
    'age': 65,
    'sex': 'M',
    'ejection_fraction': 0.35,  # HFrEF
    'systolic_bp': 140,
    'heart_rate': 85,
    'creatinine': 1.2,
    'diabetes': True,
    'high_blood_pressure': True
}

# Get recommendations
recommendations = recommender.get_recommendations(
    patient_info=patient,
    current_medications=[],
    time_horizon_days=90
)

# Access results
print(f"Top recommendation: {recommendations['summary']['top_recommendation']}")
print(f"Optimal combination: {recommendations['optimal_combination']['medications']}")
```

### Using the API

#### Start the API server:

```bash
uvicorn pdt.api.main:app --reload --port 8000
```

#### Get Medication Recommendations:

```bash
curl -X POST "http://localhost:8000/recommendations/medications" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 65,
      "sex": "M",
      "ejection_fraction": 0.35,
      "systolic_bp": 140,
      "diabetes": true,
      "high_blood_pressure": true
    },
    "current_medications": [],
    "time_horizon_days": 90
  }'
```

#### Compare Treatment Scenarios:

```bash
curl -X POST "http://localhost:8000/recommendations/compare-scenarios" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 65,
      "ejection_fraction": 0.35
    },
    "scenarios": [
      {
        "medications": ["ace_inhibitor", "beta_blocker"],
        "dosages": {"ace_inhibitor": 1.0, "beta_blocker": 1.0}
      },
      {
        "medications": ["arni", "beta_blocker"],
        "dosages": {"arni": 1.0, "beta_blocker": 1.0}
      }
    ]
  }'
```

### Demo Script

Run the demo to see examples:

```bash
python scripts/demo_recommendations.py
```

## Supported Medications

The system currently supports recommendations for:

1. **ACE Inhibitors** (e.g., lisinopril, enalapril)
2. **ARB** (Angiotensin Receptor Blockers)
3. **ARNI** (Angiotensin Receptor-Neprilysin Inhibitor)
4. **Beta Blockers** (e.g., metoprolol, carvedilol)
5. **Diuretics** (e.g., furosemide)
6. **Aldosterone Antagonists** (e.g., spironolactone)
7. **Digoxin**
8. **Anticoagulants**

## Input Patient Information

The system accepts the following patient information:

### Demographics
- `age`: Patient age
- `sex` or `gender`: M/F

### Vitals
- `heart_rate`: Heart rate (bpm)
- `systolic_bp`: Systolic blood pressure (mmHg)
- `diastolic_bp`: Diastolic blood pressure (mmHg)
- `blood_pressure`: "120/80" format

### Labs
- `ejection_fraction`: Ejection fraction (0-1)
- `creatinine`: Serum creatinine
- `sodium`: Serum sodium
- `cholesterol`: Total cholesterol

### Comorbidities
- `diabetes`: Boolean
- `high_blood_pressure` or `hypertension`: Boolean
- `high_cholesterol`: Boolean
- `anaemia`: Boolean
- `smoking`: Boolean

## Output Format

### Recommendations Response

```json
{
  "patient_info": {...},
  "current_medications": [],
  "baseline_prediction": {
    "predicted_effects": {...},
    "trajectories": {...}
  },
  "recommendations": [
    {
      "medication": "beta_blocker",
      "recommendation_score": 0.95,
      "expected_benefit": 0.90,
      "is_safe": true,
      "interactions": [],
      "predicted_effect": {
        "predicted_effects": {
          "ejection_fraction": 0.38,
          "mortality_risk": 0.10
        },
        "trajectories": {
          "time_days": [0, 7, 14, ...],
          "ejection_fraction": [0.35, 0.36, 0.37, ...],
          "mortality_risk": [0.15, 0.14, 0.13, ...]
        }
      },
      "optimal_dose": 1.0
    }
  ],
  "optimal_combination": {
    "medications": ["beta_blocker", "ace_inhibitor"],
    "total_benefit": 1.85
  },
  "summary": {
    "top_recommendation": {...},
    "optimal_combination": {...},
    "warnings": []
  }
}
```

## Model Performance

- **Training Data**: 253,680 patients
- **Medication Recommendation Models**: 8 models (one per medication class)
- **Treatment Effect Models**: 3 models (EF, mortality, readmission)
- **Cross-validation**: Integrated into training pipeline

## Files Structure

```
pdt/models/treatment/
├── medication_recommender.py      # Core recommendation engine
├── drug_interaction_checker.py    # Interaction checking
├── treatment_effect_predictor.py # Effect prediction
├── dosage_optimizer.py            # Dosage optimization
└── personalized_recommender.py    # Complete system

pdt/api/endpoints/
└── recommendations.py              # API endpoints

scripts/
├── train_medication_recommender.py # Training script
├── demo_recommendations.py         # Demo script
└── test_recommendation_api.py      # API testing
```

## Next Steps

1. **Fine-tuning**: Improve models with more data and hyperparameter tuning
2. **Additional Medications**: Add more medication classes
3. **Clinical Validation**: Validate recommendations with clinical experts
4. **Integration**: Integrate with EHR systems
5. **Monitoring**: Add monitoring and logging for production use

## Notes

- The system is trained on combined datasets (UCI, Kaggle, MIMIC-IV ED Demo)
- Recommendations are based on clinical guidelines and learned patterns
- Drug interactions are checked based on known interactions
- Treatment effects are predicted using gradient boosting models
- All predictions include uncertainty estimates

## References

- Clinical guidelines for heart failure management
- Drug interaction databases
- Treatment effect literature
- Combined dataset from multiple sources



