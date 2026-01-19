"""
Download drug/medication datasets relevant for heart failure treatment.
"""

from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path
import pandas as pd


def download_drug_datasets():
    """Download drug and medication datasets."""
    
    # Drug/medication datasets relevant for heart failure
    drug_datasets = [
        'prathamtripathi/drug-classification',  # Available
    ]
    
    api = KaggleApi()
    api.authenticate()
    
    save_path = Path("data/raw/drugs")
    save_path.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    failed = []
    
    print("="*70)
    print("Downloading Drug/Medication Datasets")
    print("="*70)
    
    for dataset in drug_datasets:
        try:
            print(f"\nTrying: {dataset}...")
            
            # Try to download
            api.dataset_download_files(
                dataset,
                path=str(save_path),
                unzip=True
            )
            print(f"  ✓ Successfully downloaded: {dataset}")
            downloaded.append(dataset)
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                print(f"  ✗ Access denied - may need to accept terms")
                print(f"    Visit: https://www.kaggle.com/datasets/{dataset}")
            elif "404" in error_msg or "Not Found" in error_msg:
                print(f"  ✗ Dataset not found")
            else:
                print(f"  ✗ Error: {error_msg}")
            failed.append((dataset, error_msg))
    
    # Check existing datasets for medication data
    print("\n" + "="*70)
    print("Checking Existing Datasets for Medication Data")
    print("="*70)
    
    existing_files = [
        'data/raw/uci/heart_failure_clinical_records_dataset.csv',
    ]
    
    for file_path in existing_files:
        try:
            df = pd.read_csv(file_path)
            med_cols = [col for col in df.columns if any(term in col.lower() 
                       for term in ['med', 'drug', 'medication', 'prescription', 'treatment'])]
            if med_cols:
                print(f"\n{file_path}:")
                print(f"  Found medication-related columns: {med_cols}")
        except:
            pass
    
    return downloaded, failed


if __name__ == "__main__":
    downloaded, failed = download_drug_datasets()
    
    print("\n" + "="*70)
    print("Alternative Drug Data Sources")
    print("="*70)
    print("""
1. MIMIC-IV (BEST SOURCE - when you get access):
   - Contains real medication/prescription data
   - Table: prescriptions.csv
   - Includes: drug names, dosages, administration times
   - This is the gold standard for medication data

2. DrugBank Database:
   - Comprehensive drug information
   - Website: https://go.drugbank.com/
   - Free access with registration
   - Includes: drug properties, interactions, targets

3. FDA Drug Databases:
   - https://www.fda.gov/drugs/drug-approvals-and-databases
   - Drug labeling, adverse events, approvals

4. UCI Drug Consumption Dataset:
   - https://archive.ics.uci.edu/ml/datasets/Drug+consumption+(quantified)
   - Drug usage patterns and responses

5. Clinical Trial Data:
   - ClinicalTrials.gov
   - Medication outcomes from trials
    """)
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    if downloaded:
        print(f"✓ Downloaded {len(downloaded)} drug dataset(s)")
    else:
        print("✗ No drug datasets downloaded from Kaggle")
        print("\nRecommendation: MIMIC-IV is the best source for medication data")
        print("  It includes real-world prescription data for heart failure patients")



