"""
Download available heart disease datasets from Kaggle.
"""

from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path
import os


def download_available_datasets():
    """Download all available heart disease datasets."""
    
    # List of heart disease datasets to try
    datasets_to_try = [
        'fedesoriano/heart-failure-prediction',  # Already downloaded
        'johnsmith88/heart-disease-dataset',
        'rashiq/heart-disease-prediction',
        'alexteboul/heart-disease-health-indicators-dataset',
        'johnsmith88/heart-disease-dataset',
    ]
    
    api = KaggleApi()
    api.authenticate()
    
    save_path = Path("data/raw/kaggle")
    save_path.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    failed = []
    
    print("="*70)
    print("Downloading Heart Disease Datasets from Kaggle")
    print("="*70)
    
    for dataset in datasets_to_try:
        try:
            print(f"\nTrying: {dataset}...")
            
            # Check if already downloaded
            dataset_name = dataset.split('/')[-1]
            if any(save_path.glob(f"*{dataset_name}*")):
                print(f"  ⚠ Already exists, skipping...")
                continue
            
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
                print(f"  ✗ Access denied - may need to accept terms on Kaggle")
                print(f"    Visit: https://www.kaggle.com/datasets/{dataset}")
            elif "404" in error_msg or "Not Found" in error_msg:
                print(f"  ✗ Dataset not found")
            else:
                print(f"  ✗ Error: {error_msg}")
            failed.append((dataset, error_msg))
    
    # Summary
    print("\n" + "="*70)
    print("Download Summary")
    print("="*70)
    print(f"✓ Successfully downloaded: {len(downloaded)}")
    for ds in downloaded:
        print(f"  - {ds}")
    
    if failed:
        print(f"\n✗ Failed: {len(failed)}")
        for ds, error in failed:
            print(f"  - {ds}")
    
    return downloaded, failed


if __name__ == "__main__":
    downloaded, failed = download_available_datasets()
    
    print("\n" + "="*70)
    print("Next Steps")
    print("="*70)
    if downloaded:
        print("✓ Datasets downloaded successfully!")
        print("  Verify with: python scripts/verify_data.py")
    else:
        print("No new datasets downloaded.")
        print("You can search for more datasets at: https://www.kaggle.com/datasets")
        print("Search for: 'heart disease', 'heart failure', 'cardiac'")



