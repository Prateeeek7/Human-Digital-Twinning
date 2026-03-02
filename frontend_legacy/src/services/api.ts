import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface PatientInfo {
  age?: number
  sex?: string
  gender?: string
  heart_rate?: number
  systolic_bp?: number
  diastolic_bp?: number
  ejection_fraction?: number
  creatinine?: number
  sodium?: number
  diabetes?: boolean
  high_blood_pressure?: boolean
  hypertension?: boolean
  high_cholesterol?: boolean
  nt_pro_bnp?: number
  troponin?: number
  nyha_class?: string
  atrial_fibrillation?: boolean
  copd?: boolean
  ckd?: boolean
  anemia?: boolean
  max_hr?: number
  oldpeak?: number
  st_slope?: string
  chest_pain_type?: string
  exercise_angina?: boolean
  resting_ecg?: string
  [key: string]: any
}

export interface MedicationRecommendation {
  medication: string
  recommendation_score: number
  expected_benefit: number
  is_safe: boolean
  interactions: any[]
  predicted_effect?: any
  optimal_dose?: number
}

export interface RecommendationResponse {
  patient_info: PatientInfo
  current_medications: string[]
  baseline_prediction: any
  recommendations: MedicationRecommendation[]
  optimal_combination: {
    medications: string[]
    total_benefit: number
  }
  summary: any
}

export const recommendationsApi = {
  getRecommendations: async (
    patientInfo: PatientInfo,
    currentMedications: string[] = [],
    timeHorizonDays: number = 90
  ): Promise<RecommendationResponse> => {
    const response = await api.post('/recommendations/medications', {
      patient_info: patientInfo,
      current_medications: currentMedications,
      time_horizon_days: timeHorizonDays,
    })
    return response.data
  },

  getEnhancedRecommendations: async (
    patientInfo: PatientInfo,
    currentMedications: string[] = [],
    timeHorizonDays: number = 90
  ) => {
    const response = await api.post('/medications/recommendations/enhanced', {
      ...patientInfo,
      current_medications: currentMedications,
      time_horizon_days: timeHorizonDays,
    })
    return response.data
  },

  compareScenarios: async (
    patientInfo: PatientInfo,
    scenarios: Array<{ medications: string[]; dosages?: Record<string, number> }>
  ) => {
    const response = await api.post('/recommendations/compare-scenarios', {
      patient_info: patientInfo,
      scenarios,
    })
    return response.data
  },

  predictCombination: async (
    patientInfo: PatientInfo,
    medications: string[],
    dosages?: Record<string, number>
  ) => {
    const response = await api.post('/medications/predict-combination', {
      patient_info: patientInfo,
      medications,
      dosages,
    })
    return response.data
  },

  compareCombinations: async (
    patientInfo: PatientInfo,
    combinations: Array<{ medications: string[]; dosages?: Record<string, number> }>
  ) => {
    const response = await api.post('/medications/compare-combinations', {
      patient_info: patientInfo,
      combinations,
    })
    return response.data
  },
}

export const medicationsApi = {
  search: async (query: string, limit: number = 50) => {
    const response = await api.get('/medications/search', {
      params: { query, limit },
    })
    return response.data
  },

  getByCategory: async (category: string) => {
    const response = await api.get(`/medications/category/${category}`)
    return response.data
  },

  getMedication: async (name: string) => {
    const response = await api.get(`/medications/${encodeURIComponent(name)}`)
    return response.data
  },

  loadHFMedications: async () => {
    const response = await api.post('/medications/load-hf-medications')
    return response.data
  },
}

export const documentsApi = {
  uploadPrescription: async (
    file: File,
    getRecommendations: boolean = false
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('get_recommendations', getRecommendations.toString())

    const response = await api.post('/documents/upload-prescription', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  uploadLabReport: async (
    file: File,
    getRecommendations: boolean = false
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('get_recommendations', getRecommendations.toString())

    const response = await api.post('/documents/upload-lab-report', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  extractText: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/documents/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

export const digitalTwinApi = {
  initialize: async (patientId: string, patientInfo: PatientInfo) => {
    const response = await api.post('/digital-twin/initialize', {
      patient_id: patientId,
      patient_info: patientInfo,
    })
    return response.data
  },

  predictHeartFailure: async (patientId: string, patientInfo: PatientInfo) => {
    const response = await api.post('/digital-twin/predict-heart-failure', {
      patient_id: patientId,
      patient_info: patientInfo,
    })
    return response.data
  },

  getRecommendations: async (
    patientId: string,
    patientInfo: PatientInfo,
    currentMedications: string[] = [],
    timeHorizonDays: number = 90,
    useMechanistic: boolean = true
  ) => {
    const response = await api.post('/digital-twin/recommendations', {
      patient_id: patientId,
      patient_info: patientInfo,
      current_medications: currentMedications,
      time_horizon_days: timeHorizonDays,
      use_mechanistic: useMechanistic,
    })
    return response.data
  },

  updateOutcome: async (
    patientId: string,
    outcomeType: string,
    observedOutcome: any
  ) => {
    const response = await api.post('/digital-twin/update-outcome', {
      patient_id: patientId,
      outcome_type: outcomeType,
      observed_outcome: observedOutcome,
    })
    return response.data
  },

  getStatus: async (patientId: string) => {
    const response = await api.get(`/digital-twin/status/${patientId}`)
    return response.data
  },

  addHistory: async (
    patientId: string,
    vitals?: any,
    labs?: any,
    medications?: string[]
  ) => {
    const response = await api.post('/digital-twin/history', null, {
      params: {
        patient_id: patientId,
        vitals: vitals ? JSON.stringify(vitals) : undefined,
        labs: labs ? JSON.stringify(labs) : undefined,
        medications: medications ? JSON.stringify(medications) : undefined,
      },
    })
    return response.data
  },

  getHistory: async (patientId: string) => {
    const response = await api.get(`/digital-twin/history/${patientId}`)
    return response.data
  },
}

export const temporalDataApi = {
  uploadPDF: async (
    file: File,
    patientId: string,
    referenceDate?: string,
    autoImport: boolean = true
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    if (referenceDate) {
      formData.append('reference_date', referenceDate)
    }
    formData.append('auto_import', autoImport.toString())

    const response = await api.post(
      `/temporal-data/upload-pdf?patient_id=${patientId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getPatientLabs: async (
    patientId: string,
    labNames?: string[],
    startDate?: string,
    endDate?: string
  ) => {
    const params: any = {}
    if (labNames && labNames.length > 0) {
      params.lab_names = labNames.join(',')
    }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get(`/temporal-data/patient/${patientId}/labs`, {
      params,
    })
    return response.data
  },

  getPatientVitals: async (
    patientId: string,
    vitalNames?: string[],
    startDate?: string,
    endDate?: string
  ) => {
    const params: any = {}
    if (vitalNames && vitalNames.length > 0) {
      params.vital_names = vitalNames.join(',')
    }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await api.get(`/temporal-data/patient/${patientId}/vitals`, {
      params,
    })
    return response.data
  },

  getPatientSummary: async (patientId: string) => {
    const response = await api.get(`/temporal-data/patient/${patientId}/summary`)
    return response.data
  },
}

export const predictionsApi = {
  predict: async (patientData: any, tasks?: string[]) => {
    const response = await api.post('/predict', {
      patient_data: patientData,
      tasks,
    })
    return response.data
  },

  predictTrajectory: async (patientData: any) => {
    const response = await api.post('/trajectory', {
      patient_data: patientData,
    })
    return response.data
  },

  simulateTreatment: async (
    patientState: any,
    treatment: string,
    dose: number = 1.0,
    timeHorizon: number = 30
  ) => {
    const response = await api.post('/treatment/simulate', {
      patient_state: patientState,
      treatment,
      treatment_dose: dose,
      time_horizon: timeHorizon,
    })
    return response.data
  },

  listModels: async () => {
    const response = await api.get('/models')
    return response.data
  },
}

export default api

