# Backend-Frontend Feature Mapping

## ✅ Features with Frontend Implementation

### 1. Recommendations API (`/recommendations`)
- ✅ **`POST /recommendations/medications`** → `Recommendations.tsx`
- ✅ **`POST /recommendations/compare-scenarios`** → `TreatmentComparison.tsx` (via enhanced endpoint)

### 2. Documents API (`/documents`)
- ✅ **`POST /documents/upload-prescription`** → `DocumentUpload.tsx`
- ✅ **`POST /documents/upload-lab-report`** → `DocumentUpload.tsx`
- ✅ **`POST /documents/extract-text`** → `DocumentUpload.tsx`

### 3. Medications API (`/medications`) - Partial
- ✅ **`GET /medications/search`** → Used in `TreatmentComparison.tsx` (search functionality)
- ✅ **`POST /medications/recommendations/enhanced`** → `Recommendations.tsx` (enhanced mode)
- ✅ **`POST /medications/predict-combination`** → `recommendationsApi.predictCombination()` (in API service)
- ✅ **`POST /medications/compare-combinations`** → `TreatmentComparison.tsx`
- ⚠️ **`GET /medications/category/{category}`** → API service exists, but no dedicated UI
- ⚠️ **`GET /medications/{medication_name}`** → API service exists, but no dedicated UI
- ⚠️ **`POST /medications/load-hf-medications`** → API service exists, but no UI button/page

---

## ❌ Missing Frontend Implementations

### 1. Digital Twin API (`/digital-twin`) - **NO FRONTEND**
Missing endpoints:
- ❌ **`POST /digital-twin/initialize`** - Initialize patient digital twin
- ❌ **`POST /digital-twin/recommendations`** - Get digital twin recommendations
- ❌ **`POST /digital-twin/update-outcome`** - Update digital twin with observed outcomes
- ❌ **`GET /digital-twin/status/{patient_id}`** - Get digital twin status
- ❌ **`POST /digital-twin/history`** - Add patient history entry
- ❌ **`GET /digital-twin/history/{patient_id}`** - Get patient history

**Required Frontend:**
- New page: `DigitalTwin.tsx` or `PatientManagement.tsx`
- Features needed:
  - Patient initialization form
  - Digital twin status dashboard
  - History entry form
  - Outcome tracking/updates
  - Calibration status display

### 2. Temporal Data API (`/temporal-data`) - **NO FRONTEND**
Missing endpoints:
- ❌ **`POST /temporal-data/upload-pdf`** - Upload multi-page PDF for temporal extraction
- ❌ **`GET /temporal-data/patient/{patient_id}/labs`** - Get time-series lab values
- ❌ **`GET /temporal-data/patient/{patient_id}/vitals`** - Get time-series vitals
- ❌ **`GET /temporal-data/patient/{patient_id}/summary`** - Get patient temporal summary

**Required Frontend:**
- New page: `TemporalData.tsx` or `PatientHistory.tsx`
- Features needed:
  - Multi-page PDF upload interface
  - Time-series lab values visualization (charts)
  - Time-series vitals visualization (charts)
  - Patient summary dashboard
  - Date range filtering
  - Lab/vital name filtering

### 3. Main API Endpoints - **NO FRONTEND**
Missing endpoints:
- ❌ **`POST /predict`** - Predict patient outcomes
- ❌ **`POST /trajectory`** - Predict patient trajectory
- ❌ **`POST /treatment/simulate`** - Simulate treatment effect
- ❌ **`GET /models`** - List available models

**Required Frontend:**
- New page: `Predictions.tsx` or `Simulation.tsx`
- Features needed:
  - Patient outcome prediction form
  - Trajectory visualization (time-series charts)
  - Treatment simulation interface
  - Model selection/status

### 4. Medications API - **PARTIAL**
Missing UI components:
- ❌ **Medication Database Browser** - Browse/search all medications
- ❌ **Medication Details Page** - View detailed medication information
- ❌ **Load Medications Button** - Admin function to load HF medications

**Required Frontend:**
- New page: `MedicationDatabase.tsx` or enhance existing pages
- Features needed:
  - Medication search/browse interface
  - Category filtering
  - Medication detail view (properties, interactions, dosages)
  - Admin panel for loading medications

---

## Summary

### ✅ Implemented (4/7 API modules)
1. Recommendations - ✅ Complete
2. Documents - ✅ Complete
3. Medications - ⚠️ Partial (search integrated, but no dedicated pages)

### ❌ Missing (3/7 API modules)
1. **Digital Twin** - ❌ No frontend (6 endpoints)
2. **Temporal Data** - ❌ No frontend (4 endpoints)
3. **Predictions/Simulation** - ❌ No frontend (4 endpoints)

### 📊 Statistics
- **Total Backend Endpoints**: ~25
- **Endpoints with Frontend**: ~12 (48%)
- **Endpoints without Frontend**: ~13 (52%)

---

## Recommended Implementation Priority

### Priority 1: Digital Twin Management
**Why**: Core feature for personalized patient management
**Pages Needed**:
- `PatientManagement.tsx` - Main digital twin page
- Features: Initialize patient, view status, add history, update outcomes

### Priority 2: Temporal Data / Patient History
**Why**: Essential for clinical-grade data visualization
**Pages Needed**:
- `PatientHistory.tsx` - Temporal data visualization
- Features: PDF upload, time-series charts, patient summary

### Priority 3: Predictions & Simulation
**Why**: Advanced features for outcome prediction
**Pages Needed**:
- `Predictions.tsx` - Outcome prediction
- `Simulation.tsx` - Treatment simulation
- Features: Prediction forms, trajectory charts, simulation interface

### Priority 4: Medication Database Browser
**Why**: Nice-to-have for browsing medication database
**Pages Needed**:
- `MedicationDatabase.tsx` - Medication browser
- Features: Search, filter by category, view details

---

## Next Steps

1. Create `DigitalTwin.tsx` page with patient management features
2. Create `TemporalData.tsx` page with time-series visualization
3. Create `Predictions.tsx` page for outcome predictions
4. Add medication database browser page
5. Update routing in `App.tsx` to include new pages
6. Add API service methods for missing endpoints
