# HF-Digital Twin Platform

A **hospital-grade** digital twin platform for heart failure (HF) patients. It combines data-driven ML, mechanistic physiology models, and clinical workflows to deliver personalized medication recommendations, outcome predictions, treatment comparison, and longitudinal patient modeling—with a production-ready API and professional web UI.

---

## What This Project Is

- **Patient digital twin**: Per-patient calibration of mechanistic models (e.g. Windkessel), outcome tracking, and model updates so recommendations improve with observed outcomes.
- **Personalized medication system**: Category-level and **drug-level** recommendations (specific drugs, dosages, strengths, frequencies) with combination success prediction and multi-scenario comparison.
- **Clinical data pipeline**: Document upload (PDFs/images), OCR (Tesseract/EasyOCR), prescription and lab report parsing, and **temporal** extraction (multi-page PDFs → time-series labs/vitals) stored in a clinical-grade patient database.
- **Hybrid intelligence**: ML models (e.g. RandomForest, GradientBoosting) for medication selection and effect prediction, plus physics-based cardiovascular models for interpretability and calibration.
- **Medication knowledge base**: RxNorm-backed medication database (search, categories, drug details, interactions) and a combination success predictor trained on medication-combination outcomes and patient parameters.

The system is built for **clinical-style use**: validation when models are untrained or data is missing (no mock/fake recommendations), audit logging, and a UI designed for clarity and minimal repetition (dashboard-driven navigation, reusable patient forms).

---

## Complexity Overview

### Backend (Python / FastAPI)

| Layer | Components |
|-------|------------|
| **API** | Multiple routers: recommendations, documents, digital twin, temporal data, medications, predictions, treatment simulation. REST with Pydantic validation and CORS. |
| **ML / treatment** | `PersonalizedMedicationRecommender` (medication + treatment effect + dosage); `MedicationRecommender`, `TreatmentEffectPredictor`, `DosageOptimizer`; `CombinationSuccessPredictor` (combination success rates); `EnhancedMedicationRecommender` (specific drugs + dosages). |
| **Mechanistic** | Windkessel-style cardiovascular models (`WindkesselModel`, `DifferentiableWindkessel`); `PatientCalibrator` (per-patient R/C calibration, outcome-based updates). |
| **Digital twin** | `DigitalTwinRecommender` orchestrating ML + calibration + patient DB; initialize patient, get recommendations with mechanistic adjustments, update from outcomes, status/history. |
| **Data** | `ClinicalPatientDatabase` (SQLite: patients, lab_values, vital_signs, medication_history, clinical_events, predictions, outcomes, calibrated_parameters, audit_log, documents). `MedicationDatabase` (RxNorm API, medications/drug_interactions/combinations). `TemporalPDFParser` for time-series extraction from PDFs. |
| **Document / OCR** | `DocumentOCR` (Tesseract/EasyOCR), `PrescriptionParser`, `LabReportParser`, temporal multi-page PDF parsing. |
| **Evaluation / ops** | Classification, survival, regression, calibration, clinical metrics; bias analysis; robustness and external validation; monitoring and experiment tracking. |

### Frontend (React / TypeScript)

- **Layout**: Single navbar (Dashboard, Patients, Medications), dashboard as main entry point, footer with branding and documentation links.
- **Pages**: Dashboard (main + quick actions), Patients (new/search/upload, quick actions to recommendations, digital twin, history, predictions, comparison), Recommendations (standard + enhanced API, `PatientInfoForm`), Treatment Comparison (scenario comparison with medication search), Digital Twin (initialize, status, history, recommendations), Temporal Data (upload, labs/vitals charts, summary), Predictions (predict, trajectory, simulate, models), Medication Database (search, by category, details, load HF medications).
- **Shared**: Reusable `PatientInfoForm` (demographics, vitals, labs, comorbidities), `RecommendationResults` (standard vs enhanced with specific drugs/dosages/success rates), API client covering all backend domains.

### External Dependencies

- **RxNorm API** (public, no key): medication concepts, properties, related drugs, interactions.
- **Datasets**: UCI Heart Failure, Kaggle HF Prediction, MIMIC-IV (when available).

---

## Architecture (High Level)

- **Data-driven ML**: Pretrained/time-series encoders, multi-task prediction (trajectories, outcomes, treatment effects).
- **Mechanistic models**: Cardiovascular physiology for interpretability and patient-specific calibration.
- **Production stack**: FastAPI backend, React frontend, SQLite for patients and medications, scripts for training and data download.

---

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

**Frontend:**

```bash
cd frontend && npm install
```

---

## Quick Start

### Backend API

```bash
uvicorn pdt.api.main:app --reload
```

### Frontend

```bash
cd frontend && npm run dev
```

### Data loading (example)

```python
from pdt.data.loaders.uci_loader import UCILoader
loader = UCILoader()
data = loader.load()
```

### Training (example)

```python
from pdt.models.baseline_xgboost import XGBoostBaseline
model = XGBoostBaseline()
model.train(data)
predictions = model.predict(data)
```

---

## Project Structure

```
pdt/
├── api/            # FastAPI app, routers (recommendations, documents, digital_twin, temporal_data, medications, predictions, treatment_simulation)
├── data/           # Loaders (UCI, Kaggle, MIMIC), clinical_patient_database, medication_database, temporal, ETL
├── models/         # Baselines, encoders, heads, hybrid, mechanistic, treatment (recommenders, calibration, combination predictor), evaluation
├── evaluation/     # Metrics, validation, bias, robustness, clinical scores
├── utils/          # OCR, prescription_parser, lab_report_parser, temporal_pdf_parser
├── config/         # Configuration
└── monitoring/     # Logging, metrics

frontend/
├── src/
│   ├── pages/      # Dashboard, Patients, Recommendations, DigitalTwin, TemporalData, Predictions, MedicationDatabase, etc.
│   ├── components/ # Layout, PatientInfoForm, RecommendationResults, Card, Input
│   └── services/   # api.ts (all backend clients)
```

---

## Documentation

- **API**: `docs/API_DOCUMENTATION.md` (and `/frontend/public/docs/` HTML).
- **User guide**: `docs/USER_GUIDE.md`.
- **Technical**: `docs/TECHNICAL_DOCUMENTATION.md`.
- **Changelog**: `docs/CHANGELOG.md`.
- **Feature notes**: `docs/MOCK_DATA_FIX.md`, `docs/CLINICAL_TRIAL_READY.md`, `docs/MEDICATION_SYSTEM_COMPLETE.md`, `docs/FRONTEND_BACKEND_GAP_ANALYSIS.md`.

---

## License

MIT
