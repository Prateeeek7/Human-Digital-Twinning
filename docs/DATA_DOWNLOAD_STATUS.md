# Data Download Status

## ✅ Successfully Downloaded

### 1. UCI Heart Failure Clinical Records Dataset
- **Status**: ✓ Downloaded
- **Location**: `data/raw/uci/heart_failure_clinical_records_dataset.csv`
- **Size**: 12 KB
- **Records**: 299 patients
- **Features**: 12 features + target (DEATH_EVENT)
- **Ready for training**: Yes

**Dataset Details:**
- Age, Anaemia, Creatinine Phosphokinase, Diabetes
- Ejection Fraction, High Blood Pressure, Platelets
- Serum Creatinine, Serum Sodium, Sex, Smoking
- Time (follow-up period), DEATH_EVENT (target)

## ⚠️ Requires Setup

### 2. Kaggle Datasets
- **Status**: Requires Kaggle API setup
- **Location**: `data/raw/kaggle/`

**To Download:**
1. Install Kaggle: `pip install kaggle`
2. Get API credentials from https://www.kaggle.com/settings
3. Place `kaggle.json` in `~/.kaggle/`
4. Run: `python scripts/download_kaggle_datasets.py`

**Recommended Datasets:**
- `dileep070/heart-disease-prediction`
- `fedesoriano/heart-failure-prediction`

### 3. MIMIC-IV Dataset
- **Status**: Requires credentialed access
- **Location**: `data/raw/mimic/`

**To Obtain:**
1. Complete CITI training: https://www.citiprogram.org/
2. Request access: https://physionet.org/content/mimiciv/
3. Sign data use agreement
4. Download and extract to `data/raw/mimic/`

**Note**: This is a large dataset (several GB) and requires institutional approval.

## 📊 Current Training Capability

With the UCI dataset, you can:
- ✅ Train baseline XGBoost model for mortality prediction
- ✅ Train time-series baseline models
- ✅ Test data pipeline and preprocessing
- ✅ Validate evaluation framework
- ⚠️ Limited by small dataset size (299 patients)

## 🚀 Next Steps

1. **Start with UCI dataset:**
   ```bash
   python scripts/train_baseline.py
   ```

2. **Set up Kaggle for more data:**
   ```bash
   python scripts/setup_kaggle.py
   python scripts/download_kaggle_datasets.py
   ```

3. **For production-grade training:**
   - Obtain MIMIC-IV access
   - Download additional PhysioNet datasets
   - Combine multiple datasets for robust training

## 📁 Data Directory Structure

```
data/
├── raw/
│   ├── uci/
│   │   └── heart_failure_clinical_records_dataset.csv ✓
│   ├── kaggle/ (empty - requires setup)
│   └── mimic/ (empty - requires access)
├── processed/ (will be created during training)
└── cache/ (will be created during training)
```

## ✅ Verification

Run verification script:
```bash
python scripts/verify_data.py
```

This will check all datasets and provide a summary of what's available for training.



