# Frontend-Backend Gap Analysis

## Complete Backend Endpoint List (37 routes)

### ✅ Implemented in Frontend

#### Recommendations (2/3 endpoints)
- ✅ `POST /recommendations/medications` → `Recommendations.tsx`
- ✅ `POST /recommendations/compare-scenarios` → `TreatmentComparison.tsx`
- ⚠️ `GET /recommendations/health` → Not needed (internal)

#### Documents (3/3 endpoints)
- ✅ `POST /documents/upload-prescription` → `DocumentUpload.tsx`
- ✅ `POST /documents/upload-lab-report` → `DocumentUpload.tsx`
- ✅ `POST /documents/extract-text` → `DocumentUpload.tsx`

#### Medications (Partial - 3/7 endpoints)
- ✅ `GET /medications/search` → Used in `TreatmentComparison.tsx` (search dropdown)
- ✅ `POST /medications/recommendations/enhanced` → `Recommendations.tsx` (enhanced mode)
- ✅ `POST /medications/compare-combinations` → `TreatmentComparison.tsx`
- ❌ `GET /medications/category/{category}` → No UI
- ❌ `GET /medications/{medication_name}` → No UI
- ❌ `POST /medications/load-hf-medications` → No UI
- ❌ `POST /medications/predict-combination` → API exists, but no dedicated UI

---

### ❌ Missing Frontend Implementation

#### Digital Twin (0/6 endpoints) - **CRITICAL MISSING**
- ❌ `POST /digital-twin/initialize` - Initialize patient digital twin
- ❌ `POST /digital-twin/recommendations` - Get personalized digital twin recommendations
- ❌ `POST /digital-twin/update-outcome` - Update with observed outcomes
- ❌ `GET /digital-twin/status/{patient_id}` - Get digital twin status
- ❌ `POST /digital-twin/history` - Add patient history entry
- ❌ `GET /digital-twin/history/{patient_id}` - Get patient history

**Impact**: Core personalized digital twin functionality is completely inaccessible from UI

#### Temporal Data (0/4 endpoints) - **CRITICAL MISSING**
- ❌ `POST /temporal-data/upload-pdf` - Upload multi-page PDF for temporal extraction
- ❌ `GET /temporal-data/patient/{patient_id}/labs` - Get time-series lab values
- ❌ `GET /temporal-data/patient/{patient_id}/vitals` - Get time-series vitals
- ❌ `GET /temporal-data/patient/{patient_id}/summary` - Get patient temporal summary

**Impact**: Clinical-grade temporal data visualization and bulk PDF processing unavailable

#### Main API (0/4 endpoints) - **MISSING**
- ❌ `POST /predict` - Predict patient outcomes
- ❌ `POST /trajectory` - Predict patient trajectory
- ❌ `POST /treatment/simulate` - Simulate treatment effect
- ❌ `GET /models` - List available models

**Impact**: Outcome prediction and treatment simulation features unavailable

#### Medications (4/7 endpoints missing UI)
- ❌ `GET /medications/category/{category}` - Browse by category
- ❌ `GET /medications/{medication_name}` - View medication details
- ❌ `POST /medications/load-hf-medications` - Load medications (admin)
- ❌ `POST /medications/predict-combination` - Predict combination (standalone UI)

---

## Statistics

| Category | Total Endpoints | With Frontend | Missing Frontend | Coverage |
|----------|----------------|---------------|------------------|----------|
| **Recommendations** | 3 | 2 | 1 (health) | 100% ✅ |
| **Documents** | 3 | 3 | 0 | 100% ✅ |
| **Medications** | 7 | 3 | 4 | 43% ⚠️ |
| **Digital Twin** | 6 | 0 | 6 | 0% ❌ |
| **Temporal Data** | 4 | 0 | 4 | 0% ❌ |
| **Main API** | 4 | 0 | 4 | 0% ❌ |
| **System** | 10 | 0 | 10 (health/docs) | N/A |
| **TOTAL** | **37** | **8** | **29** | **22%** |

**Note**: System endpoints (health checks, docs) are not user-facing and don't need frontend.

---

## Required Frontend Pages

### 1. Digital Twin Management Page (`DigitalTwin.tsx`)
**Priority**: 🔴 HIGH

**Features Needed**:
- Patient initialization form
  - Patient ID input
  - Patient information form (age, EF, vitals, labs, comorbidities)
  - Initialize button → `POST /digital-twin/initialize`
- Digital Twin Status Dashboard
  - Patient ID lookup
  - Display calibration status
  - Show prediction accuracy
  - Number of data points
  - Calibration quality metrics
  - → `GET /digital-twin/status/{patient_id}`
- Patient History Management
  - Add history entry form (vitals, labs, medications)
  - View history timeline
  - → `POST /digital-twin/history`, `GET /digital-twin/history/{patient_id}`
- Outcome Tracking
  - Update observed outcomes form
  - Compare predicted vs observed
  - → `POST /digital-twin/update-outcome`
- Digital Twin Recommendations
  - Get personalized recommendations using digital twin
  - → `POST /digital-twin/recommendations`

### 2. Temporal Data / Patient History Page (`TemporalData.tsx`)
**Priority**: 🔴 HIGH

**Features Needed**:
- Multi-page PDF Upload
  - File upload interface
  - Patient ID input
  - Reference date picker
  - Auto-import toggle
  - Progress indicator for large PDFs
  - → `POST /temporal-data/upload-pdf`
- Time-Series Lab Values Visualization
  - Patient ID lookup
  - Date range filter
  - Lab name filter (comma-separated)
  - Interactive charts (line charts, time-series)
  - Data table with export
  - → `GET /temporal-data/patient/{patient_id}/labs`
- Time-Series Vitals Visualization
  - Similar to labs
  - Multiple vitals on same chart
  - → `GET /temporal-data/patient/{patient_id}/vitals`
- Patient Summary Dashboard
  - Overview of all temporal data
  - Data counts, date ranges
  - Quality metrics
  - → `GET /temporal-data/patient/{patient_id}/summary`

### 3. Predictions & Simulation Page (`Predictions.tsx`)
**Priority**: 🟡 MEDIUM

**Features Needed**:
- Outcome Prediction
  - Patient data form
  - Task selection (readmission, mortality, EF)
  - Prediction results display
  - → `POST /predict`
- Trajectory Prediction
  - Patient data form
  - Time horizon selection
  - Trajectory visualization (charts)
  - → `POST /trajectory`
- Treatment Simulation
  - Patient state form
  - Treatment selection
  - Dose input
  - Time horizon
  - Simulated trajectory charts
  - → `POST /treatment/simulate`
- Model Status
  - List available models
  - Model versions
  - → `GET /models`

### 4. Medication Database Browser (`MedicationDatabase.tsx`)
**Priority**: 🟢 LOW

**Features Needed**:
- Medication Search
  - Search bar (already exists in TreatmentComparison)
  - Results list with pagination
- Category Browser
  - Filter by category (ACE inhibitor, Beta-blocker, etc.)
  - Category list view
  - → `GET /medications/category/{category}`
- Medication Details View
  - Full medication information
  - Properties, interactions, dosages
  - Related medications
  - → `GET /medications/{medication_name}`
- Admin Functions
  - Load HF medications button
  - Progress indicator
  - → `POST /medications/load-hf-medications`
- Combination Predictor Standalone
  - Patient info form
  - Medication selection
  - Dosage input
  - Success rate prediction
  - → `POST /medications/predict-combination`

---

## Implementation Checklist

### Phase 1: Critical Features (Digital Twin + Temporal Data)
- [ ] Create `DigitalTwin.tsx` page
- [ ] Create `TemporalData.tsx` page
- [ ] Add API service methods for digital twin endpoints
- [ ] Add API service methods for temporal data endpoints
- [ ] Update `App.tsx` routing
- [ ] Update `Layout.tsx` navigation

### Phase 2: Advanced Features (Predictions)
- [ ] Create `Predictions.tsx` page
- [ ] Add API service methods for prediction endpoints
- [ ] Add trajectory visualization components
- [ ] Update routing

### Phase 3: Enhancement (Medication Database)
- [ ] Create `MedicationDatabase.tsx` page
- [ ] Add medication detail view component
- [ ] Add category browser
- [ ] Update routing

---

## API Service Methods to Add

```typescript
// Add to frontend/src/services/api.ts

export const digitalTwinApi = {
  initialize: async (patientId: string, patientInfo: PatientInfo) => {
    const response = await api.post('/digital-twin/initialize', {
      patient_id: patientId,
      patient_info: patientInfo
    })
    return response.data
  },
  
  getRecommendations: async (patientId: string, patientInfo: PatientInfo, ...) => {
    // ...
  },
  
  updateOutcome: async (patientId: string, outcomeType: string, observedOutcome: any) => {
    // ...
  },
  
  getStatus: async (patientId: string) => {
    // ...
  },
  
  addHistory: async (patientId: string, vitals?: any, labs?: any, medications?: string[]) => {
    // ...
  },
  
  getHistory: async (patientId: string) => {
    // ...
  }
}

export const temporalDataApi = {
  uploadPDF: async (file: File, patientId: string, referenceDate?: string, autoImport?: boolean) => {
    // ...
  },
  
  getPatientLabs: async (patientId: string, labNames?: string[], startDate?: string, endDate?: string) => {
    // ...
  },
  
  getPatientVitals: async (patientId: string, vitalNames?: string[], startDate?: string, endDate?: string) => {
    // ...
  },
  
  getPatientSummary: async (patientId: string) => {
    // ...
  }
}

export const predictionsApi = {
  predict: async (patientData: any, tasks?: string[]) => {
    // ...
  },
  
  predictTrajectory: async (patientData: any) => {
    // ...
  },
  
  simulateTreatment: async (patientState: any, treatment: string, dose: number, timeHorizon: number) => {
    // ...
  },
  
  listModels: async () => {
    // ...
  }
}
```

---

## Summary

**Current Status**: 22% of user-facing endpoints have frontend implementation

**Critical Gaps**:
1. **Digital Twin** - 0% coverage (6 endpoints)
2. **Temporal Data** - 0% coverage (4 endpoints)
3. **Predictions** - 0% coverage (4 endpoints)

**Next Steps**: Implement Phase 1 (Digital Twin + Temporal Data) to unlock core personalized features.
