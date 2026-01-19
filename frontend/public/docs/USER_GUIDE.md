# HF-Digital Twin Platform - User Guide

**Version:** 0.1.0  
**Last Updated:** December 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Medication Recommendations](#medication-recommendations)
5. [Document Upload & Parsing](#document-upload--parsing)
6. [Treatment Scenario Comparison](#treatment-scenario-comparison)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

The HF-Digital Twin Platform is a hospital-grade AI system designed to provide personalized medication recommendations for heart failure patients. The platform combines machine learning models trained on 253,680+ patient records with clinical guidelines to deliver evidence-based treatment recommendations.

### Key Features

- **Personalized Medication Recommendations:** AI-powered recommendations based on patient characteristics
- **Document Parsing:** Automatic extraction from prescriptions and lab reports using OCR
- **Treatment Comparison:** Side-by-side comparison of multiple treatment scenarios
- **Drug Interaction Checking:** Automatic validation of medication safety
- **Trajectory Forecasting:** Prediction of patient outcomes over time

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for API access
- JavaScript enabled

---

## Getting Started

### Accessing the Platform

1. Navigate to the platform URL (typically `http://localhost:3000` for local development)
2. The dashboard will load automatically
3. No login required for development mode

### First Steps

1. **Review the Dashboard:** Familiarize yourself with system statistics and quick actions
2. **Try Recommendations:** Enter sample patient data to see recommendations
3. **Upload Documents:** Test document parsing with sample prescriptions or lab reports
4. **Compare Scenarios:** Create multiple treatment scenarios to compare outcomes

---

## Dashboard Overview

The dashboard provides an overview of the system and quick access to key features.

### Statistics Panel

- **Patients in Database:** Total number of patients used for training (253,680+)
- **Recommendations Generated:** Count of recommendations created
- **Documents Processed:** Number of documents parsed
- **Average Accuracy:** Model performance metrics

### Quick Actions

Four main sections accessible from the dashboard:

1. **Recommendations:** Get personalized medication recommendations
2. **Upload Documents:** Process prescriptions and lab reports
3. **Compare Treatments:** Compare multiple treatment scenarios
4. **Dashboard:** Return to this overview page

---

## Medication Recommendations

### Purpose

Generate personalized medication recommendations based on patient demographics, vitals, lab values, and medical history.

### Step-by-Step Process

#### 1. Navigate to Recommendations

Click "Recommendations" in the navigation menu or from the dashboard quick actions.

#### 2. Enter Patient Information

Fill in the patient information form. Fields are organized into sections:

**Demographics:**
- **Age:** Patient age in years
- **Sex:** Biological sex (M/F)

**Vital Signs:**
- **Heart Rate:** Beats per minute (bpm)
- **Systolic BP:** Systolic blood pressure (mmHg)
- **Diastolic BP:** Diastolic blood pressure (mmHg)

**Laboratory Values:**
- **Ejection Fraction:** Heart's pumping efficiency (0-100%, entered as percentage)
- **Creatinine:** Kidney function marker (mg/dL)
- **Sodium:** Electrolyte level (mEq/L)
- **Cholesterol:** Total cholesterol (mg/dL)
- **Glucose:** Blood sugar level (mg/dL)
- **Hemoglobin:** Blood oxygen carrier (g/dL)

**Medical History:**
- Checkboxes for common conditions:
  - Diabetes
  - High Blood Pressure
  - High Cholesterol
  - Anaemia
  - Smoking

**Current Medications:**
- Add current medications using the "Add Medication" button
- Medications are displayed as tags that can be removed

#### 3. Set Prediction Horizon

- **Time Horizon:** Select prediction timeframe (default: 90 days)
- Range: 1-365 days
- Longer horizons provide more comprehensive trajectory predictions

#### 4. Generate Recommendations

Click the "Get Recommendations" button. The system will:

1. Validate input data
2. Extract patient features
3. Generate medication recommendations
4. Check for drug interactions
5. Predict treatment effects
6. Calculate expected benefits

#### 5. Review Results

Results are displayed in several sections:

**Top Recommendation:**
- Highest-scoring medication
- Safety status (Safe/Unsafe)
- Recommendation score
- Expected benefits

**All Recommendations:**
- List of all recommended medications
- Sorted by recommendation score
- Each includes:
  - Medication name
  - Recommendation score
  - Safety status
  - Predicted effects
  - Expected benefits

**Optimal Combination:**
- Best medication combination
- Considers drug interactions
- Maximum expected benefit

**Predicted Outcomes:**
- Baseline predictions (without new medications)
- Predicted changes with recommended medications
- Metrics include:
  - Ejection fraction improvement
  - Mortality risk reduction
  - Readmission risk reduction

### Understanding Results

**Recommendation Score:**
- Range: 0.0 - 1.0
- Higher scores indicate better fit for the patient
- Based on patient characteristics and clinical evidence

**Safety Status:**
- **Safe:** No severe interactions detected
- **Unsafe:** Drug interactions or contraindications present
- Review interactions list for details

**Expected Benefits:**
- Quantified improvement in patient outcomes
- Based on predicted treatment effects
- Higher values indicate greater expected improvement

### Example Use Case

**Scenario:** 65-year-old male with heart failure, ejection fraction 35%, diabetes, and hypertension.

**Input:**
- Age: 65
- Sex: M
- Ejection Fraction: 35%
- Systolic BP: 140
- Diabetes: Yes
- High Blood Pressure: Yes
- Current Medications: None

**Expected Output:**
- Top recommendation: ACE Inhibitor
- Score: 0.85
- Safety: Safe
- Expected EF improvement: +5%
- Mortality risk reduction: -10%

---

## Document Upload & Parsing

### Purpose

Automatically extract information from prescription images/PDFs and lab reports using OCR technology.

### Supported File Formats

- **Images:** JPG, JPEG, PNG
- **Documents:** PDF
- **Maximum File Size:** 10 MB (recommended)

### Step-by-Step Process

#### 1. Navigate to Documents

Click "Documents" in the navigation menu.

#### 2. Select Document Type

Choose the type of document you're uploading:

- **Prescription:** For medication prescriptions
- **Lab Report:** For laboratory test results

#### 3. Upload File

**Option A: Drag and Drop**
- Drag file from your computer into the upload area
- File will be highlighted when ready

**Option B: Click to Browse**
- Click the upload area
- Select file from file browser

#### 4. Process Document

Click "Upload & Parse" button. The system will:

1. Upload file to server
2. Extract text using OCR
3. Parse document structure
4. Extract relevant information
5. Optionally generate recommendations

#### 5. Review Parsed Results

**For Prescriptions:**
- **Patient Information:** Name, age (if available)
- **Medications:** List of prescribed medications
- **Medication Details:** Dosage, frequency, instructions
- **Prescriber:** Doctor name
- **Date:** Prescription date

**For Lab Reports:**
- **Patient Information:** Name (if available)
- **Lab Values:** Extracted laboratory results
  - Creatinine
  - Sodium
  - Cholesterol
  - Ejection Fraction
  - Other values found
- **Date:** Report date

**Extracted Text:**
- Raw OCR text for verification
- Can be used to verify parsing accuracy

#### 6. Get Recommendations (Optional)

If "Get Recommendations" is enabled:

- System uses parsed patient information
- Generates medication recommendations
- Uses extracted lab values as patient features

### Tips for Best Results

**Image Quality:**
- Use high-resolution images (300 DPI or higher)
- Ensure good lighting and contrast
- Avoid blurry or skewed images
- Remove shadows and reflections

**PDF Quality:**
- Use text-based PDFs (not scanned images)
- Ensure PDFs are not password-protected
- Verify text is selectable

**Document Format:**
- Standard prescription formats work best
- Clear, typed text is more accurate than handwriting
- Structured lab reports parse better than free-form text

### Common Issues

**Low OCR Accuracy:**
- Improve image quality
- Use higher resolution
- Ensure proper lighting

**Missing Information:**
- Some fields may not be present in document
- System will use available information
- Manual entry may be needed for missing fields

**Parsing Errors:**
- Review extracted text
- Verify medication names are correct
- Check dosage and frequency accuracy

---

## Treatment Scenario Comparison

### Purpose

Compare multiple treatment scenarios side-by-side to identify the optimal medication combination.

### Step-by-Step Process

#### 1. Navigate to Comparison

Click "Comparison" in the navigation menu.

#### 2. Enter Patient Information

Fill in patient demographics, vitals, and lab values (same as Recommendations page).

#### 3. Create Treatment Scenarios

**Default Scenarios:**
- Two default scenarios are pre-loaded
- Can be modified or removed

**Add Scenario:**
- Click "Add New Scenario" button
- New scenario card appears

**Add Medications to Scenario:**
- Click "Add Medication" in scenario card
- Enter medication name (e.g., "ace_inhibitor")
- Medication appears as tag
- Can add multiple medications per scenario

**Remove Medications:**
- Click "×" on medication tag to remove

**Remove Scenario:**
- Click "×" button on scenario header
- Minimum one scenario required

#### 4. Compare Scenarios

Click "Compare Scenarios" button. The system will:

1. Validate patient information
2. Evaluate each scenario
3. Predict outcomes for each
4. Check drug interactions
5. Calculate expected benefits
6. Rank scenarios by benefit

#### 5. Review Comparison Results

**Summary:**
- Number of scenarios compared
- Best scenario identified

**Comparison Chart:**
- Bar chart showing total benefit for each scenario
- Visual comparison of outcomes

**Individual Scenario Results:**

Each scenario displays:

- **Medications:** List of medications in scenario
- **Total Benefit:** Overall expected benefit score
- **Safety Status:** Safe/Unsafe with interaction details
- **Predicted Effects:**
  - Ejection fraction change
  - Mortality risk change
  - Readmission risk change
- **Best Option Badge:** Highlighted on optimal scenario

**Drug Interactions:**
- Listed if present
- Severity level (Severe, Moderate, Mild)
- Recommended actions

### Interpreting Results

**Total Benefit:**
- Higher values indicate better expected outcomes
- Considers multiple factors:
  - Ejection fraction improvement
  - Risk reduction
  - Safety profile

**Best Option:**
- Scenario with highest total benefit
- Marked with "Best Option" badge
- Consider safety and interactions

**Safety Assessment:**
- Review all interactions
- Severe interactions require attention
- May need dosage adjustments or alternative medications

### Example Use Case

**Scenario:** Compare ACE inhibitor vs. ARNI for heart failure patient.

**Patient:**
- Age: 65, Male
- EF: 35%
- Diabetes: Yes
- Current: Beta blocker

**Scenarios:**
1. ACE Inhibitor + Beta Blocker
2. ARNI + Beta Blocker

**Expected Results:**
- Scenario 2 (ARNI) may show higher benefit
- Both scenarios safe
- ARNI may show better EF improvement

---

## Best Practices

### Data Entry

1. **Complete Information:** Provide as much patient data as possible for better recommendations
2. **Accurate Values:** Ensure lab values and vitals are current and accurate
3. **Current Medications:** List all current medications to avoid interactions
4. **Regular Updates:** Update patient information as conditions change

### Using Recommendations

1. **Review All Options:** Don't rely solely on top recommendation
2. **Check Interactions:** Always review drug interaction warnings
3. **Consider Context:** Recommendations are evidence-based but require clinical judgment
4. **Monitor Outcomes:** Track patient response and adjust as needed

### Document Processing

1. **Quality First:** Use high-quality images for better OCR accuracy
2. **Verify Results:** Always review parsed information for accuracy
3. **Manual Correction:** Correct any parsing errors before using data
4. **Privacy:** Ensure patient privacy when uploading documents

### Treatment Comparison

1. **Multiple Scenarios:** Compare at least 2-3 scenarios
2. **Consider Safety:** Don't choose highest benefit if safety concerns exist
3. **Patient Factors:** Consider patient-specific factors not captured in data
4. **Clinical Guidelines:** Align with established clinical guidelines

---

## Troubleshooting

### Recommendations Not Loading

**Symptoms:** Recommendations page doesn't load or shows error

**Solutions:**
1. Check API server is running (`http://localhost:8000`)
2. Verify model is trained (`models/personalized_medication_recommender.pkl` exists)
3. Check browser console for errors
4. Refresh page

### Document Upload Fails

**Symptoms:** File upload fails or shows error

**Solutions:**
1. Check file size (should be < 10 MB)
2. Verify file format (JPG, PNG, PDF)
3. Check OCR dependencies are installed
4. Try different file
5. Check server logs for detailed error

### Parsing Inaccurate

**Symptoms:** Extracted information is incorrect

**Solutions:**
1. Improve image quality
2. Use higher resolution
3. Ensure good lighting
4. Try different file format
5. Manually correct parsed data

### Comparison Not Working

**Symptoms:** Scenario comparison fails

**Solutions:**
1. Verify patient information is complete
2. Check at least one scenario has medications
3. Ensure API server is running
4. Check browser console for errors

### Slow Performance

**Symptoms:** System is slow to respond

**Solutions:**
1. Check API server resources
2. Reduce file sizes for document upload
3. Limit number of scenarios in comparison
4. Check network connection

---

## FAQ

### General Questions

**Q: Is this system a replacement for clinical judgment?**  
A: No. The platform provides evidence-based recommendations but should be used as a decision support tool alongside clinical expertise.

**Q: What data is used for training?**  
A: The system is trained on 253,680+ de-identified patient records from multiple sources including UCI, Kaggle, and MIMIC-IV datasets.

**Q: How accurate are the recommendations?**  
A: Model performance varies by medication and patient population. Average AUROC is approximately 0.80. Individual recommendations should be validated clinically.

**Q: Is patient data stored?**  
A: In development mode, data is processed but not permanently stored. In production, data handling follows HIPAA and local privacy regulations.

### Technical Questions

**Q: What browsers are supported?**  
A: Modern browsers including Chrome, Firefox, Safari, and Edge. JavaScript must be enabled.

**Q: Can I use the API programmatically?**  
A: Yes. See API Documentation for details on REST API endpoints.

**Q: How do I train the models?**  
A: See Technical Documentation for model training procedures.

**Q: What file formats are supported for documents?**  
A: Images (JPG, PNG) and PDFs. Maximum recommended size is 10 MB.

### Clinical Questions

**Q: Are drug interactions checked?**  
A: Yes. The system checks for drug-drug interactions and contraindications before recommending medications.

**Q: How are recommendations generated?**  
A: Recommendations are based on patient characteristics, clinical evidence from training data, and established guidelines for heart failure management.

**Q: Can I customize recommendations?**  
A: The system provides evidence-based recommendations. Clinical judgment should be applied to customize for individual patients.

**Q: What medications are supported?**  
A: The system supports common heart failure medications including ACE inhibitors, ARNIs, beta blockers, diuretics, and others. See model training data for complete list.

---

## Support

For technical support or questions:

- **Email:** support@pdt.com
- **Documentation:** See Technical Documentation and API Documentation
- **Issues:** Report bugs or request features through project repository

---

**Last Updated:** December 2024  
**Version:** 0.1.0  
**Platform:** HF-Digital Twin Platform

