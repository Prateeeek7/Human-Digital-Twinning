"""
Helper script to set up Kaggle API for dataset downloads.
"""

import os
from pathlib import Path
import json


def setup_kaggle():
    """Guide user through Kaggle API setup."""
    print("="*60)
    print("Kaggle API Setup Guide")
    print("="*60)
    
    print("\n1. Install Kaggle package:")
    print("   pip install kaggle")
    
    print("\n2. Get your Kaggle API credentials:")
    print("   a. Go to https://www.kaggle.com/")
    print("   b. Sign in to your account")
    print("   c. Go to Account settings: https://www.kaggle.com/settings")
    print("   d. Scroll to 'API' section")
    print("   e. Click 'Create New API Token'")
    print("   f. This downloads kaggle.json")
    
    print("\n3. Place kaggle.json in the correct location:")
    kaggle_dir = Path.home() / ".kaggle"
    print(f"   {kaggle_dir}/kaggle.json")
    
    print("\n4. Set proper permissions (Linux/Mac):")
    print(f"   chmod 600 {kaggle_dir}/kaggle.json")
    
    print("\n5. After setup, run download_data.py again")
    
    # Check if already set up
    kaggle_file = kaggle_dir / "kaggle.json"
    if kaggle_file.exists():
        print("\n✓ Kaggle credentials file found!")
        print(f"  Location: {kaggle_file}")
    else:
        print(f"\n✗ Kaggle credentials not found at {kaggle_file}")
        print("  Please follow the steps above to set up.")


if __name__ == "__main__":
    setup_kaggle()



