# HF-Digital Twin Platform - API Documentation

**Version:** 0.1.0  
**Base URL:** `http://localhost:8000`  
**API Type:** RESTful JSON API  
**Authentication:** None (development mode)

---

## Table of Contents

1. [Overview](#overview)
2. [Base Endpoints](#base-endpoints)
3. [Recommendation Endpoints](#recommendation-endpoints)
4. [Document Processing Endpoints](#document-processing-endpoints)
5. [Request/Response Models](#requestresponse-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

The HF-Digital Twin Platform API provides programmatic access to personalized medication recommendations, treatment scenario comparisons, and document parsing capabilities. The API is built on FastAPI and follows RESTful principles.

### API Versioning

Current version: `v0.1.0`. Version information is included in response headers and the root endpoint.

### Content Types

- **Request:** `application/json`
- **Response:** `application/json`
- **File Upload:** `multipart/form-data`

### Response Format

All successful responses follow this structure:

```json
{
  "status": "success",
  "data": { ... },
  "metadata": { ... }
}
```

Error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Base Endpoints

### GET `/`

Root endpoint providing API information.

**Response:**
```json
{
  "message": "Patient Digital Twin API",
  "version": "0.1.0"
}
```

### GET `/health`

Health check endpoint for service availability.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET `/models`

List available trained models.

**Response:**
```json
{
  "models": [
    {
      "name": "baseline_xgboost",
      "version": "1.0"
    },
    {
      "name": "patient_digital_twin",
      "version": "0.1.0"
    }
  ]
}
```

---

## Recommendation Endpoints

### POST `/recommendations/medications`

Generate personalized medication recommendations for a patient.

**Request Body:**
```json
{
  "patient_info": {
    "age": 65,
    "sex": "M",
    "ejection_fraction": 0.35,
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "heart_rate": 75,
    "creatinine": 1.2,
    "sodium": 140,
    "cholesterol": 200,
    "diabetes": true,
    "high_blood_pressure": true,
    "high_cholesterol": false,
    "anaemia": false,
    "smoking": false
  },
  "current_medications": ["aspirin", "metformin"],
  "time_horizon_days": 90
}
```

**Patient Info Fields:**

| Field | Type | Required | Description | Range/Values |
|-------|------|----------|-------------|--------------|
| `age` | float | No | Patient age in years | > 0 |
| `sex` | string | No | Biological sex | "M", "F", "Male", "Female" |
| `gender` | string | No | Gender identity | Any string |
| `ejection_fraction` | float | No | Ejection fraction (0-1) | 0.0 - 1.0 |
| `systolic_bp` | float | No | Systolic blood pressure (mmHg) | > 0 |
| `diastolic_bp` | float | No | Diastolic blood pressure (mmHg) | > 0 |
| `heart_rate` | float | No | Heart rate (bpm) | > 0 |
| `creatinine` | float | No | Serum creatinine (mg/dL) | > 0 |
| `sodium` | float | No | Serum sodium (mEq/L) | > 0 |
| `cholesterol` | float | No | Total cholesterol (mg/dL) | > 0 |
| `diabetes` | boolean | No | Diabetes diagnosis | true/false |
| `high_blood_pressure` | boolean | No | Hypertension diagnosis | true/false |
| `hypertension` | boolean | No | Alternative hypertension field | true/false |
| `high_cholesterol` | boolean | No | Hyperlipidemia diagnosis | true/false |
| `anaemia` | boolean | No | Anemia diagnosis | true/false |
| `smoking` | boolean | No | Current smoking status | true/false |

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `patient_info` | object | Yes | - | Patient demographic, vital, and lab information |
| `current_medications` | array[string] | No | [] | List of current medications |
| `time_horizon_days` | integer | No | 90 | Prediction time horizon (1-365 days) |

**Response:**
```json
{
  "recommendations": [
    {
      "medication": "ace_inhibitor",
      "recommendation_score": 0.85,
      "is_safe": true,
      "interactions": [],
      "predicted_effect": {
        "ejection_fraction_change": 0.05,
        "mortality_risk_change": -0.10,
        "readmission_risk_change": -0.08,
        "time_horizon_days": 90
      },
      "expected_benefit": 0.75,
      "contraindications": []
    }
  ],
  "optimal_combination": {
    "medications": ["ace_inhibitor", "beta_blocker"],
    "expected_benefit": 0.88,
    "is_safe": true,
    "interactions": []
  },
  "baseline_prediction": {
    "ejection_fraction": 0.35,
    "mortality_risk": 0.25,
    "readmission_risk": 0.30
  },
  "summary": {
    "top_recommendation": {
      "medication": "ace_inhibitor",
      "score": 0.85
    },
    "total_recommendations": 5,
    "safe_recommendations": 4
  }
}
```

**Response Fields:**

- `recommendations`: Array of medication recommendations sorted by score (descending)
- `optimal_combination`: Best medication combination considering interactions
- `baseline_prediction`: Predicted outcomes without new medications
- `summary`: High-level summary of recommendations

**Status Codes:**

- `200`: Success
- `400`: Invalid request (missing required fields, invalid values)
- `500`: Internal server error
- `503`: Model not available (model not trained)

**Example cURL:**

```bash
curl -X POST "http://localhost:8000/recommendations/medications" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 65,
      "sex": "M",
      "ejection_fraction": 0.35,
      "systolic_bp": 140,
      "diabetes": true
    },
    "time_horizon_days": 90
  }'
```

---

### POST `/recommendations/compare-scenarios`

Compare multiple treatment scenarios side-by-side.

**Request Body:**
```json
{
  "patient_info": {
    "age": 65,
    "sex": "M",
    "ejection_fraction": 0.35,
    "systolic_bp": 140,
    "diabetes": true
  },
  "scenarios": [
    {
      "medications": ["ace_inhibitor", "beta_blocker"],
      "dosages": {
        "ace_inhibitor": 1.0,
        "beta_blocker": 1.0
      }
    },
    {
      "medications": ["arni", "beta_blocker"],
      "dosages": {
        "arni": 1.0,
        "beta_blocker": 1.0
      }
    }
  ]
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `patient_info` | object | Yes | Patient information (same as medications endpoint) |
| `scenarios` | array[object] | Yes | Array of treatment scenarios to compare |

**Scenario Object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `medications` | array[string] | Yes | List of medications in this scenario |
| `dosages` | object | No | Medication dosages (medication_name: dose) |

**Response:**
```json
[
  {
    "scenario_index": 0,
    "medications": ["ace_inhibitor", "beta_blocker"],
    "total_benefit": 0.88,
    "is_safe": true,
    "interactions": [],
    "effects": {
      "predicted_effects": {
        "ejection_fraction": 0.40,
        "mortality_risk": 0.15,
        "readmission_risk": 0.22
      }
    }
  },
  {
    "scenario_index": 1,
    "medications": ["arni", "beta_blocker"],
    "total_benefit": 0.92,
    "is_safe": true,
    "interactions": [],
    "effects": {
      "predicted_effects": {
        "ejection_fraction": 0.42,
        "mortality_risk": 0.12,
        "readmission_risk": 0.18
      }
    }
  }
]
```

**Response Fields:**

- Results are sorted by `total_benefit` (descending)
- Each scenario includes safety assessment and predicted effects
- Drug interactions are listed if present

**Status Codes:**

- `200`: Success
- `400`: Invalid request
- `500`: Internal server error

---

### GET `/recommendations/health`

Check recommendation service health and model availability.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

**Status Codes:**

- `200`: Service healthy
- `503`: Service unhealthy (model not loaded)

---

## Document Processing Endpoints

### POST `/documents/upload-prescription`

Upload and parse a prescription image or PDF.

**Request:**

- **Method:** POST
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: File (image or PDF)
  - `get_recommendations`: boolean (optional, default: false)

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Prescription image (JPG, PNG) or PDF |
| `get_recommendations` | boolean | No | Whether to generate medication recommendations based on parsed prescription |

**Supported File Types:**

- Images: JPG, JPEG, PNG
- Documents: PDF

**Response:**
```json
{
  "status": "success",
  "file_name": "prescription.jpg",
  "extracted_text": "Dr. Smith\nPatient: John Doe\n...",
  "parsed_prescription": {
    "patient_info": {
      "name": "John Doe",
      "age": 65
    },
    "medications": [
      {
        "name": "lisinopril",
        "dosage": "10mg",
        "frequency": "once daily",
        "instructions": "Take with food"
      }
    ],
    "prescriber": "Dr. Smith",
    "date": "2024-01-15"
  },
  "medications": ["lisinopril", "metformin"],
  "medication_details": [
    {
      "name": "lisinopril",
      "dosage": "10mg",
      "frequency": "once daily"
    }
  ],
  "recommendations": { ... }  // Only if get_recommendations=true
}
```

**Status Codes:**

- `200`: Success
- `400`: Invalid file format
- `500`: Processing error
- `503`: OCR not available

**Example cURL:**

```bash
curl -X POST "http://localhost:8000/documents/upload-prescription" \
  -F "file=@prescription.jpg" \
  -F "get_recommendations=true"
```

---

### POST `/documents/upload-lab-report`

Upload and parse a lab report image or PDF.

**Request:**

- **Method:** POST
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: File (image or PDF)
  - `get_recommendations`: boolean (optional, default: false)

**Response:**
```json
{
  "status": "success",
  "file_name": "lab_report.pdf",
  "extracted_text": "Lab Results\nPatient: John Doe\n...",
  "parsed_lab_report": {
    "patient_info": {
      "name": "John Doe"
    },
    "lab_values": {
      "creatinine": 1.2,
      "sodium": 140,
      "cholesterol": 200,
      "ejection_fraction": 0.35
    },
    "date": "2024-01-15"
  },
  "lab_values": {
    "creatinine": 1.2,
    "sodium": 140,
    "cholesterol": 200,
    "ejection_fraction": 0.35
  },
  "patient_features": {
    "creatinine": 1.2,
    "sodium": 140,
    "cholesterol": 200,
    "ejection_fraction": 0.35
  },
  "recommendations": { ... }  // Only if get_recommendations=true
}
```

**Status Codes:**

- `200`: Success
- `400`: Invalid file format
- `500`: Processing error
- `503`: OCR not available

---

### POST `/documents/extract-text`

Extract raw text from image or PDF without parsing.

**Request:**

- **Method:** POST
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: File (image or PDF)

**Response:**
```json
{
  "status": "success",
  "file_name": "document.jpg",
  "extracted_text": "Raw extracted text from OCR..."
}
```

---

### GET `/documents/health`

Check document processing service health.

**Response:**
```json
{
  "status": "healthy",
  "ocr_available": true,
  "prescription_parser_available": true,
  "lab_parser_available": true
}
```

---

## Request/Response Models

### PatientInfo Model

Complete patient information model used across endpoints.

```typescript
interface PatientInfo {
  // Demographics
  age?: number;
  sex?: string;  // "M", "F", "Male", "Female"
  gender?: string;
  
  // Vitals
  heart_rate?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  blood_pressure?: string;  // "120/80" format
  
  // Laboratory Values
  ejection_fraction?: number;  // 0.0 - 1.0
  creatinine?: number;  // mg/dL
  sodium?: number;  // mEq/L
  cholesterol?: number;  // mg/dL
  glucose?: number;  // mg/dL
  hemoglobin?: number;  // g/dL
  
  // Comorbidities
  diabetes?: boolean;
  high_blood_pressure?: boolean;
  hypertension?: boolean;
  high_cholesterol?: boolean;
  anaemia?: boolean;
  smoking?: boolean;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### Common Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `400` | Bad Request | Invalid input, missing required fields, invalid data types |
| `404` | Not Found | Endpoint does not exist |
| `500` | Internal Server Error | Server-side processing error |
| `503` | Service Unavailable | Model not loaded, OCR not available |

### Error Examples

**Missing Required Field:**
```json
{
  "detail": "patient_info is required",
  "status_code": 400
}
```

**Invalid Value:**
```json
{
  "detail": "ejection_fraction must be between 0.0 and 1.0",
  "status_code": 400
}
```

**Model Not Available:**
```json
{
  "detail": "Model not found. Please train the model first.",
  "status_code": 503
}
```

---

## Rate Limiting

Currently, no rate limiting is enforced. In production deployments, rate limiting should be configured based on:

- API key tier
- Endpoint complexity
- Resource usage

Recommended limits:
- `/recommendations/medications`: 100 requests/minute
- `/recommendations/compare-scenarios`: 50 requests/minute
- `/documents/*`: 20 requests/minute

---

## Examples

### Python Example

```python
import requests

# Medication recommendations
response = requests.post(
    "http://localhost:8000/recommendations/medications",
    json={
        "patient_info": {
            "age": 65,
            "sex": "M",
            "ejection_fraction": 0.35,
            "systolic_bp": 140,
            "diabetes": True
        },
        "time_horizon_days": 90
    }
)

recommendations = response.json()
print(f"Top recommendation: {recommendations['summary']['top_recommendation']['medication']}")

# Document upload
with open("prescription.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/documents/upload-prescription",
        files={"file": f},
        data={"get_recommendations": True}
    )
    
parsed = response.json()
print(f"Medications found: {parsed['medications']}")
```

### JavaScript Example

```javascript
// Medication recommendations
const response = await fetch('http://localhost:8000/recommendations/medications', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    patient_info: {
      age: 65,
      sex: 'M',
      ejection_fraction: 0.35,
      systolic_bp: 140,
      diabetes: true
    },
    time_horizon_days: 90
  })
});

const recommendations = await response.json();
console.log('Top recommendation:', recommendations.summary.top_recommendation.medication);

// Document upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('get_recommendations', 'true');

const uploadResponse = await fetch('http://localhost:8000/documents/upload-prescription', {
  method: 'POST',
  body: formData
});

const parsed = await uploadResponse.json();
console.log('Medications:', parsed.medications);
```

---

## Additional Resources

- **Interactive API Documentation:** Available at `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Documentation:** Available at `http://localhost:8000/redoc` (ReDoc)
- **Source Code:** See `pdt/api/` directory
- **Model Training:** See `scripts/train_medication_recommender.py`

---

**Last Updated:** December 2024  
**API Version:** 0.1.0  
**Maintainer:** HF-Digital Twin Platform Team

