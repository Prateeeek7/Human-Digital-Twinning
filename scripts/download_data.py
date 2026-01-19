"""
Download all required datasets for training.
"""

import os
import urllib.request
from pathlib import Path
import zipfile
import tarfile
import subprocess
import sys


def create_data_directories():
    """Create data directory structure."""
    data_dirs = [
        "data/raw/uci",
        "data/raw/kaggle",
        "data/raw/mimic",
        "data/processed",
        "data/cache"
    ]
    
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")


def download_uci_dataset():
    """Download UCI Heart Failure Clinical Records dataset."""
    print("\n" + "="*60)
    print("Downloading UCI Heart Failure Clinical Records Dataset")
    print("="*60)
    
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv"
    save_path = Path("data/raw/uci/heart_failure_clinical_records_dataset.csv")
    
    if save_path.exists():
        print(f"Dataset already exists at {save_path}")
        return str(save_path)
    
    try:
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, save_path)
        print(f"✓ Successfully downloaded to {save_path}")
        return str(save_path)
    except Exception as e:
        print(f"✗ Error downloading UCI dataset: {e}")
        return None


def download_kaggle_dataset(dataset_name="heart-failure-prediction"):
    """
    Download Kaggle dataset (requires Kaggle API credentials).
    
    Args:
        dataset_name: Name of the Kaggle dataset
    """
    print("\n" + "="*60)
    print("Downloading Kaggle Heart Failure Dataset")
    print("="*60)
    
    # Check if kaggle is installed
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("✗ Kaggle API not installed.")
        print("  Install with: pip install kaggle")
        print("  Then set up credentials: https://www.kaggle.com/docs/api")
        return None
    except Exception as e:
        # Kaggle installed but credentials not set up
        print("✗ Kaggle API installed but credentials not configured.")
        print("  Set up credentials: https://www.kaggle.com/docs/api")
        return None
    
    # Check if credentials exist
    kaggle_dir = Path.home() / ".kaggle"
    credentials_file = kaggle_dir / "kaggle.json"
    
    if not credentials_file.exists():
        print("✗ Kaggle credentials not found.")
        print(f"  Please download kaggle.json from https://www.kaggle.com/settings")
        print(f"  and place it in {kaggle_dir}/")
        return None
    
    save_path = Path("data/raw/kaggle")
    
    try:
        print(f"Downloading dataset: {dataset_name}...")
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_name, path=str(save_path), unzip=True)
        print(f"✓ Successfully downloaded to {save_path}")
        return str(save_path)
    except IOError as e:
        print(f"✗ Kaggle credentials not found: {e}")
        print("  Run: python scripts/setup_kaggle.py for setup instructions")
        return None
    except Exception as e:
        print(f"✗ Error downloading Kaggle dataset: {e}")
        print("  Note: You may need to accept the dataset terms on Kaggle first")
        return None


def download_additional_datasets():
    """Download additional publicly available heart failure datasets."""
    print("\n" + "="*60)
    print("Downloading Additional Datasets")
    print("="*60)
    
    # UCI has the main dataset, but we can add more sources
    print("Additional datasets can be downloaded manually:")
    print("  1. PhysioNet datasets (require credentials):")
    print("     - MIMIC-IV: https://physionet.org/content/mimiciv/")
    print("     - Zigong HF dataset: https://physionet.org/content/zigong-hf/")
    print("  2. Kaggle datasets:")
    print("     - Search for 'heart failure' on kaggle.com")
    print("     - Use: kaggle datasets download <dataset-name>")


def check_mimic_access():
    """Check if MIMIC-IV data is available."""
    print("\n" + "="*60)
    print("MIMIC-IV Dataset Access")
    print("="*60)
    
    mimic_path = Path("data/raw/mimic")
    
    if any(mimic_path.glob("*.csv")):
        print("✓ MIMIC-IV data files found")
        print(f"  Location: {mimic_path}")
    else:
        print("✗ MIMIC-IV data not found")
        print("  To obtain MIMIC-IV access:")
        print("  1. Complete CITI training: https://www.citiprogram.org/")
        print("  2. Request access: https://physionet.org/content/mimiciv/")
        print("  3. Sign data use agreement")
        print("  4. Download data and place in data/raw/mimic/")


def main():
    """Main download function."""
    print("="*60)
    print("Patient Digital Twin - Data Download Script")
    print("="*60)
    
    # Create directories
    create_data_directories()
    
    # Download UCI dataset
    uci_path = download_uci_dataset()
    
    # Try to download Kaggle dataset
    kaggle_path = download_kaggle_dataset()
    
    # Check MIMIC access
    check_mimic_access()
    
    # Additional info
    download_additional_datasets()
    
    print("\n" + "="*60)
    print("Download Summary")
    print("="*60)
    print(f"UCI Dataset: {'✓ Downloaded' if uci_path else '✗ Failed'}")
    print(f"Kaggle Dataset: {'✓ Downloaded' if kaggle_path else '✗ Not available (requires setup)'}")
    print(f"MIMIC-IV: Check manually (requires credentialed access)")
    print("\nNext steps:")
    print("1. If Kaggle download failed, set up Kaggle API credentials")
    print("2. For MIMIC-IV, follow the access instructions above")
    print("3. Run training scripts with: python scripts/train_baseline.py")


if __name__ == "__main__":
    main()

