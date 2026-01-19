# Patient Digital Twin (PDT)

Hospital-Grade Patient Digital Twin system for heart-failure patients with hybrid architecture (mechanistic + ML), longitudinal trajectory forecasting, treatment simulation, and production-ready infrastructure.

## Architecture

The system combines:
- **Data-driven ML**: Pretrained time-series encoders for EHR/physiological data
- **Mechanistic models**: Cardiovascular physiology models for interpretability
- **Multi-task learning**: Simultaneous prediction of trajectories, outcomes, and treatment effects
- **Production infrastructure**: API, monitoring, and deployment pipeline

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Data Loading

```python
from pdt.data.loaders.uci_loader import UCILoader

loader = UCILoader()
data = loader.load()
```

### Training Baseline Models

```python
from pdt.models.baseline_xgboost import XGBoostBaseline

model = XGBoostBaseline()
model.train(data)
predictions = model.predict(data)
```

### Using the API

```bash
uvicorn pdt.api.main:app --reload
```

## Project Structure

```
pdt/
├── data/           # Data loading and preprocessing
├── models/         # Model architectures
├── evaluation/     # Metrics and validation
├── api/            # REST API
├── utils/          # Shared utilities
└── config/         # Configuration management
```

## Datasets

- UCI Heart Failure Clinical Records
- Kaggle Heart Failure Prediction
- MIMIC-IV (when access obtained)

## License

MIT



