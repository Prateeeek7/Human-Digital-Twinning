"""
Download specific Kaggle heart failure datasets.
"""

from pathlib import Path
import subprocess
import sys


def download_kaggle_dataset(dataset_name, save_path=None):
    """
    Download a Kaggle dataset.
    
    Args:
        dataset_name: Kaggle dataset name (e.g., 'dileep070/heart-disease-prediction')
        save_path: Path to save dataset (default: data/raw/kaggle)
    """
    if save_path is None:
        save_path = Path("data/raw/kaggle")
    else:
        save_path = Path(save_path)
    
    save_path.mkdir(parents=True, exist_ok=True)
    
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print(f"Downloading {dataset_name}...")
        api.dataset_download_files(dataset_name, path=str(save_path), unzip=True)
        print(f"✓ Successfully downloaded to {save_path}")
        return True
    except ImportError:
        print("✗ Kaggle package not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Make sure you have:")
        print("  1. Accepted the dataset terms on Kaggle")
        print("  2. Set up kaggle.json credentials")
        return False


def main():
    """Download common heart failure datasets from Kaggle."""
    print("="*60)
    print("Kaggle Heart Failure Datasets Download")
    print("="*60)
    
    # Common heart failure datasets on Kaggle
    datasets = [
        "dileep070/heart-disease-prediction",
        "fedesoriano/heart-failure-prediction",
        # Add more as needed
    ]
    
    print("\nAvailable datasets:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset}")
    
    print("\nNote: You need to:")
    print("  1. Have Kaggle API set up (run setup_kaggle.py)")
    print("  2. Accept dataset terms on Kaggle website")
    
    for dataset in datasets:
        print(f"\n{'='*60}")
        print(f"Downloading: {dataset}")
        print('='*60)
        download_kaggle_dataset(dataset)


if __name__ == "__main__":
    main()



