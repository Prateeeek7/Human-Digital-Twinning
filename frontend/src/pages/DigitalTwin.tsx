import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import PatientInfoForm from '../components/PatientInfoForm'
import { digitalTwinApi, PatientInfo } from '../services/api'
import { 
  UserPlus, 
  Activity, 
  TrendingUp, 
  History, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  Heart,
  Calendar,
  Database
} from 'lucide-react'
import './DigitalTwin.css'

export default function DigitalTwin() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState<'initialize' | 'status' | 'history' | 'outcome' | 'recommendations'>('initialize')
  const [patientId, setPatientId] = useState<string>(location.state?.patientId || '')
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
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (field: string, value: any) => {
    setPatientInfo((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleInitialize = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await digitalTwinApi.initialize(patientId, patientInfo)
      setResults(response)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initialize patient')
    } finally {
      setLoading(false)
    }
  }

  const handleGetStatus = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await digitalTwinApi.getStatus(patientId)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get status')
    } finally {
      setLoading(false)
    }
  }

  const handleGetHistory = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await digitalTwinApi.getHistory(patientId)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get history')
    } finally {
      setLoading(false)
    }
  }

  const handleGetRecommendations = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await digitalTwinApi.getRecommendations(
        patientId,
        patientInfo,
        [],
        90,
        true
      )
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="digital-twin-page">
      <div className="page-header">
        <h1>Patient Digital Twin</h1>
        <p>Manage personalized patient digital twins with calibrated models and outcome tracking</p>
      </div>

      <div className="digital-twin-layout">
        <Card title="Patient ID" className="patient-id-card">
          <Input
            label="Patient ID"
            type="text"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            placeholder="Enter patient ID (e.g., P001)"
          />
        </Card>

        <div className="tabs-container">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'initialize' ? 'active' : ''}`}
              onClick={() => setActiveTab('initialize')}
            >
              <UserPlus size={18} />
              Initialize
            </button>
            <button
              className={`tab ${activeTab === 'status' ? 'active' : ''}`}
              onClick={() => setActiveTab('status')}
            >
              <Activity size={18} />
              Status
            </button>
            <button
              className={`tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={18} />
              History
            </button>
            <button
              className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommendations')}
            >
              <TrendingUp size={18} />
              Recommendations
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'initialize' && (
              <Card title="Initialize Patient Digital Twin" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Initialize a new patient in the digital twin system. This will calibrate patient-specific parameters.</span>
                </div>
                <PatientInfoForm
                  patientInfo={patientInfo}
                  onChange={handleInputChange}
                  showComorbidities={true}
                />
                <Button onClick={handleInitialize} disabled={loading || !patientId} style={{ marginTop: 'var(--spacing-lg)' }}>
                  {loading ? 'Initializing...' : 'Initialize Digital Twin'}
                </Button>
              </Card>
            )}

            {activeTab === 'status' && (
              <Card title="Digital Twin Status" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>View the status and calibration quality of a patient's digital twin.</span>
                </div>
                <Button onClick={handleGetStatus} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get Status'}
                </Button>
                {results && results.calibration_status && (
                  <div className="status-results">
                    <div className="status-section">
                      <h3>Calibration Status</h3>
                      <div className={`status-badge ${results.calibration_status === 'calibrated' ? 'success' : 'warning'}`}>
                        {results.calibration_status === 'calibrated' ? (
                          <>
                            <CheckCircle size={16} />
                            <span>Calibrated</span>
                          </>
                        ) : (
                          <>
                            <AlertTriangle size={16} />
                            <span>Not Calibrated</span>
                          </>
                        )}
                      </div>
                    </div>
                    {results.prediction_accuracy && (
                      <div className="status-section">
                        <h3>Prediction Accuracy</h3>
                        <div className="metric-grid">
                          <div className="metric">
                            <span className="metric-label">EF Accuracy</span>
                            <span className="metric-value">
                              {(results.prediction_accuracy.ef_accuracy * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="metric">
                            <span className="metric-label">Mortality Accuracy</span>
                            <span className="metric-value">
                              {(results.prediction_accuracy.mortality_accuracy * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                    {results.n_data_points !== undefined && (
                      <div className="status-section">
                        <h3>Data Points</h3>
                        <div className="data-points">
                          <Database size={20} />
                          <span>{results.n_data_points} history entries</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'history' && (
              <Card title="Patient History" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>View and manage patient history entries for digital twin calibration.</span>
                </div>
                <Button onClick={handleGetHistory} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get History'}
                </Button>
                {results && results.history && (
                  <div className="history-results">
                    <div className="history-header">
                      <span>Total Entries: {results.n_entries}</span>
                    </div>
                    <div className="history-list">
                      {results.history.slice(0, 10).map((entry: any, idx: number) => (
                        <div key={idx} className="history-item">
                          <div className="history-date">
                            <Calendar size={14} />
                            <span>{entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : 'N/A'}</span>
                          </div>
                          <div className="history-content">
                            {entry.vitals && (
                              <div className="history-section">
                                <strong>Vitals:</strong> {JSON.stringify(entry.vitals)}
                              </div>
                            )}
                            {entry.labs && (
                              <div className="history-section">
                                <strong>Labs:</strong> {JSON.stringify(entry.labs)}
                              </div>
                            )}
                            {entry.medications && entry.medications.length > 0 && (
                              <div className="history-section">
                                <strong>Medications:</strong> {entry.medications.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'recommendations' && (
              <Card title="Digital Twin Recommendations" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Get personalized recommendations using the patient's calibrated digital twin.</span>
                </div>
                <div className="patient-form">
                  <div className="form-row">
                    <Input
                      label="Ejection Fraction (%)"
                      type="number"
                      step="0.01"
                      value={patientInfo.ejection_fraction ? (patientInfo.ejection_fraction * 100).toFixed(0) : ''}
                      onChange={(e) => handleInputChange('ejection_fraction', parseFloat(e.target.value) / 100)}
                    />
                    <Input
                      label="Age"
                      type="number"
                      value={patientInfo.age || ''}
                      onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
                    />
                  </div>
                </div>
                <Button onClick={handleGetRecommendations} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get Recommendations'}
                </Button>
                {results && results.recommendations && (
                  <div className="recommendations-results">
                    <h3>Recommendations</h3>
                    <div className="recommendations-list">
                      {results.recommendations.slice(0, 5).map((rec: any, idx: number) => (
                        <div key={idx} className="recommendation-item">
                          <Heart size={16} />
                          <span>{rec.medication || rec.medication_name || 'Unknown'}</span>
                          {rec.recommendation_score && (
                            <span className="score">
                              {(rec.recommendation_score * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}
          </div>
        </div>

        {error && (
          <Card className="error-card">
            <div className="error-message">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
