"""
Guide for downloading MIMIC-IV dataset.
This script provides instructions since MIMIC-IV requires credentialed access.
"""

import os
from pathlib import Path


def check_mimic_access():
    """Check if MIMIC-IV is already downloaded."""
    mimic_path = Path("data/raw/mimic")
    
    if mimic_path.exists() and any(mimic_path.glob("*.csv")):
        csv_files = list(mimic_path.glob("*.csv"))
        print("✓ MIMIC-IV data found!")
        print(f"  Files: {len(csv_files)}")
        print(f"  Location: {mimic_path}")
        return True
    else:
        return False


def print_mimic_instructions():
    """Print detailed instructions for MIMIC-IV access."""
    print("="*70)
    print("MIMIC-IV Dataset Download Instructions")
    print("="*70)
    
    print("\n📋 STEP 1: Complete CITI Training")
    print("-" * 70)
    print("1. Go to: https://www.citiprogram.org/")
    print("2. Register for an account")
    print("3. Complete 'Data or Specimens Only Research' course")
    print("4. Download your completion certificate")
    print("   (This typically takes 2-4 hours)")
    
    print("\n📋 STEP 2: Create PhysioNet Account")
    print("-" * 70)
    print("1. Go to: https://physionet.org/")
    print("2. Click 'Sign up' and create an account")
    print("3. Verify your email address")
    
    print("\n📋 STEP 3: Request MIMIC-IV Access")
    print("-" * 70)
    print("1. Go to: https://physionet.org/content/mimiciv/")
    print("2. Click 'Request access' or 'Sign the data use agreement'")
    print("3. Upload your CITI completion certificate")
    print("4. Sign the data use agreement")
    print("5. Wait for approval (usually 1-3 business days)")
    
    print("\n📋 STEP 4: Download MIMIC-IV Data")
    print("-" * 70)
    print("Once approved, you can download via:")
    print("\nOption A: Using wget (recommended for large files)")
    print("-" * 70)
    print("1. Get your PhysioNet username and password")
    print("2. Run:")
    print("""
   cd data/raw/mimic
   wget -r -N -c -np --user YOUR_USERNAME --password YOUR_PASSWORD \\
        https://physionet.org/files/mimiciv/2.2/
    """)
    
    print("\nOption B: Using PhysioNet Credentialed Access")
    print("-" * 70)
    print("1. Install: pip install physionet-download")
    print("2. Run:")
    print("""
   from physionet_download import download_physionet_files
   download_physionet_files(
       project_name='mimiciv',
       output_dir='data/raw/mimic',
       version='2.2'
   )
    """)
    
    print("\nOption C: Manual Download")
    print("-" * 70)
    print("1. Go to: https://physionet.org/content/mimiciv/")
    print("2. Click 'Files' tab")
    print("3. Download files individually or as zip")
    print("4. Extract to: data/raw/mimic/")
    
    print("\n📋 STEP 5: Verify Download")
    print("-" * 70)
    print("After download, verify with:")
    print("  python scripts/verify_data.py")
    
    print("\n" + "="*70)
    print("Important Notes:")
    print("="*70)
    print("• MIMIC-IV is LARGE (~50+ GB compressed, ~100+ GB uncompressed)")
    print("• Download can take several hours depending on connection")
    print("• Ensure you have sufficient disk space")
    print("• The dataset contains de-identified patient data")
    print("• You must comply with the data use agreement")
    
    print("\n📁 Expected File Structure:")
    print("-" * 70)
    print("data/raw/mimic/")
    print("  ├── core/")
    print("  │   ├── patients.csv")
    print("  │   ├── admissions.csv")
    print("  │   └── ...")
    print("  ├── hosp/")
    print("  │   ├── diagnoses_icd.csv")
    print("  │   ├── labevents.csv")
    print("  │   └── ...")
    print("  └── icu/")
    print("      ├── icustays.csv")
    print("      └── ...")


def main():
    """Main function."""
    print("\n" + "="*70)
    print("MIMIC-IV Download Guide")
    print("="*70 + "\n")
    
    if check_mimic_access():
        print("\n✓ MIMIC-IV data is already available!")
        return
    
    print("MIMIC-IV requires credentialed access and cannot be downloaded automatically.")
    print("Follow the steps below to obtain access:\n")
    
    print_mimic_instructions()
    
    print("\n" + "="*70)
    print("Alternative: Use MIMIC-IV Demo Dataset")
    print("="*70)
    print("For testing purposes, you can use the demo dataset:")
    print("  https://physionet.org/content/mimiciv-demo/")
    print("  (No credentials required, but limited data)")


if __name__ == "__main__":
    main()



