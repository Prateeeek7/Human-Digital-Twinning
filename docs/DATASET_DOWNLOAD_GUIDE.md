# Complete Dataset Download Guide

This guide will help you download all datasets needed for training the Patient Digital Twin model.

## Current Status

- ✅ **UCI Heart Failure Dataset**: Downloaded and ready
- ⚠️ **Kaggle Datasets**: Requires API setup
- ⚠️ **MIMIC-IV**: Requires credentialed access

---

## Part 1: Kaggle Datasets

### Step 1: Install Kaggle Package

```bash
pip install kaggle
```

### Step 2: Get Kaggle API Credentials

1. **Go to Kaggle**: https://www.kaggle.com/
2. **Sign in** (or create an account if you don't have one)
3. **Go to Account Settings**: https://www.kaggle.com/settings
4. **Scroll to 'API' section**
5. **Click 'Create New API Token'**
   - This downloads a file called `kaggle.json`

### Step 3: Set Up Credentials

**On Mac/Linux:**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.kaggle

# Move the downloaded kaggle.json file
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set proper permissions (required)
chmod 600 ~/.kaggle/kaggle.json
```

**On Windows:**
1. Create folder: `C:\Users\<YourUsername>\.kaggle\`
2. Move `kaggle.json` to that folder

### Step 4: Download Datasets

Once credentials are set up, run:

```bash
python scripts/download_all_datasets.py
```

Or download specific datasets:

```bash
python scripts/download_kaggle_datasets.py
```

**Recommended Kaggle Datasets:**
- `fedesoriano/heart-failure-prediction`
- `dileep070/heart-disease-prediction`

**Note**: You may need to accept dataset terms on Kaggle first by visiting the dataset page.

---

## Part 2: MIMIC-IV Dataset

MIMIC-IV requires credentialed access and cannot be downloaded automatically. Follow these steps:

### Step 1: Complete CITI Training

1. **Go to**: https://www.citiprogram.org/
2. **Register** for an account
3. **Complete the course**: "Data or Specimens Only Research"
   - This typically takes 2-4 hours
4. **Download** your completion certificate

### Step 2: Create PhysioNet Account

1. **Go to**: https://physionet.org/
2. **Sign up** and create an account
3. **Verify** your email address

### Step 3: Request MIMIC-IV Access

1. **Go to**: https://physionet.org/content/mimiciv/
2. **Click** "Request access" or "Sign the data use agreement"
3. **Upload** your CITI completion certificate
4. **Sign** the data use agreement
5. **Wait** for approval (usually 1-3 business days)

### Step 4: Download MIMIC-IV

Once approved, you have three options:

#### Option A: Using wget (Recommended)

```bash
cd data/raw/mimic
wget -r -N -c -np --user YOUR_USERNAME --password YOUR_PASSWORD \
     https://physionet.org/files/mimiciv/2.2/
```

#### Option B: Using Python Package

```bash
pip install physionet-download
```

Then in Python:
```python
from physionet_download import download_physionet_files

download_physionet_files(
    project_name='mimiciv',
    output_dir='data/raw/mimic',
    version='2.2'
)
```

#### Option C: Manual Download

1. Go to: https://physionet.org/content/mimiciv/
2. Click "Files" tab
3. Download files individually or as zip
4. Extract to: `data/raw/mimic/`

### Important Notes for MIMIC-IV

- **Size**: ~50+ GB compressed, ~100+ GB uncompressed
- **Time**: Download can take several hours
- **Space**: Ensure you have sufficient disk space
- **Compliance**: You must comply with the data use agreement

### Expected File Structure

```
data/raw/mimic/
├── core/
│   ├── patients.csv
│   ├── admissions.csv
│   └── ...
├── hosp/
│   ├── diagnoses_icd.csv
│   ├── labevents.csv
│   └── ...
└── icu/
    ├── icustays.csv
    └── ...
```

---

## Part 3: Alternative - MIMIC-IV Demo

For testing purposes, you can use the demo dataset (no credentials required):

```bash
# Download demo dataset
wget -r -N -c -np https://physionet.org/files/mimiciv-demo/1.0/ -P data/raw/mimic-demo/
```

**Note**: Demo dataset has limited data but is useful for testing the pipeline.

---

## Verification

After downloading datasets, verify them:

```bash
python scripts/verify_data.py
```

This will show:
- Which datasets are available
- Number of records
- File sizes
- Ready status for training

---

## Quick Reference

### All-in-One Script

```bash
# This will attempt to download everything available
python scripts/download_all_datasets.py
```

### Individual Scripts

```bash
# UCI dataset (already done)
python scripts/download_data.py

# Kaggle setup guide
python scripts/setup_kaggle.py

# MIMIC-IV guide
python scripts/download_mimic_guide.py

# Verify all data
python scripts/verify_data.py
```

---

## Troubleshooting

### Kaggle Issues

**Error: "Could not find kaggle.json"**
- Make sure the file is in `~/.kaggle/kaggle.json`
- Check file permissions: `chmod 600 ~/.kaggle/kaggle.json`

**Error: "403 Forbidden"**
- Accept the dataset terms on Kaggle website first
- Visit the dataset page and click "I understand and accept"

### MIMIC-IV Issues

**Error: "Access Denied"**
- Make sure you've completed CITI training
- Verify your PhysioNet account is approved
- Check that you've signed the data use agreement

**Download is slow**
- MIMIC-IV is very large, this is normal
- Consider downloading during off-peak hours
- Use wget with resume capability (`-c` flag)

---

## Next Steps

Once datasets are downloaded:

1. **Verify data**: `python scripts/verify_data.py`
2. **Start training**: Create training scripts using the data loaders
3. **Check data loaders**: Test with `pdt.data.loaders`

For more information, see:
- `QUICK_START.md` - Quick start guide
- `DATA_DOWNLOAD_STATUS.md` - Current status
- `README.md` - Project overview



