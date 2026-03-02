from fastapi import FastAPI
from pdt.api.endpoints import digital_twin, recommendations, temporal_data, documents, medications, treatment_simulation

app = FastAPI()
app.include_router(digital_twin.router)
app.include_router(recommendations.router)
app.include_router(temporal_data.router)
app.include_router(documents.router)
app.include_router(medications.router)
app.include_router(treatment_simulation.router)

for route in app.routes:
    print(f"{route.methods} {route.path}")
