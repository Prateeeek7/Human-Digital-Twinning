"""
Combine all datasets (UCI, Kaggle, MIMIC-IV ED) into unified training dataset.
"""

import pandas as pd
import numpy as np
import gzip
from pathlib import Path
from typing import Dict, List, Optional


def load_uci_dataset() -> pd.DataFrame:
    """Load and standardize UCI dataset."""
    print("Loading UCI Heart Failure dataset...")
    df = pd.read_csv('data/raw/uci/heart_failure_clinical_records_dataset.csv')
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Create target column
    if 'death_event' in df.columns:
        df['target'] = df['death_event']
    elif 'target' not in df.columns:
        df['target'] = 0  # Default if no target
    
    # Add dataset identifier
    df['dataset_source'] = 'UCI'
    
    # Standardize feature names
    feature_mapping = {
        'ejection_fraction': 'ejection_fraction',
        'serum_creatinine': 'creatinine',
        'serum_sodium': 'sodium',
        'creatinine_phosphokinase': 'cpk',
    }
    
    for old, new in feature_mapping.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
    
    print(f"  ✓ Loaded {len(df):,} patients")
    return df


def load_kaggle_brfss() -> pd.DataFrame:
    """Load and standardize BRFSS dataset."""
    print("Loading Kaggle BRFSS dataset...")
    df = pd.read_csv('data/raw/kaggle/heart_disease_health_indicators_BRFSS2015.csv')
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Create target (heart disease or attack)
    if 'heartdiseaseorattack' in df.columns:
        df['target'] = df['heartdiseaseorattack']
    else:
        df['target'] = 0
    
    # Add dataset identifier
    df['dataset_source'] = 'Kaggle_BRFSS'
    
    # Map to common features
    if 'highbp' in df.columns:
        df['high_blood_pressure'] = df['highbp']
    if 'highchol' in df.columns:
        df['high_cholesterol'] = df['highchol']
    
    print(f"  ✓ Loaded {len(df):,} patients")
    return df


def load_kaggle_heart() -> pd.DataFrame:
    """Load and standardize Kaggle heart dataset."""
    print("Loading Kaggle Heart dataset...")
    df = pd.read_csv('data/raw/kaggle/heart.csv')
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Create target
    if 'heartdisease' in df.columns:
        df['target'] = df['heartdisease']
    elif 'target' in df.columns:
        pass  # Already exists
    else:
        df['target'] = 0
    
    # Add dataset identifier
    df['dataset_source'] = 'Kaggle_Heart'
    
    # Map features
    if 'trestbps' in df.columns:
        df['systolic_bp'] = df['trestbps']
    if 'chol' in df.columns:
        df['cholesterol'] = df['chol']
    if 'fbs' in df.columns:
        df['fasting_blood_sugar'] = df['fbs']
    
    print(f"  ✓ Loaded {len(df):,} patients")
    return df


def load_mimic_ed_data() -> Optional[pd.DataFrame]:
    """Load and process MIMIC-IV ED demo data."""
    print("Loading MIMIC-IV ED demo data...")
    
    ed_path = Path('mimic-iv-ed-demo-2.2/ed')
    if not ed_path.exists():
        print("  ✗ MIMIC-IV ED directory not found")
        return None
    
    try:
        # Load ED stays
        with gzip.open(ed_path / 'edstays.csv.gz', 'rt') as f:
            edstays = pd.read_csv(f)
        
        # Load diagnoses
        with gzip.open(ed_path / 'diagnosis.csv.gz', 'rt') as f:
            diagnoses = pd.read_csv(f)
        
        # Load medications
        with gzip.open(ed_path / 'medrecon.csv.gz', 'rt') as f:
            medications = pd.read_csv(f)
        
        # Load vital signs
        with gzip.open(ed_path / 'vitalsign.csv.gz', 'rt') as f:
            vitals = pd.read_csv(f)
        
        # Extract heart failure patients
        hf_codes = diagnoses[diagnoses['icd_code'].str.startswith('I50', na=False)]
        hf_patient_ids = hf_codes['subject_id'].unique()
        
        if len(hf_patient_ids) == 0:
            print("  ⚠ No heart failure patients found in MIMIC-IV ED")
            return None
        
        # Create patient-level features
        mimic_data = []
        
        for patient_id in hf_patient_ids:
            # Get patient info
            patient_stays = edstays[edstays['subject_id'] == patient_id]
            if len(patient_stays) == 0:
                continue
            
            # Get latest stay
            latest_stay = patient_stays.iloc[0]
            stay_id = latest_stay['stay_id']
            
            # Get vital signs for this stay
            stay_vitals = vitals[vitals['stay_id'] == stay_id]
            
            # Get medications
            stay_meds = medications[medications['stay_id'] == stay_id]
            
            # Create feature vector
            features = {
                'patient_id': patient_id,
                'age': np.nan,  # Not in ED demo
                'sex': 1 if latest_stay['gender'] == 'M' else 0,
                'target': 1,  # Heart failure patient
                'dataset_source': 'MIMIC_ED'
            }
            
            # Add vital signs (use mean if multiple)
            if len(stay_vitals) > 0:
                features['heart_rate'] = stay_vitals['heartrate'].mean()
                features['systolic_bp'] = stay_vitals['sbp'].mean()
                features['diastolic_bp'] = stay_vitals['dbp'].mean()
                features['oxygen_saturation'] = stay_vitals['o2sat'].mean()
                features['temperature'] = stay_vitals['temperature'].mean()
                features['respiratory_rate'] = stay_vitals['resprate'].mean()
            
            # Count medications
            features['num_medications'] = len(stay_meds)
            
            # Check for HF medications
            if len(stay_meds) > 0:
                med_names = stay_meds['name'].str.lower().fillna('')
                features['has_ace_inhibitor'] = med_names.str.contains('lisinopril|enalapril|captopril', case=False, na=False).any()
                features['has_beta_blocker'] = med_names.str.contains('metoprolol|carvedilol|bisoprolol', case=False, na=False).any()
                features['has_diuretic'] = med_names.str.contains('furosemide|bumetanide', case=False, na=False).any()
            
            mimic_data.append(features)
        
        if len(mimic_data) == 0:
            print("  ⚠ No processable heart failure patients")
            return None
        
        df = pd.DataFrame(mimic_data)
        print(f"  ✓ Loaded {len(df):,} heart failure patients from MIMIC-IV ED")
        return df
        
    except Exception as e:
        print(f"  ✗ Error loading MIMIC-IV ED: {e}")
        return None


def align_features(datasets: List[pd.DataFrame]) -> pd.DataFrame:
    """Align features across datasets and combine."""
    print("\n" + "="*70)
    print("Aligning Features Across Datasets")
    print("="*70)
    
    # Define common feature set
    common_features = [
        # Demographics
        'age', 'sex', 'gender',
        
        # Vital signs
        'heart_rate', 'systolic_bp', 'diastolic_bp', 'blood_pressure',
        'oxygen_saturation', 'temperature', 'respiratory_rate',
        
        # Lab values
        'creatinine', 'sodium', 'cholesterol', 'cpk',
        'hemoglobin', 'bnp', 'glucose',
        
        # Cardiac
        'ejection_fraction', 'high_blood_pressure', 'high_cholesterol',
        
        # Comorbidities
        'diabetes', 'anaemia', 'smoking',
        
        # Medications
        'has_ace_inhibitor', 'has_beta_blocker', 'has_diuretic',
        'num_medications',
        
        # Target and metadata
        'target', 'dataset_source'
    ]
    
    # Process each dataset
    aligned_datasets = []
    
    for i, df in enumerate(datasets):
        if df is None or len(df) == 0:
            continue
        
        print(f"\nProcessing dataset {i+1} ({df['dataset_source'].iloc[0] if 'dataset_source' in df.columns else 'unknown'}):")
        
        # Create aligned dataframe
        aligned = pd.DataFrame()
        
        # Add common features
        for feat in common_features:
            # Try different variations
            possible_names = [
                feat,
                feat.lower(),
                feat.upper(),
                feat.replace('_', ' '),
                feat.replace('_', '')
            ]
            
            found = False
            for name in possible_names:
                if name in df.columns:
                    aligned[feat] = df[name]
                    found = True
                    break
            
            if not found:
                aligned[feat] = np.nan
        
        # Add patient ID if not exists
        if 'patient_id' not in aligned.columns:
            if 'subject_id' in df.columns:
                aligned['patient_id'] = df['subject_id']
            elif 'id' in df.columns:
                aligned['patient_id'] = df['id']
            else:
                aligned['patient_id'] = range(len(df))
        
        aligned_datasets.append(aligned)
        print(f"  ✓ Aligned {len(aligned):,} patients with {len([c for c in aligned.columns if aligned[c].notna().any()])} features")
    
    # Combine all datasets
    print("\nCombining all datasets...")
    combined = pd.concat(aligned_datasets, ignore_index=True)
    
    print(f"  ✓ Combined dataset: {len(combined):,} patients, {len(combined.columns)} columns")
    
    return combined


def clean_and_prepare(combined: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare final dataset."""
    print("\n" + "="*70)
    print("Cleaning and Preparing Final Dataset")
    print("="*70)
    
    # Remove duplicates based on patient_id if exists
    if 'patient_id' in combined.columns:
        before = len(combined)
        combined = combined.drop_duplicates(subset=['patient_id'], keep='first')
        print(f"  Removed {before - len(combined)} duplicate patients")
    
    # Handle missing values - create missing indicators
    print("\nHandling missing values...")
    numeric_cols = combined.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['target', 'patient_id']]
    
    for col in numeric_cols:
        if combined[col].isna().sum() > 0:
            # Add missing indicator
            combined[f'{col}_missing'] = combined[col].isna().astype(int)
            # Fill with median
            combined[col].fillna(combined[col].median(), inplace=True)
    
    # Ensure target is binary
    if 'target' in combined.columns:
        combined['target'] = combined['target'].astype(int)
        print(f"  Target distribution: {combined['target'].value_counts().to_dict()}")
    
    # Final feature selection
    # Keep features with at least 10% non-missing values
    feature_cols = [c for c in combined.columns 
                   if c not in ['target', 'patient_id', 'dataset_source'] 
                   and combined[c].notna().sum() >= len(combined) * 0.1]
    
    final_cols = ['patient_id'] + feature_cols + ['target', 'dataset_source']
    final_cols = [c for c in final_cols if c in combined.columns]
    
    final_df = combined[final_cols].copy()
    
    print(f"\n  ✓ Final dataset: {len(final_df):,} patients")
    print(f"  ✓ Features: {len(feature_cols)}")
    print(f"  ✓ Missing data handled")
    
    return final_df


def save_dataset(df: pd.DataFrame, output_path: str = 'data/processed/combined_dataset.csv'):
    """Save combined dataset."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved combined dataset to: {output_path}")
    print(f"  Size: {output_path.stat().st_size / (1024*1024):.2f} MB")


def print_summary(df: pd.DataFrame):
    """Print dataset summary."""
    print("\n" + "="*70)
    print("Final Dataset Summary")
    print("="*70)
    
    print(f"\nTotal Patients: {len(df):,}")
    print(f"Total Features: {len([c for c in df.columns if c not in ['patient_id', 'target', 'dataset_source']])}")
    
    print("\nBy Dataset Source:")
    if 'dataset_source' in df.columns:
        print(df['dataset_source'].value_counts())
    
    print("\nTarget Distribution:")
    if 'target' in df.columns:
        print(df['target'].value_counts())
        print(f"Positive cases: {df['target'].sum():,} ({df['target'].mean()*100:.1f}%)")
    
    print("\nFeature Statistics:")
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_features = [f for f in numeric_features if f not in ['target', 'patient_id']]
    
    print(f"  Numeric features: {len(numeric_features)}")
    print(f"  Sample features: {numeric_features[:10]}")
    
    print("\nMissing Data:")
    missing = df[numeric_features].isna().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(missing.head(10))
    else:
        print("  ✓ No missing values in numeric features")


def main():
    """Main function to combine all datasets."""
    print("="*70)
    print("Combining All Datasets for Training")
    print("="*70)
    print()
    
    # Load all datasets
    datasets = []
    
    # UCI
    try:
        uci_df = load_uci_dataset()
        datasets.append(uci_df)
    except Exception as e:
        print(f"  ✗ Error loading UCI: {e}")
    
    # Kaggle BRFSS
    try:
        brfss_df = load_kaggle_brfss()
        datasets.append(brfss_df)
    except Exception as e:
        print(f"  ✗ Error loading BRFSS: {e}")
    
    # Kaggle Heart
    try:
        heart_df = load_kaggle_heart()
        datasets.append(heart_df)
    except Exception as e:
        print(f"  ✗ Error loading Kaggle Heart: {e}")
    
    # MIMIC-IV ED
    mimic_df = load_mimic_ed_data()
    if mimic_df is not None:
        datasets.append(mimic_df)
    
    if len(datasets) == 0:
        print("\n✗ No datasets loaded. Check file paths.")
        return
    
    # Align and combine
    combined = align_features(datasets)
    
    # Clean and prepare
    final_df = clean_and_prepare(combined)
    
    # Save
    save_dataset(final_df)
    
    # Print summary
    print_summary(final_df)
    
    print("\n" + "="*70)
    print("✓ Dataset Combination Complete!")
    print("="*70)
    print("\nReady for training!")
    print("Location: data/processed/combined_dataset.csv")


if __name__ == "__main__":
    main()



