"""
Demo script for medication recommendations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib
import json


def demo_recommendations():
    """Demonstrate medication recommendations."""
    print("="*70)
    print("Medication Recommendation System - Demo")
    print("="*70)
    
    # Load model
    print("\nLoading model...")
    model_path = Path("models/personalized_medication_recommender.pkl")
    if not model_path.exists():
        print("✗ Model not found. Please train first with: python scripts/train_medication_recommender.py")
        return
    
    recommender = PersonalizedMedicationRecommender()
    recommender.load(str(model_path))
    print("✓ Model loaded")
    
    # Example patient 1: HFrEF patient
    print("\n" + "="*70)
    print("Example 1: Heart Failure with Reduced Ejection Fraction (HFrEF)")
    print("="*70)
    
    patient1 = {
        'age': 65,
        'sex': 'M',
        'ejection_fraction': 0.35,  # Reduced EF
        'systolic_bp': 140,
        'heart_rate': 85,
        'creatinine': 1.2,
        'diabetes': True,
        'high_blood_pressure': True
    }
    
    print("\nPatient Information:")
    print(json.dumps(patient1, indent=2))
    
    recommendations1 = recommender.get_recommendations(
        patient1,
        current_medications=None,
        time_horizon_days=90
    )
    
    print("\n" + "-"*70)
    print("Recommendations:")
    print("-"*70)
    print(f"Top Recommendation: {recommendations1['summary']['top_recommendation']['medication']}")
    print(f"  Score: {recommendations1['summary']['top_recommendation']['recommendation_score']:.3f}")
    print(f"  Expected Benefit: {recommendations1['summary']['top_recommendation']['expected_benefit']:.3f}")
    
    print(f"\nOptimal Combination: {recommendations1['optimal_combination']['medications']}")
    print(f"  Total Benefit: {recommendations1['optimal_combination']['total_benefit']:.3f}")
    
    print("\nAll Recommendations:")
    for i, rec in enumerate(recommendations1['recommendations'][:5], 1):
        print(f"\n{i}. {rec['medication']}")
        print(f"   Recommendation Score: {rec['recommendation_score']:.3f}")
        print(f"   Expected Benefit: {rec.get('predicted_effect', {}).get('treatment_benefit', 0):.3f}")
        print(f"   Is Safe: {rec.get('is_safe', True)}")
        if rec.get('interactions'):
            print(f"   Interactions: {len(rec['interactions'])}")
    
    # Example 2: Compare treatment scenarios
    print("\n" + "="*70)
    print("Example 2: Treatment Scenario Comparison")
    print("="*70)
    
    scenarios = [
        {
            'medications': ['ace_inhibitor', 'beta_blocker'],
            'dosages': {'ace_inhibitor': 1.0, 'beta_blocker': 1.0}
        },
        {
            'medications': ['arni', 'beta_blocker'],
            'dosages': {'arni': 1.0, 'beta_blocker': 1.0}
        },
        {
            'medications': ['ace_inhibitor', 'beta_blocker', 'aldosterone_antagonist'],
            'dosages': {'ace_inhibitor': 1.0, 'beta_blocker': 1.0, 'aldosterone_antagonist': 1.0}
        }
    ]
    
    comparisons = recommender.compare_treatment_scenarios(patient1, scenarios)
    
    print("\nScenario Comparison (sorted by benefit):")
    for i, comp in enumerate(comparisons, 1):
        print(f"\nScenario {i}: {comp['medications']}")
        print(f"  Total Benefit: {comp['total_benefit']:.3f}")
        print(f"  Is Safe: {comp['is_safe']}")
        if comp['interactions']:
            print(f"  Interactions: {len(comp['interactions'])}")
            for interaction in comp['interactions'][:2]:
                print(f"    - {interaction['medication1']} + {interaction['medication2']}: {interaction['severity']}")
    
    print("\n" + "="*70)
    print("Demo Complete")
    print("="*70)


if __name__ == "__main__":
    demo_recommendations()



