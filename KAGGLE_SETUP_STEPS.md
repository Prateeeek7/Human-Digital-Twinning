# Kaggle Dataset Download - Step by Step

## Complete Instructions (5 minutes)

### Step 1: Get Kaggle API Token

1. **Open your browser** and go to: **https://www.kaggle.com/**
2. **Sign in** (or create a free account if needed)
3. **Go to Account Settings**: https://www.kaggle.com/settings
4. **Scroll down** to the "API" section
5. **Click "Create New API Token"** button
   - This will automatically download a file called `kaggle.json`
   - The file will be in your Downloads folder

### Step 2: Set Up Credentials on Your Computer

**Option A: Using the Helper Script (Easiest)**

After downloading `kaggle.json`, just run:
```bash
bash scripts/kaggle_setup_helper.sh
```

**Option B: Manual Setup**

Run these commands in your terminal:

```bash
# 1. Create the Kaggle directory (if it doesn't exist)
mkdir -p ~/.kaggle

# 2. Move the downloaded file to the correct location
mv ~/Downloads/kaggle.json ~/.kaggle/

# 3. Set proper permissions (required for security)
chmod 600 ~/.kaggle/kaggle.json

# 4. Verify it worked
ls -la ~/.kaggle/kaggle.json
```

You should see output like:
```
-rw-------  1 yourname  staff  65 Dec 21 19:00 /Users/yourname/.kaggle/kaggle.json
```

### Step 3: Verify Setup

Check if everything is set up correctly:

```bash
python -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✓ Kaggle API authenticated successfully!')"
```

If you see "✓ Kaggle API authenticated successfully!", you're ready!

### Step 4: Download Datasets

Now download the heart failure datasets:

```bash
python scripts/download_all_datasets.py
```

Or download specific datasets:

```bash
# Install kaggle package if needed
pip install kaggle

# Download specific datasets
python -c "
from kaggle.api.kaggle_api_extended import KaggleApi
import os
os.makedirs('data/raw/kaggle', exist_ok=True)
api = KaggleApi()
api.authenticate()
api.dataset_download_files('fedesoriano/heart-failure-prediction', path='data/raw/kaggle', unzip=True)
print('✓ Downloaded heart-failure-prediction')
"
```

### Step 5: Verify Downloads

Check what was downloaded:

```bash
python scripts/verify_data.py
```

Or manually check:

```bash
ls -lh data/raw/kaggle/
```

## Recommended Kaggle Datasets

1. **fedesoriano/heart-failure-prediction**
   - Good for heart failure prediction
   - Multiple features

2. **dileep070/heart-disease-prediction**
   - Heart disease dataset
   - Useful for training

## Troubleshooting

### Error: "Could not find kaggle.json"
- Make sure the file is at `~/.kaggle/kaggle.json`
- Check: `ls -la ~/.kaggle/kaggle.json`

### Error: "403 Forbidden"
- You need to accept the dataset terms on Kaggle first
- Visit the dataset page on Kaggle and click "I understand and accept"

### Error: "401 Unauthorized"
- Your API token might be invalid
- Generate a new token from https://www.kaggle.com/settings

## Quick Checklist

- [ ] Downloaded `kaggle.json` from Kaggle
- [ ] Moved file to `~/.kaggle/kaggle.json`
- [ ] Set permissions: `chmod 600 ~/.kaggle/kaggle.json`
- [ ] Verified authentication works
- [ ] Downloaded datasets
- [ ] Verified data is in `data/raw/kaggle/`

## Next Steps

After downloading:
1. Verify data: `python scripts/verify_data.py`
2. Start training with the new datasets
3. Combine with UCI dataset for better model performance



