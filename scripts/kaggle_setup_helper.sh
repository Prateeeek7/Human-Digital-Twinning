#!/bin/bash

echo "=========================================="
echo "Kaggle Setup Helper"
echo "=========================================="
echo ""

# Check if kaggle.json exists in Downloads
if [ -f ~/Downloads/kaggle.json ]; then
    echo "✓ Found kaggle.json in Downloads folder"
    echo ""
    echo "Moving to ~/.kaggle/..."
    mkdir -p ~/.kaggle
    mv ~/Downloads/kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    echo "✓ Setup complete!"
    echo ""
    echo "Verifying..."
    ls -la ~/.kaggle/kaggle.json
    echo ""
    echo "✓ Ready to download datasets!"
else
    echo "✗ kaggle.json not found in Downloads folder"
    echo ""
    echo "Please:"
    echo "1. Go to https://www.kaggle.com/settings"
    echo "2. Click 'Create New API Token'"
    echo "3. This downloads kaggle.json to your Downloads folder"
    echo "4. Run this script again: bash scripts/kaggle_setup_helper.sh"
fi



