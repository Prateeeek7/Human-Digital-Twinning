# Quick Start Guide - Medication Recommendation System

## 1. Train the Model

```bash
python scripts/train_medication_recommender.py
```

This trains the complete medication recommendation system on your combined dataset.

## 2. Test with Demo

```bash
python scripts/demo_recommendations.py
```

This shows example recommendations for a sample patient.

## 3. Start the API Server

```bash
uvicorn pdt.api.main:app --reload --port 8000
```

## 4. Test the API

In another terminal:

```bash
python scripts/test_recommendation_api.py
```

Or use curl:

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

## Example Python Usage

```python
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib

# Load model
recommender = PersonalizedMedicationRecommender()
recommender.load('models/personalized_medication_recommender.pkl')

# Patient data
patient = {
    'age': 65,
    'sex': 'M',
    'ejection_fraction': 0.35,
    'systolic_bp': 140,
    'diabetes': True,
    'high_blood_pressure': True
}

# Get recommendations
result = recommender.get_recommendations(patient)

# Print top recommendation
print(f"Top: {result['summary']['top_recommendation']['medication']}")
print(f"Combination: {result['optimal_combination']['medications']}")
```

## What You Get

1. **Personalized Medication Recommendations** - Based on patient characteristics
2. **Treatment Effect Predictions** - How patient will respond
3. **Drug Interaction Checking** - Safety validation
4. **Dosage Optimization** - Optimal dosages
5. **Treatment Comparison** - Compare multiple scenarios

## Files Created

- `models/personalized_medication_recommender.pkl` - Trained model
- API endpoints at `/recommendations/*`
- Demo and test scripts

## Documentation

See `MEDICATION_RECOMMENDATION_SYSTEM.md` for complete documentation.
