import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import PatientInfoForm from '../components/PatientInfoForm'
import { recommendationsApi, PatientInfo } from '../services/api'
import { Loader2, AlertTriangle, Pill, TrendingUp } from 'lucide-react'
import RecommendationResults from '../components/RecommendationResults'
import './Recommendations.css'

export default function Recommendations() {
  const location = useLocation()
  const [patientInfo, setPatientInfo] = useState<PatientInfo>(
    (location.state?.patientInfo as PatientInfo) || {
      age: undefined,
      sex: '',
      ejection_fraction: undefined,
      systolic_bp: undefined,
      heart_rate: undefined,
      creatinine: undefined,
      diabetes: false,
      high_blood_pressure: false,
    }
  )
  const [currentMedications, setCurrentMedications] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (field: string, value: any) => {
    setPatientInfo((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const [useEnhanced, setUseEnhanced] = useState(true)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)

    // Client-side validation
    if (!patientInfo.age || patientInfo.age === undefined) {
      setError('Please provide patient age. Age is required for accurate recommendations.')
      setLoading(false)
      return
    }

    if (!patientInfo.ejection_fraction || patientInfo.ejection_fraction === undefined) {
      setError('Please provide ejection fraction. Ejection fraction is required for accurate recommendations.')
      setLoading(false)
      return
    }

    try {
      // Use enhanced recommender for specific drugs and dosages
      const response = useEnhanced
        ? await recommendationsApi.getEnhancedRecommendations(
            patientInfo,
            currentMedications,
            90
          )
        : await recommendationsApi.getRecommendations(
            patientInfo,
            currentMedications,
            90
          )
      setResults(response)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get recommendations'
      setError(errorMessage)
      setResults(null) // Clear any previous results
    } finally {
      setLoading(false)
    }
  }

  const addMedication = () => {
    const med = prompt('Enter medication name:')
    if (med) {
      setCurrentMedications([...currentMedications, med])
    }
  }

  const removeMedication = (index: number) => {
    setCurrentMedications(currentMedications.filter((_, i) => i !== index))
  }

  return (
    <div className="recommendations-page">
      <div className="page-header">
        <h1>Medication Recommendations</h1>
        <p>Enter patient information to get personalized medication recommendations based on AI-powered analysis</p>
      </div>

      <div className="recommendations-layout">
        <Card title="Patient Information" className="form-card">
          <form onSubmit={handleSubmit} className="patient-form">
            <div className="form-section">
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={useEnhanced}
                    onChange={(e) => setUseEnhanced(e.target.checked)}
                  />
                  <span>Use Enhanced Recommendations (Specific drugs with dosages)</span>
                </label>
              </div>
            </div>
            <PatientInfoForm
              patientInfo={patientInfo}
              onChange={handleInputChange}
              showComorbidities={true}
            />

            <div className="form-section">
              <h3>
                <Pill size={18} />
                Current Medications
              </h3>
              <p className="section-description">List all current medications to check for interactions and optimize recommendations</p>
              <div className="medications-list">
                {currentMedications.length > 0 ? (
                  currentMedications.map((med, index) => (
                    <div key={index} className="medication-tag">
                      <span>{med.replace(/_/g, ' ')}</span>
                      <button
                        type="button"
                        onClick={() => removeMedication(index)}
                        className="remove-med"
                        title="Remove medication"
                      >
                        ×
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="empty-state">No medications added yet</p>
                )}
                <Button type="button" variant="secondary" onClick={addMedication}>
                  + Add Medication
                </Button>
              </div>
              <div className="medication-hints">
                <small>Common medications: ace_inhibitor, beta_blocker, diuretic, arni, aldosterone_antagonist</small>
              </div>
            </div>

            {error && (
              <div className="error-message">
                <AlertTriangle size={20} />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={loading}
              className="submit-button"
            >
              {loading ? (
                <>
                  <Loader2 className="spinner" size={20} />
                  Getting Recommendations...
                </>
              ) : (
                <>
                  <TrendingUp size={20} />
                  Get Recommendations
                </>
              )}
            </Button>
          </form>
        </Card>

        {results && (
          <div className="results-section">
            <RecommendationResults results={results} />
          </div>
        )}
      </div>
    </div>
  )
}

