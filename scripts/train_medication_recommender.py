"""
Train the complete medication recommendation system.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import joblib


def load_training_data():
    """Load combined dataset for training."""
    print("Loading training data...")
    df = pd.read_csv('data/processed/combined_dataset.csv')
    print(f"✓ Loaded {len(df):,} patients")
    return df


def train_recommendation_system():
    """Train the complete medication recommendation system."""
    print("="*70)
    print("Training Personalized Medication Recommendation System")
    print("="*70)
    
    # Load data
    df = load_training_data()
    
    # Initialize recommender
    recommender = PersonalizedMedicationRecommender()
    
    # Train
    recommender.train(df)
    
    # Save
    model_path = Path("models/personalized_medication_recommender.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    recommender.save(str(model_path))
    print(f"\n✓ Model saved to: {model_path}")
    
    # Test with sample patient
    print("\n" + "="*70)
    print("Testing Recommendation System")
    print("="*70)
    
    sample_patient = {
        'age': 65,
        'sex': 'M',
        'ejection_fraction': 0.35,  # HFrEF
        'systolic_bp': 140,
        'heart_rate': 85,
        'creatinine': 1.2,
        'diabetes': 1,
        'high_blood_pressure': 1
    }
    
    recommendations = recommender.get_recommendations(
        sample_patient,
        current_medications=None,
        time_horizon_days=90
    )
    
    print("\nSample Recommendations:")
    print(f"Top recommendation: {recommendations['summary']['top_recommendation']}")
    print(f"Optimal combination: {recommendations['optimal_combination']['medications']}")
    
    return recommender


if __name__ == "__main__":
    recommender = train_recommendation_system()
    print("\n✓ Training complete! System ready for recommendations.")



