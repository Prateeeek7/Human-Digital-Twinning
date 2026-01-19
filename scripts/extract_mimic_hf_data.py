"""
Extract Heart Failure patients and their medications from MIMIC-IV.
"""

import pandas as pd
from pathlib import Path

def extract_heart_failure_cohort(mimic_path='data/raw/mimic'):
    """
    Extract heart failure patients from MIMIC-IV.
    
    Args:
        mimic_path: Path to MIMIC-IV data
    """
    mimic_path = Path(mimic_path)
    
    print("="*70)
    print("Extracting Heart Failure Cohort from MIMIC-IV")
    print("="*70)
    
    # Load diagnoses
    diagnoses_file = mimic_path / 'hosp' / 'diagnoses_icd.csv'
    if not diagnoses_file.exists():
        print(f"✗ File not found: {diagnoses_file}")
        print("  Make sure MIMIC-IV is downloaded to data/raw/mimic/")
        return None
    
    print(f"Loading diagnoses from {diagnoses_file}...")
    diagnoses = pd.read_csv(diagnoses_file)
    
    # Heart failure ICD-10 codes
    hf_codes = ['I50', 'I501', 'I509', 'I5020', 'I5021', 'I5022', 'I5023']
    
    # Filter for heart failure
    hf_patients = diagnoses[
        diagnoses['icd_code'].str.startswith(tuple(hf_codes), na=False)
    ]
    
    print(f"✓ Found {len(hf_patients)} heart failure diagnoses")
    print(f"  Unique patients: {hf_patients['subject_id'].nunique()}")
    
    # Get unique patient IDs
    hf_patient_ids = hf_patients['subject_id'].unique()
    
    return hf_patient_ids, hf_patients


def extract_medications(hf_patient_ids, mimic_path='data/raw/mimic'):
    """
    Extract medications for heart failure patients.
    
    Args:
        hf_patient_ids: Array of patient IDs
        mimic_path: Path to MIMIC-IV data
    """
    mimic_path = Path(mimic_path)
    
    print("\n" + "="*70)
    print("Extracting Medication Data")
    print("="*70)
    
    # Load prescriptions
    prescriptions_file = mimic_path / 'hosp' / 'prescriptions.csv'
    if not prescriptions_file.exists():
        print(f"✗ File not found: {prescriptions_file}")
        return None
    
    print(f"Loading prescriptions from {prescriptions_file}...")
    prescriptions = pd.read_csv(prescriptions_file)
    
    # Filter for heart failure patients
    hf_prescriptions = prescriptions[
        prescriptions['subject_id'].isin(hf_patient_ids)
    ]
    
    print(f"✓ Found {len(hf_prescriptions)} prescriptions for HF patients")
    
    # Common heart failure medications to highlight
    hf_meds = [
        'lisinopril', 'enalapril', 'captopril',  # ACE inhibitors
        'losartan', 'valsartan', 'candesartan',   # ARBs
        'sacubitril', 'entresto',                 # ARNI
        'metoprolol', 'carvedilol', 'bisoprolol', # Beta-blockers
        'furosemide', 'bumetanide',               # Diuretics
        'spironolactone', 'eplerenone',           # Aldosterone antagonists
        'digoxin', 'warfarin', 'aspirin'
    ]
    
    # Check for HF medications
    hf_med_prescriptions = hf_prescriptions[
        hf_prescriptions['drug'].str.lower().str.contains(
            '|'.join(hf_meds), na=False, case=False
        )
    ]
    
    print(f"✓ Found {len(hf_med_prescriptions)} HF-specific medication prescriptions")
    
    return hf_prescriptions, hf_med_prescriptions


def save_extracted_data(hf_patient_ids, hf_diagnoses, hf_prescriptions, 
                       hf_med_prescriptions, output_path='data/processed/mimic_hf'):
    """Save extracted data."""
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("Saving Extracted Data")
    print("="*70)
    
    # Save patient IDs
    pd.Series(hf_patient_ids).to_csv(
        output_path / 'hf_patient_ids.csv', 
        index=False, 
        header=['subject_id']
    )
    print(f"✓ Saved patient IDs: {output_path / 'hf_patient_ids.csv'}")
    
    # Save diagnoses
    hf_diagnoses.to_csv(
        output_path / 'hf_diagnoses.csv',
        index=False
    )
    print(f"✓ Saved diagnoses: {output_path / 'hf_diagnoses.csv'}")
    
    # Save all prescriptions
    hf_prescriptions.to_csv(
        output_path / 'hf_prescriptions.csv',
        index=False
    )
    print(f"✓ Saved prescriptions: {output_path / 'hf_prescriptions.csv'}")
    
    # Save HF-specific medications
    hf_med_prescriptions.to_csv(
        output_path / 'hf_medications.csv',
        index=False
    )
    print(f"✓ Saved HF medications: {output_path / 'hf_medications.csv'}")


def main():
    """Main extraction function."""
    # Extract heart failure cohort
    result = extract_heart_failure_cohort()
    if result is None:
        return
    
    hf_patient_ids, hf_diagnoses = result
    
    # Extract medications
    med_result = extract_medications(hf_patient_ids)
    if med_result is None:
        return
    
    hf_prescriptions, hf_med_prescriptions = med_result
    
    # Save extracted data
    save_extracted_data(
        hf_patient_ids,
        hf_diagnoses,
        hf_prescriptions,
        hf_med_prescriptions
    )
    
    print("\n" + "="*70)
    print("Extraction Complete!")
    print("="*70)
    print(f"\nExtracted data saved to: data/processed/mimic_hf/")
    print("\nYou can now use this data for training your Patient Digital Twin.")


if __name__ == "__main__":
    main()
