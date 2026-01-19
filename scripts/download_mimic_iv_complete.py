"""
Complete guide and script for downloading MIMIC-IV data for heart failure.
"""

import os
from pathlib import Path
import subprocess


def print_complete_guide():
    """Print complete step-by-step guide."""
    
    print("="*80)
    print("COMPLETE GUIDE: Downloading MIMIC-IV for Heart Failure & Medications")
    print("="*80)
    
    print("\n" + "="*80)
    print("STEP 1: Complete CITI Training (2-4 hours)")
    print("="*80)
    print("""
1. Go to: https://www.citiprogram.org/
2. Click "Register" and create an account
3. Select your institution (or "Independent Learner" if not affiliated)
4. Complete the course: "Data or Specimens Only Research"
   - This is required for accessing de-identified patient data
   - Takes approximately 2-4 hours
   - You can pause and resume
5. Complete all modules and pass the quiz
6. Download your completion certificate (PDF)
   - Save it somewhere accessible
   - You'll need to upload this to PhysioNet
    """)
    
    print("\n" + "="*80)
    print("STEP 2: Create PhysioNet Account (5 minutes)")
    print("="*80)
    print("""
1. Go to: https://physionet.org/
2. Click "Sign up" in the top right
3. Fill in your information:
   - Name, email, institution
   - Create a username and password
4. Verify your email address (check your inbox)
5. Log in to your account
    """)
    
    print("\n" + "="*80)
    print("STEP 3: Request MIMIC-IV Access (5 minutes + 1-3 days wait)")
    print("="*80)
    print("""
1. Go to: https://physionet.org/content/mimiciv/
2. Click "Request access" or "Sign the data use agreement"
3. You'll be asked to:
   a. Upload your CITI completion certificate (PDF)
   b. Sign the data use agreement (DUA)
   c. Provide your research purpose
4. Submit your request
5. Wait for approval (typically 1-3 business days)
   - You'll receive an email when approved
   - Check your PhysioNet account status
    """)
    
    print("\n" + "="*80)
    print("STEP 4: Download MIMIC-IV Data (Several hours - 50+ GB)")
    print("="*80)
    
    print("\n📋 OPTION A: Using wget (Recommended for large downloads)")
    print("-" * 80)
    print("""
# 1. Create download directory
mkdir -p data/raw/mimic
cd data/raw/mimic

# 2. Download using wget (replace YOUR_USERNAME and YOUR_PASSWORD)
wget -r -N -c -np \\
     --user YOUR_PHYSIONET_USERNAME \\
     --password YOUR_PHYSIONET_PASSWORD \\
     https://physionet.org/files/mimiciv/2.2/

# This will download the entire MIMIC-IV database
# Size: ~50 GB compressed, ~100+ GB uncompressed
# Time: Several hours depending on connection
    """)
    
    print("\n📋 OPTION B: Using Python physionet-download package")
    print("-" * 80)
    print("""
# 1. Install the package
pip install physionet-download

# 2. Download using Python
python << EOF
from physionet_download import download_physionet_files

download_physionet_files(
    project_name='mimiciv',
    output_dir='data/raw/mimic',
    version='2.2',
    username='YOUR_PHYSIONET_USERNAME',
    password='YOUR_PHYSIONET_PASSWORD'
)
EOF
    """)
    
    print("\n📋 OPTION C: Manual Download via Browser")
    print("-" * 80)
    print("""
1. Go to: https://physionet.org/content/mimiciv/
2. Click "Files" tab
3. Browse to the version you want (e.g., 2.2/)
4. Download files individually or as zip archives
5. Extract to: data/raw/mimic/
    """)
    
    print("\n" + "="*80)
    print("STEP 5: Extract Heart Failure & Medication Data")
    print("="*80)
    print("""
After downloading, you'll need to extract specific tables:

FOR HEART FAILURE PATIENTS:
1. diagnoses_icd.csv - Contains ICD codes (I50.* for heart failure)
2. patients.csv - Patient demographics
3. admissions.csv - Admission information
4. icustays.csv - ICU stay information

FOR MEDICATION DATA:
1. prescriptions.csv - Medication prescriptions
2. Contains: drug names, dosages, routes, frequencies

We'll create a script to extract heart failure cohort and link medications.
    """)


def create_extraction_script():
    """Create script to extract heart failure and medication data."""
    
    script_content = '''"""
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
    
    print("\\n" + "="*70)
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
    
    print("\\n" + "="*70)
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
    
    print("\\n" + "="*70)
    print("Extraction Complete!")
    print("="*70)
    print(f"\\nExtracted data saved to: data/processed/mimic_hf/")
    print("\\nYou can now use this data for training your Patient Digital Twin.")


if __name__ == "__main__":
    main()
'''
    
    script_path = Path("scripts/extract_mimic_hf_data.py")
    script_path.write_text(script_content)
    print(f"\n✓ Created extraction script: {script_path}")


if __name__ == "__main__":
    print_complete_guide()
    create_extraction_script()
    
    print("\n" + "="*80)
    print("QUICK REFERENCE COMMANDS")
    print("="*80)
    print("""
After you get MIMIC-IV access and download the data:

1. Extract heart failure cohort and medications:
   python scripts/extract_mimic_hf_data.py

2. Verify extracted data:
   ls -lh data/processed/mimic_hf/

3. Check patient count:
   python -c "import pandas as pd; print(len(pd.read_csv('data/processed/mimic_hf/hf_patient_ids.csv')))"
    """)



