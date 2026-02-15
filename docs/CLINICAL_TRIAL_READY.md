# Clinical Trial Ready - Multi-Page PDF Extraction & Digital Twin System

## Overview

This system is designed for **first-stage clinical trials** and provides:

1. **Multi-page PDF processing** - Extract temporal medical data from 100s of pages
2. **Time-series data extraction** - Lab values and vitals with dates
3. **Clinical-grade database** - 100+ parameters with audit logging
4. **True Digital Twin** - Patient-specific calibration and learning

## Key Features

### 1. Temporal PDF Parser (`pdt/utils/temporal_pdf_parser.py`)

**Capabilities:**
- Processes PDFs with 100s of pages
- Extracts dates in multiple formats (MM/DD/YYYY, DD-MM-YYYY, written dates, relative dates)
- Links lab values to dates
- Extracts 50+ lab parameters
- Extracts vital signs with timestamps
- Validates values within clinical ranges
- Quality metrics for extraction

**Supported Lab Parameters:**
- Cardiac markers: EF, BNP, NT-proBNP, troponin, CK-MB
- Metabolic panel: Creatinine, eGFR, Na, K, Cl, HCO3, Glucose, BUN, Ca, P, Mg
- Complete blood count: Hb, Hct, WBC, RBC, Platelets, MCV, MCH, MCHC, RDW, differentials
- Lipid panel: Cholesterol, LDL, HDL, Triglycerides, Non-HDL
- Liver function: ALT, AST, Alk Phos, Bilirubin (total/direct/indirect), Albumin, Protein, PT, INR, aPTT
- Thyroid: TSH, T3, T4
- Inflammatory: CRP, ESR, Ferritin
- Other: Vitamin D, B12, Folate, CPK, LDH, Uric Acid, Lactate, Procalcitonin, D-Dimer

**Supported Vital Signs:**
- Blood pressure (systolic, diastolic)
- Heart rate
- Respiratory rate
- Temperature
- Oxygen saturation
- Weight
- BMI

### 2. Clinical Patient Database (`pdt/data/clinical_patient_database.py`)

**Schema:**
- **Patients table**: Demographics, baseline data, comorbidities, family history, social history
- **Lab values table**: Time-series lab values with timestamps, units, validation flags
- **Vital signs table**: Time-series vitals with timestamps
- **Medication history**: Medications with start/stop dates, dosages, frequencies
- **Clinical events**: Hospitalizations, procedures, events with dates
- **Predictions**: Model predictions with timestamps
- **Outcomes**: Observed outcomes for comparison
- **Calibrated parameters**: Patient-specific model parameters
- **Audit log**: Complete audit trail for clinical trial compliance
- **Documents**: Metadata for uploaded PDFs

**Features:**
- Bulk import of lab values and vitals
- Time-series queries with date ranges
- Data validation flags
- Audit logging for all operations
- Foreign key constraints for data integrity
- Indexed queries for performance

### 3. API Endpoints (`pdt/api/endpoints/temporal_data.py`)

**Endpoints:**

#### `POST /temporal-data/upload-pdf`
Upload multi-page PDF and extract temporal data.

**Parameters:**
- `file`: PDF file (can be 100s of pages)
- `patient_id`: Patient identifier (required if auto_import=True)
- `reference_date`: Reference date for relative dates (ISO format)
- `auto_import`: Automatically import to database (default: True)

**Response:**
```json
{
  "patient_id": "P001",
  "document_metadata": {
    "total_pages": 150,
    "primary_date": "2024-01-15T00:00:00",
    "date_range": {
      "earliest": "2023-10-01T00:00:00",
      "latest": "2024-01-15T00:00:00"
    }
  },
  "extraction_quality": {
    "total_lab_values_extracted": 450,
    "total_vitals_extracted": 120,
    "total_dates_found": 15,
    "date_coverage_labs": 0.95,
    "extraction_completeness": "high"
  },
  "lab_values_count": 450,
  "vitals_count": 120,
  "imported": true,
  "imported_counts": {
    "labs": 450,
    "vitals": 120
  }
}
```

#### `GET /temporal-data/patient/{patient_id}/labs`
Get time-series lab values for a patient.

**Query Parameters:**
- `lab_names`: Comma-separated list of lab names (optional)
- `start_date`: Start date filter (ISO format, optional)
- `end_date`: End date filter (ISO format, optional)

**Response:**
```json
{
  "patient_id": "P001",
  "lab_values": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "lab_name": "creatinine",
      "value": 1.2,
      "unit": "mg/dl",
      "flag": null,
      "validated": false
    }
  ],
  "count": 450,
  "date_range": {
    "earliest": "2023-10-01T00:00:00",
    "latest": "2024-01-15T00:00:00"
  }
}
```

#### `GET /temporal-data/patient/{patient_id}/vitals`
Get time-series vital signs for a patient.

#### `GET /temporal-data/patient/{patient_id}/summary`
Get comprehensive patient summary with data counts.

## Usage Examples

### 1. Upload Multi-Page PDF

```python
import requests

# Upload PDF
with open('patient_reports.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/temporal-data/upload-pdf',
        files={'file': f},
        data={
            'patient_id': 'P001',
            'auto_import': 'true',
            'reference_date': '2024-01-15T00:00:00'
        }
    )

result = response.json()
print(f"Extracted {result['lab_values_count']} lab values")
print(f"Extracted {result['vitals_count']} vital signs")
print(f"Quality: {result['extraction_quality']['extraction_completeness']}")
```

### 2. Query Time-Series Data

```python
# Get all creatinine values
response = requests.get(
    'http://localhost:8000/temporal-data/patient/P001/labs',
    params={'lab_names': 'creatinine'}
)

labs = response.json()
for lab in labs['lab_values']:
    print(f"{lab['timestamp']}: {lab['value']} {lab['unit']}")
```

### 3. Get Patient Summary

```python
response = requests.get(
    'http://localhost:8000/temporal-data/patient/P001/summary'
)

summary = response.json()
print(f"Total lab values: {summary['total_lab_values']}")
print(f"Date range: {summary['lab_date_range']}")
```

## Data Model

### Lab Values Structure
- **timestamp**: ISO format datetime
- **lab_name**: Standardized lab name (e.g., 'creatinine', 'ejection_fraction')
- **value**: Numeric value
- **unit**: Unit of measurement
- **flag**: Abnormal flag (if available)
- **validated**: Boolean flag for clinical validation
- **source**: Source of data (e.g., 'pdf_extraction')
- **page_number**: Page number in original PDF
- **extraction_context**: Context text from PDF

### Vital Signs Structure
- **timestamp**: ISO format datetime
- **vital_name**: Standardized vital name (e.g., 'systolic_bp', 'heart_rate')
- **value**: Numeric value
- **unit**: Unit of measurement
- **validated**: Boolean flag for clinical validation
- **source**: Source of data

## Clinical Validation

### Value Ranges
The system validates extracted values against clinical ranges:
- **Ejection Fraction**: 0.15 - 0.80
- **Creatinine**: 0.3 - 15.0 mg/dL
- **Sodium**: 100 - 160 mEq/L
- **Potassium**: 2.0 - 8.0 mEq/L
- **Glucose**: 40 - 600 mg/dL
- **Hemoglobin**: 5.0 - 25.0 g/dL
- And more...

Values outside these ranges are flagged but still stored.

### Data Quality Metrics
- **Date coverage**: Percentage of values with associated dates
- **Extraction completeness**: High/Medium/Low based on number of values extracted
- **Validation flags**: Track which values have been clinically validated

## Audit Logging

All database operations are logged in the `audit_log` table:
- User actions
- Table modifications
- Patient data access
- Timestamps
- Change details

This ensures compliance with clinical trial requirements.

## Performance Considerations

### PDF Processing
- **Tesseract OCR**: Faster, good for text-based PDFs
- **EasyOCR**: More accurate, slower (can be enabled with `use_easyocr=True`)
- **Page-by-page processing**: Handles large PDFs efficiently
- **Parallel processing**: Can be added for multiple PDFs

### Database
- **Indexed queries**: Fast time-series queries
- **Bulk inserts**: Efficient for large data imports
- **Foreign keys**: Data integrity
- **Connection pooling**: Can be added for production

## Clinical Trial Readiness

### Compliance Features
1. **Audit logging**: Complete trail of all operations
2. **Data validation**: Clinical range validation
3. **Data integrity**: Foreign key constraints
4. **Error handling**: Comprehensive error messages
5. **Documentation**: Complete API and data model documentation

### Next Steps for Full Clinical Trial
1. **User authentication**: Add user management and access control
2. **Data encryption**: Encrypt sensitive patient data
3. **HIPAA compliance**: Add required safeguards
4. **Clinical validation workflow**: Add review/approval process
5. **Export capabilities**: Export data for analysis
6. **Reporting**: Generate clinical trial reports

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Tesseract is installed
# macOS: brew install tesseract
# Linux: apt-get install tesseract-ocr
# Windows: Download from GitHub

# Initialize database (automatic on first use)
python -c "from pdt.data.clinical_patient_database import ClinicalPatientDatabase; ClinicalPatientDatabase()"
```

## Testing

```bash
# Test PDF parsing
python -c "
from pdt.utils.temporal_pdf_parser import TemporalPDFParser
parser = TemporalPDFParser()
result = parser.parse_multi_page_pdf('test_report.pdf')
print(f'Extracted {len(result[\"temporal_lab_values\"])} lab values')
"

# Test database
python -c "
from pdt.data.clinical_patient_database import ClinicalPatientDatabase
db = ClinicalPatientDatabase()
print('Database initialized successfully')
"
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For clinical trial support, contact the development team.
