"""
Comprehensive script to download all available datasets.
"""

import sys
from pathlib import Path


def download_kaggle_with_instructions():
    """Attempt Kaggle download with helpful instructions."""
    print("\n" + "="*70)
    print("KAGGLE DATASET DOWNLOAD")
    print("="*70)
    
    # Check credentials first (before importing kaggle which auto-authenticates)
    kaggle_dir = Path.home() / ".kaggle"
    credentials_file = kaggle_dir / "kaggle.json"
    
    if not credentials_file.exists():
        print("\n✗ Kaggle credentials not found")
        print(f"  Expected location: {credentials_file}")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("-" * 70)
        print("1. Go to: https://www.kaggle.com/")
        print("2. Sign in to your account (or create one)")
        print("3. Go to Account Settings: https://www.kaggle.com/settings")
        print("4. Scroll to 'API' section")
        print("5. Click 'Create New API Token'")
        print("6. This downloads kaggle.json file")
        print(f"7. Move kaggle.json to: {kaggle_dir}/")
        print("8. Set permissions (Mac/Linux): chmod 600 ~/.kaggle/kaggle.json")
        print("\nAfter setting up, run this script again.")
        return False
    
    print(f"✓ Kaggle credentials found at {credentials_file}")
    
    # Check if kaggle is installed
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("✗ Kaggle package not installed")
        print("\nInstalling Kaggle package...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        print("✓ Kaggle installed")
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
        except ImportError:
            print("✗ Failed to import Kaggle. Please install manually: pip install kaggle")
            return False
    
    # Check credentials
    kaggle_dir = Path.home() / ".kaggle"
    credentials_file = kaggle_dir / "kaggle.json"
    
    if not credentials_file.exists():
        print("\n✗ Kaggle credentials not found")
        print(f"  Expected location: {credentials_file}")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("-" * 70)
        print("1. Go to: https://www.kaggle.com/")
        print("2. Sign in to your account (or create one)")
        print("3. Go to Account Settings: https://www.kaggle.com/settings")
        print("4. Scroll to 'API' section")
        print("5. Click 'Create New API Token'")
        print("6. This downloads kaggle.json file")
        print(f"7. Move kaggle.json to: {kaggle_dir}/")
        print("8. Set permissions (Mac/Linux): chmod 600 ~/.kaggle/kaggle.json")
        print("\nAfter setting up, run this script again.")
        return False
    
    # Try to download datasets
    try:
        api = KaggleApi()
        api.authenticate()
        print("✓ Kaggle API authenticated")
        
        # List of heart failure datasets
        datasets = [
            "fedesoriano/heart-failure-prediction",
            "dileep070/heart-disease-prediction",
        ]
        
        save_path = Path("data/raw/kaggle")
        save_path.mkdir(parents=True, exist_ok=True)
        
        downloaded = []
        for dataset in datasets:
            try:
                print(f"\nDownloading: {dataset}...")
                api.dataset_download_files(
                    dataset,
                    path=str(save_path),
                    unzip=True
                )
                print(f"✓ Successfully downloaded {dataset}")
                downloaded.append(dataset)
            except Exception as e:
                print(f"✗ Failed to download {dataset}: {e}")
                print("  Note: You may need to accept dataset terms on Kaggle first")
        
        if downloaded:
            print(f"\n✓ Downloaded {len(downloaded)} Kaggle dataset(s)")
            return True
        else:
            print("\n✗ No datasets downloaded")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Download all available datasets."""
    print("="*70)
    print("COMPREHENSIVE DATASET DOWNLOAD")
    print("="*70)
    
    # 1. UCI Dataset (already downloaded)
    print("\n1. UCI Heart Failure Dataset")
    print("-" * 70)
    uci_path = Path("data/raw/uci/heart_failure_clinical_records_dataset.csv")
    if uci_path.exists():
        print("✓ UCI dataset already downloaded")
    else:
        print("Downloading UCI dataset...")
        from scripts.download_data import download_uci_dataset
        download_uci_dataset()
    
    # 2. Kaggle Datasets
    print("\n2. Kaggle Datasets")
    print("-" * 70)
    kaggle_success = download_kaggle_with_instructions()
    
    # 3. MIMIC-IV
    print("\n3. MIMIC-IV Dataset")
    print("-" * 70)
    print("MIMIC-IV requires manual setup.")
    print("\nFor detailed instructions, run:")
    print("  python scripts/download_mimic_guide.py")
    print("\nOr see: DATASET_DOWNLOAD_GUIDE.md")
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"UCI Dataset: ✓ Available")
    print(f"Kaggle Datasets: {'✓ Downloaded' if kaggle_success else '✗ Requires setup'}")
    print(f"MIMIC-IV: ✗ Requires credentialed access (see instructions above)")
    
    print("\nNext steps:")
    if kaggle_success:
        print("✓ Kaggle datasets ready")
    else:
        print("1. Set up Kaggle API credentials (see instructions above)")
        print("2. Run this script again")
    
    print("3. For MIMIC-IV, follow the detailed instructions above")
    print("4. Verify all data: python scripts/verify_data.py")


if __name__ == "__main__":
    main()

