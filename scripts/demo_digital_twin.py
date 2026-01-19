"""
Demo script for Patient Digital Twin system.
Shows how the digital twin learns and adapts to individual patients.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdt.models.treatment.digital_twin_recommender import DigitalTwinRecommender
from pdt.models.treatment.personalized_recommender import PersonalizedMedicationRecommender
import json


def demo_digital_twin():
    """Demonstrate the Patient Digital Twin system."""
    print("="*70)
    print("Patient Digital Twin System - Demo")
    print("="*70)
    
    # Load base recommender
    print("\n1. Loading base ML model (trained on population data)...")
    model_path = Path("models/personalized_medication_recommender.pkl")
    if not model_path.exists():
        print("✗ Model not found. Please train first with: python scripts/train_medication_recommender.py")
        return
    
    base_recommender = PersonalizedMedicationRecommender()
    base_recommender.load(str(model_path))
    print("✓ Base model loaded")
    
    # Initialize digital twin recommender
    print("\n2. Initializing Digital Twin Recommender...")
    digital_twin = DigitalTwinRecommender(base_recommender=base_recommender)
    print("✓ Digital Twin system initialized")
    
    # Initialize a patient
    print("\n" + "="*70)
    print("3. Initializing Patient in Digital Twin System")
    print("="*70)
    
    patient_id = "demo_patient_001"
    patient_info = {
        'age': 65,
        'sex': 'M',
        'ejection_fraction': 0.35,  # HFrEF
        'systolic_bp': 140,
        'heart_rate': 85,
        'creatinine': 1.2,
        'diabetes': True,
        'high_blood_pressure': True
    }
    
    print(f"\nPatient ID: {patient_id}")
    print(f"Patient Info: {json.dumps(patient_info, indent=2)}")
    
    init_result = digital_twin.initialize_patient(patient_id, patient_info)
    print(f"\n✓ Patient initialized")
    print(f"  Calibrated: {init_result['calibrated']}")
    print(f"  Calibration Quality: {init_result['calibration_results']['windkessel'].get('calibration_quality', 'N/A')}")
    
    # Add some history to enable calibration
    print("\n4. Adding patient history for calibration...")
    digital_twin.patient_db.add_history_entry(
        patient_id,
        vitals={'systolic_bp': 140, 'heart_rate': 85},
        labs={'ejection_fraction': 0.35, 'creatinine': 1.2}
    )
    digital_twin.patient_db.add_history_entry(
        patient_id,
        vitals={'systolic_bp': 138, 'heart_rate': 82},
        labs={'ejection_fraction': 0.36, 'creatinine': 1.1}
    )
    digital_twin.patient_db.add_history_entry(
        patient_id,
        vitals={'systolic_bp': 135, 'heart_rate': 80},
        labs={'ejection_fraction': 0.37, 'creatinine': 1.0}
    )
    print("✓ Added 3 history entries")
    
    # Re-initialize to trigger calibration
    init_result = digital_twin.initialize_patient(patient_id, patient_info)
    print(f"✓ Re-calibrated with history")
    print(f"  Calibration Quality: {init_result['calibration_results']['windkessel'].get('calibration_quality', 'N/A')}")
    
    # Get recommendations using digital twin
    print("\n" + "="*70)
    print("5. Getting Personalized Recommendations (Digital Twin)")
    print("="*70)
    
    recommendations = digital_twin.get_recommendations(
        patient_id=patient_id,
        patient_info=patient_info,
        current_medications=None,
        time_horizon_days=90,
        use_mechanistic=True
    )
    
    print(f"\n✓ Recommendations generated")
    print(f"  Digital Twin Calibrated: {recommendations['digital_twin']['calibrated']}")
    print(f"  Calibration Quality: {recommendations['digital_twin']['calibration_quality']}")
    print(f"  Mechanistic Adjustments: {recommendations['digital_twin']['mechanistic_adjustments_applied']}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(recommendations['recommendations'][:3], 1):
        print(f"\n  {i}. {rec['medication']}")
        print(f"     Score: {rec['recommendation_score']:.3f}")
        if 'mechanistic_features' in rec:
            print(f"     Cardiac Output: {rec['mechanistic_features']['cardiac_output']:.2f} L/min")
            print(f"     Systemic Resistance: {rec['mechanistic_features']['systemic_resistance']:.2f}")
    
    # Simulate outcome and update digital twin
    print("\n" + "="*70)
    print("6. Simulating Outcome and Updating Digital Twin")
    print("="*70)
    
    # Simulate that patient was given beta_blocker and we observed outcomes
    observed_outcome = {
        'ejection_fraction': 0.40,  # Improved from 0.35
        'systolic_bp': 130,  # Improved from 140
        'heart_rate': 75  # Improved from 85
    }
    
    print(f"\nObserved Outcome (after treatment):")
    print(json.dumps(observed_outcome, indent=2))
    
    update_result = digital_twin.update_from_outcome(
        patient_id=patient_id,
        observed_outcome=observed_outcome,
        outcome_type='treatment_response'
    )
    
    print(f"\n✓ Digital Twin updated")
    print(f"  Updated: {update_result['updated']}")
    if update_result['updated']:
        print(f"  Previous R: {update_result['previous_params'].get('R', 'N/A'):.3f}")
        print(f"  Updated R: {update_result['updated_params'].get('R', 'N/A'):.3f}")
        print(f"  Previous C: {update_result['previous_params'].get('C', 'N/A'):.3f}")
        print(f"  Updated C: {update_result['updated_params'].get('C', 'N/A'):.3f}")
        if update_result.get('prediction_errors'):
            print(f"  Prediction Errors: {update_result['prediction_errors']}")
    
    # Get digital twin status
    print("\n" + "="*70)
    print("7. Digital Twin Status")
    print("="*70)
    
    status = digital_twin.get_patient_digital_twin_status(patient_id)
    print(f"\nPatient ID: {status['patient_id']}")
    print(f"History Points: {status['n_history_points']}")
    print(f"Calibrated: {status['calibrated']}")
    print(f"Calibration Quality: {status['calibration_quality']}")
    print(f"Number of Predictions: {status['n_predictions']}")
    if status.get('prediction_accuracy'):
        print(f"Prediction Accuracy: {status['prediction_accuracy']}")
    
    print("\n" + "="*70)
    print("✓ Digital Twin Demo Complete")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  1. Patient-specific parameter calibration")
    print("  2. Mechanistic model integration")
    print("  3. Outcome-based learning and adaptation")
    print("  4. Continuous improvement from observed outcomes")


if __name__ == "__main__":
    demo_digital_twin()

