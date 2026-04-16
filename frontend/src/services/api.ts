import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface PredictionRequest {
    patient_id: string;
    time_horizon_days: number;
    current_medications?: string[];
}

export interface PredictionResponse {
    recommendations: Array<{
        medication: string;
        recommendation_score: number;
        is_safe: boolean;
        expected_benefit: number;
        expected_ef_improvement?: number;
        expected_mortality_reduction?: number;
        optimal_dose?: number;
        typical_dose?: [number, number];
        predicted_effect?: {
            trajectories?: {
                time_days: number[];
                ejection_fraction: number[];
                mortality_risk: number[];
            };
            predicted_effects?: {
                ejection_fraction: number;
                mortality_risk: number;
                readmission_risk: number;
            };
        };
    }>;
    summary: {
        top_recommendation: {
            medication: string;
            recommendation_score: number;
        }
    }
}

export const getMedicationRecommendations = async (data: PredictionRequest): Promise<PredictionResponse> => {
    const response = await api.post('/recommendations/medications', data);
    return response.data;
};

// Also expose an endpoint for generic prediction if needed
export const runHeartFailurePrediction = async (data: any) => {
    const response = await api.post('/digital-twin/predict-heart-failure', data);
    return response.data;
};

export const getPatientHistory = async (patientId: string) => {
    const [vitalsRes, labsRes] = await Promise.all([
        api.get(`/temporal-data/patient/${patientId}/vitals`),
        api.get(`/temporal-data/patient/${patientId}/labs`)
    ]);
    return {
        vitals: vitalsRes.data.vitals || [],
        labs: labsRes.data.lab_values || []
    };
};

export const getPatientSummary = async (patientId: string) => {
    const response = await api.get(`/temporal-data/patient/${patientId}/summary`);
    return response.data;
};

export const getOrderCategories = async () => {
    const response = await api.get('/order-catalog/categories');
    return response.data;
};

export const getOrderItems = async (category: string, search: string = '') => {
    const response = await api.get('/order-catalog/items', {
        params: { category, search }
    });
    return response.data;
};

export const submitOrders = async (patientId: string, providerId: string, items: any[]) => {
    const response = await api.post('/order-catalog/submit', {
        patient_id: patientId,
        provider_id: providerId,
        items: items
    });
    return response.data;
};

// Hospital Core Endpoints
export const getMPIPatients = async (searchTerm: string = '') => {
    const response = await api.get('/hospital/mpi', {
        params: { search: searchTerm }
    });
    return response.data;
};

export const getBedBoard = async (unit: string = '') => {
    const response = await api.get('/hospital/bedboard', {
        params: { unit: unit }
    });
    return response.data;
};

export const getInboxResults = async () => {
    const response = await api.get('/hospital/results');
    return response.data;
};

export const getSchedule = async () => {
    const response = await api.get('/hospital/schedule');
    return response.data;
};

// Provider Preferences Endpoints
export const getProviderPreferences = async (providerId: string = "DR-SMITH") => {
    const response = await api.get(`/hospital/preferences/${providerId}`);
    return response.data;
};

export const updateProviderPreferences = async (providerId: string, prefs: any) => {
    const response = await api.put(`/hospital/preferences/${providerId}`, prefs);
    return response.data;
};

// ==========================================
// REAL-TIME DIGITAL TWIN INITIALIZATION
// ==========================================

// Document OCR — patient-scoped (saves to DB, returns structured labs)
export const ingestPatientLabs = async (patientId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/hospital/patients/${patientId}/ingest-labs`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
};
export const getAllergens = async () => {
    const response = await api.get(`/hospital/allergens`);
    return response.data.allergens;
};

export const searchMedicines = async (query: string) => {
    const response = await api.get(`/hospital/medicines?q=${query}`);
    return response.data.medicines;
};

export const createDigitalTwinEncounter = async (encounterData: any) => {
    const response = await api.post(`/hospital/encounter`, encounterData);
    return response.data.patient_id;
};

export const addMedication = async (patientId: string, medicationData: any) => {
    const response = await api.post(`/hospital/patients/${patientId}/medications`, medicationData);
    return response.data;
};

export default api;
