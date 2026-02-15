# Drug/Medication Data Sources for Patient Digital Twin

## Why Drug Data is Important

For a Patient Digital Twin focused on heart failure, drug/medication data enables:
- **Treatment Simulation**: Predict effects of medication changes
- **Drug Interactions**: Identify potential adverse interactions
- **Dosage Optimization**: Find optimal medication dosages
- **Treatment Outcomes**: Predict patient response to medications

## Available Sources

### 1. MIMIC-IV (BEST SOURCE - Requires Access) ⭐

**Why it's the best:**
- Real-world hospital medication data
- Heart failure patient prescriptions
- Dosage, timing, administration routes
- Combined with patient outcomes

**How to get:**
1. Complete CITI training
2. Request access via PhysioNet
3. Download `prescriptions.csv` table
4. Contains: drug names, dosages, routes, frequencies

**Location in MIMIC-IV:**
- Table: `prescriptions.csv`
- Links to: `patients.csv`, `admissions.csv`
- Includes: medication start/stop times

### 2. DrugBank Database (Free with Registration)

**Website**: https://go.drugbank.com/

**What it provides:**
- Drug properties and mechanisms
- Drug-drug interactions
- Targets and pathways
- Pharmacokinetics data

**How to use:**
1. Register for free account
2. Download structured data
3. Integrate with patient data for drug effect modeling

### 3. FDA Drug Databases

**Sources:**
- **OpenFDA**: https://open.fda.gov/
- **Drugs@FDA**: https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files

**What it provides:**
- Drug approvals and labeling
- Adverse event reports
- Drug interactions
- Safety information

### 4. UCI Drug Consumption Dataset

**Link**: https://archive.ics.uci.edu/ml/datasets/Drug+consumption+(quantified)

**What it provides:**
- Drug usage patterns
- Individual drug responses
- Demographics and drug use

### 5. Clinical Trial Data

**ClinicalTrials.gov**: https://clinicaltrials.gov/

**What it provides:**
- Medication outcomes from trials
- Heart failure treatment studies
- Drug efficacy data

**Access**: Public API available

## Heart Failure Specific Medications

For heart failure treatment, key medications include:

1. **ACE Inhibitors** (e.g., Lisinopril, Enalapril)
2. **ARBs** (e.g., Losartan, Valsartan)
3. **ARNI** (Sacubitril/Valsartan)
4. **Beta-Blockers** (e.g., Metoprolol, Carvedilol)
5. **Diuretics** (e.g., Furosemide)
6. **Aldosterone Antagonists** (e.g., Spironolactone)
7. **Digoxin**
8. **Anticoagulants** (e.g., Warfarin)

## Integration Strategy

### Phase 1: Use Existing Data
- Check if current datasets have medication columns
- Extract medication information from patient records

### Phase 2: Add DrugBank Data
- Download DrugBank database
- Map medications to properties
- Add interaction data

### Phase 3: MIMIC-IV (When Available)
- Extract prescription data
- Link to patient outcomes
- Build treatment effect models

## Current Status

**Downloaded:**
- Drug classification dataset (if available from Kaggle)

**Recommended Next Steps:**
1. **Immediate**: Download DrugBank data (free, no credentials needed)
2. **Short-term**: Get MIMIC-IV access for real prescription data
3. **Long-term**: Integrate multiple sources for comprehensive drug modeling

## Quick Start: Download DrugBank

```bash
# DrugBank requires manual download
# 1. Go to: https://go.drugbank.com/
# 2. Register for free account
# 3. Download structured data files
# 4. Place in: data/raw/drugs/drugbank/
```

## For Treatment Simulation

The Patient Digital Twin's treatment simulator (`pdt/models/treatment/treatment_simulator.py`) can use:
- Drug properties from DrugBank
- Real prescription patterns from MIMIC-IV
- Clinical trial outcomes
- Drug interaction data

This enables realistic "what-if" scenarios for medication changes.



