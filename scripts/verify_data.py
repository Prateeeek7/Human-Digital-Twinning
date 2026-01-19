"""
Verify downloaded datasets and provide summary.
"""

from pathlib import Path
import pandas as pd


def verify_uci_dataset():
    """Verify UCI dataset."""
    uci_path = Path("data/raw/uci/heart_failure_clinical_records_dataset.csv")
    
    if not uci_path.exists():
        return False, "UCI dataset not found"
    
    try:
        df = pd.read_csv(uci_path)
        return True, {
            "rows": len(df),
            "columns": len(df.columns),
            "size_mb": uci_path.stat().st_size / (1024 * 1024),
            "columns_list": df.columns.tolist()
        }
    except Exception as e:
        return False, f"Error reading dataset: {e}"


def verify_kaggle_datasets():
    """Verify Kaggle datasets."""
    kaggle_dir = Path("data/raw/kaggle")
    
    if not kaggle_dir.exists():
        return False, "Kaggle directory not found"
    
    csv_files = list(kaggle_dir.glob("*.csv"))
    
    if not csv_files:
        return False, "No Kaggle datasets found"
    
    results = {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            results[csv_file.name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "size_mb": csv_file.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            results[csv_file.name] = f"Error: {e}"
    
    return True, results


def verify_mimic_data():
    """Check for MIMIC-IV data."""
    mimic_dir = Path("data/raw/mimic")
    
    if not mimic_dir.exists():
        return False, "MIMIC directory not found"
    
    csv_files = list(mimic_dir.glob("*.csv"))
    
    if csv_files:
        return True, {
            "files_found": len(csv_files),
            "file_names": [f.name for f in csv_files[:5]]  # First 5
        }
    else:
        return False, "No MIMIC-IV files found (requires credentialed access)"


def main():
    """Verify all datasets."""
    print("="*60)
    print("Dataset Verification Report")
    print("="*60)
    
    # UCI Dataset
    print("\n1. UCI Heart Failure Dataset:")
    print("-" * 60)
    success, info = verify_uci_dataset()
    if success:
        print("✓ Dataset found and valid")
        print(f"  Rows: {info['rows']}")
        print(f"  Columns: {info['columns']}")
        print(f"  Size: {info['size_mb']:.2f} MB")
        print(f"  Columns: {', '.join(info['columns_list'][:5])}...")
    else:
        print(f"✗ {info}")
    
    # Kaggle Datasets
    print("\n2. Kaggle Datasets:")
    print("-" * 60)
    success, info = verify_kaggle_datasets()
    if success:
        print("✓ Kaggle datasets found:")
        for filename, details in info.items():
            if isinstance(details, dict):
                print(f"  - {filename}: {details['rows']} rows, {details['columns']} columns, {details['size_mb']:.2f} MB")
            else:
                print(f"  - {filename}: {details}")
    else:
        print(f"✗ {info}")
        print("  To download: Set up Kaggle API and run download_kaggle_datasets.py")
    
    # MIMIC-IV
    print("\n3. MIMIC-IV Dataset:")
    print("-" * 60)
    success, info = verify_mimic_data()
    if success:
        print("✓ MIMIC-IV data found")
        print(f"  Files: {info['files_found']}")
        print(f"  Sample files: {', '.join(info['file_names'])}")
    else:
        print(f"✗ {info}")
        print("  To obtain: Complete CITI training and request access via PhysioNet")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    uci_ok, _ = verify_uci_dataset()
    kaggle_ok, _ = verify_kaggle_datasets()
    mimic_ok, _ = verify_mimic_data()
    
    total_available = sum([uci_ok, kaggle_ok, mimic_ok])
    
    print(f"Datasets available: {total_available}/3")
    print(f"  - UCI: {'✓' if uci_ok else '✗'}")
    print(f"  - Kaggle: {'✓' if kaggle_ok else '✗'}")
    print(f"  - MIMIC-IV: {'✓' if mimic_ok else '✗'}")
    
    if uci_ok:
        print("\n✓ Ready to start training with UCI dataset!")
        print("  Run: python scripts/train_baseline.py")


if __name__ == "__main__":
    main()



