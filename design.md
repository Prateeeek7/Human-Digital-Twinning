# HF-Digital Twin Platform — Design Document

This document describes the high-level design, architecture, and design decisions for the HF-Digital Twin platform.

---

## 1. Design Goals

- **Clinical-grade**: Validation when models are untrained or data is missing; no mock recommendations in production paths; audit logging for traceability.
- **Hybrid intelligence**: Combine data-driven ML (outcome prediction, medication selection) with mechanistic physiology (Windkessel, calibration) for interpretability and personalization.
- **Unified patient view**: Single digital twin per patient—calibrated models, recommendations, outcomes, and temporal data in one place.
- **Minimal repetition**: Dashboard-driven navigation, reusable forms (e.g. `PatientInfoForm`), shared API client and result components.

---

## 2. System Architecture

### 2.1 High-Level View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (React / TypeScript)                    │
│  Dashboard │ Patients │ Recommendations │ Digital Twin │ Predictions   │
│  Treatment Comparison │ Temporal Data │ Medication Database             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ REST / JSON
┌─────────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                                │
│  Routers: recommendations, documents, digital_twin, temporal_data,      │
│           medications, predictions, treatment_simulation                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ ML / Treatment│         │ Mechanistic     │         │ Data Layer      │
│ Recommenders  │         │ (Windkessel,    │         │ Clinical DB,    │
│ Effect/Dosage │         │  Calibration)   │         │ Medication DB,  │
│ Combination   │         │ Digital Twin    │         │ OCR / Parsers   │
└───────────────┘         └─────────────────┘         └─────────────────┘
```

### 2.2 Backend Layers

| Layer | Responsibility |
|-------|----------------|
| **API** | REST endpoints, Pydantic request/response validation, CORS, error handling. |
| **Orchestration** | `DigitalTwinRecommender` coordinates ML, calibration, and patient DB for recommendations and updates. |
| **ML / treatment** | Medication recommendation (category + drug-level), treatment effect prediction, dosage optimization, combination success. |
| **Mechanistic** | Windkessel-style models; `PatientCalibrator` for per-patient R/C and outcome-based updates. |
| **Data** | `ClinicalPatientDatabase` (SQLite), `MedicationDatabase` (RxNorm), document/OCR and temporal PDF parsing. |

### 2.3 Frontend Structure

- **Entry**: Dashboard as main landing; quick actions to common flows (new patient, recommendations, digital twin).
- **Navigation**: Single navbar (Dashboard, Patients, Medications) with footer links to docs.
- **Pages**: Dedicated routes for Patients, Recommendations, Treatment Comparison, Digital Twin, Temporal Data, Predictions, Medication Database.
- **Shared**: `PatientInfoForm` (demographics, vitals, labs, comorbidities), `RecommendationResults` (standard vs enhanced with drugs/dosages/success), centralized API client.

---

## 3. Core Components

### 3.1 Digital Twin Recommender

- **Role**: Single entry point for “patient-aware” recommendations and twin lifecycle.
- **Responsibilities**: Initialize patient twin, fetch recommendations (with mechanistic adjustments), update from outcomes, expose status/history.
- **Inputs**: Patient ID, optional scenario parameters (e.g. target BP, constraints).
- **Outputs**: Recommendations, confidence/limits, calibration status, and audit trail.

### 3.2 Personalized Medication System

- **Category-level**: Drug classes and high-level suggestions.
- **Drug-level**: Specific drugs, dosages, strengths, frequencies (e.g. `EnhancedMedicationRecommender`).
- **Combination**: `CombinationSuccessPredictor` for multi-drug success rates and patient parameters.
- **Knowledge**: RxNorm-backed medication database (search, categories, interactions).

### 3.3 Clinical Data Pipeline

- **Upload**: PDFs/images via API and UI.
- **OCR**: Tesseract/EasyOCR in `DocumentOCR`; prescription and lab report parsers.
- **Temporal**: Multi-page PDFs → time-series labs/vitals via `TemporalPDFParser`.
- **Storage**: Normalized tables (patients, lab_values, vital_signs, medication_history, clinical_events, documents, audit_log).

### 3.4 Mechanistic Models

- **Windkessel**: `WindkesselModel` and `DifferentiableWindkessel` for cardiovascular dynamics.
- **Calibration**: `PatientCalibrator` fits R/C (and related parameters) per patient; updates from observed outcomes to improve future recommendations.

---

## 4. Data Design

### 4.1 Clinical Patient Database (SQLite)

- **Core**: `patients` (demographics, identifiers).
- **Time-series**: `lab_values`, `vital_signs` with timestamps and source (e.g. document ID).
- **Clinical**: `medication_history`, `clinical_events`, `predictions`, `outcomes`, `calibrated_parameters`.
- **Audit**: `audit_log` for recommendation requests, model updates, and key actions.
- **Documents**: Document metadata and references for OCR/parsing outputs.

### 4.2 Medication Database

- **Source**: RxNorm API (concepts, properties, related drugs, interactions).
- **Usage**: Search, category browse, drug details, interaction checks, and feeding the combination success predictor.

### 4.3 Validation Rules

- Required fields enforced at API and DB layer (e.g. patient ID, critical vitals/labs when used for recommendations).
- No “fake” or placeholder recommendations when models are untrained or data is insufficient; return clear validation/limit status instead.

---

## 5. API Design Principles

- **REST**: Resource-oriented URLs; JSON bodies; consistent error format (e.g. status, message, details).
- **Validation**: Pydantic for all request/response schemas; 422 on invalid input with field-level errors.
- **Idempotency**: Safe operations where appropriate; clear semantics for create vs update.
- **Documentation**: OpenAPI/Swagger from FastAPI; aligned with `docs/API_DOCUMENTATION.md` and frontend `/docs` HTML.

---

## 6. UI/UX Design

- **Clarity**: Labels, units, and ranges visible on forms; recommendations show confidence/limits when available.
- **Efficiency**: Dashboard quick actions; patient-scoped links to recommendations, digital twin, history, comparison.
- **Consistency**: Same `PatientInfoForm` across recommendation, digital twin, and prediction flows; shared result and card components.
- **Feedback**: Loading and error states; messages when data is missing or models cannot yet recommend.

---

## 7. Security and Operations

- **Audit**: All recommendation and twin-update paths logged (who, when, inputs, outcome references).
- **CORS**: Configured for frontend origin(s); no broad `*` in production.
- **Sensitive data**: No credentials in frontend; API keys and DB paths in env/backend config only.
- **Evaluation and monitoring**: Classification/survival/regression metrics; bias and robustness checks; experiment tracking (e.g. MLflow, wandb) for model lifecycle.

---

## 8. Technology Choices

| Area | Choice | Rationale |
|------|--------|-----------|
| Backend | FastAPI | Async, automatic OpenAPI, Pydantic integration. |
| Frontend | React + TypeScript + Vite | Component reuse, type safety, fast dev build. |
| DB | SQLite | Single-file, no separate server; suitable for single-tenant and demos. |
| ML | PyTorch, XGBoost, LightGBM, scikit-learn | Flexibility for baselines, survival, and custom models. |
| OCR | Tesseract / EasyOCR | Balance of accuracy and speed; configurable per use case. |
| Medications | RxNorm API | Standard terminology and interaction data. |

---

## 9. Future Considerations

- **Scale**: Replace SQLite with PostgreSQL for multi-tenant or higher concurrency; consider read replicas for reporting.
- **Real-time**: WebSockets or SSE for long-running calibrations or batch prediction status.
- **Deployment**: Containerized backend and frontend; env-based config; health and readiness endpoints for orchestration.

---

*This design aligns with the project README, requirements, and existing API/frontend structure. Update this document when making significant architectural changes.*
