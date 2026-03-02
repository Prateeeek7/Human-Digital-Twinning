import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import PatientInfoForm from '../components/PatientInfoForm'
import { predictionsApi, digitalTwinApi, PatientInfo } from '../services/api'
import {
  TrendingUp,
  Activity,
  Heart,
  Target,
  AlertTriangle,
  Info,
  Play,
  BarChart3
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import './Predictions.css'

export default function Predictions() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState<'predict' | 'trajectory' | 'simulate' | 'models'>('predict')
  const [patientData, setPatientData] = useState<PatientInfo>(
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
  const [selectedTasks, setSelectedTasks] = useState<string[]>(['readmission_risk', 'mortality_risk'])
  const [treatment, setTreatment] = useState<string>('')
  const [treatmentDose, setTreatmentDose] = useState<number>(1.0)
  const [timeHorizon, setTimeHorizon] = useState<number>(30)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [hfRisk, setHfRisk] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (field: string, value: any) => {
    setPatientData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    setHfRisk(null)
    try {
      const response = await predictionsApi.predict(patientData, selectedTasks)
      setResults(response)

      // Also fetch the dedicated heart failure risk if applicable vitals exist
      if (patientData.age && patientData.max_hr) {
        const hfResponse = await digitalTwinApi.predictHeartFailure("temp-id", patientData)
        setHfRisk(hfResponse)
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate predictions')
    } finally {
      setLoading(false)
    }
  }

  const handlePredictTrajectory = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await predictionsApi.predictTrajectory(patientData)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to predict trajectory')
    } finally {
      setLoading(false)
    }
  }

  const handleSimulate = async () => {
    if (!treatment) {
      setError('Please enter a treatment')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await predictionsApi.simulateTreatment(
        patientData,
        treatment,
        treatmentDose,
        timeHorizon
      )
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to simulate treatment')
    } finally {
      setLoading(false)
    }
  }

  const handleListModels = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await predictionsApi.listModels()
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to list models')
    } finally {
      setLoading(false)
    }
  }

  // Prepare trajectory chart data
  const prepareTrajectoryData = () => {
    if (!results || !results.trajectory) return []
    const trajectory = results.trajectory
    return trajectory.time_points.map((time: number, idx: number) => ({
      time: time,
      ejection_fraction: trajectory.ejection_fraction ? (trajectory.ejection_fraction[idx] * 100).toFixed(1) : null,
      bnp: trajectory.bnp ? trajectory.bnp[idx] : null,
    }))
  }

  // Prepare simulation chart data
  const prepareSimulationData = () => {
    if (!results || !results.trajectories) return []
    const trajectories = results.trajectories
    return Array.from({ length: timeHorizon }, (_, i) => ({
      day: i + 1,
      ejection_fraction: trajectories.ejection_fraction ? (trajectories.ejection_fraction[i] * 100).toFixed(1) : null,
      mortality_risk: trajectories.mortality_risk ? (trajectories.mortality_risk[i] * 100).toFixed(1) : null,
    }))
  }

  const trajectoryData = prepareTrajectoryData()
  const simulationData = prepareSimulationData()

  return (
    <div className="predictions-page">
      <div className="page-header">
        <h1>Predictions & Simulation</h1>
        <p>Predict patient outcomes, trajectories, and simulate treatment effects</p>
      </div>

      <div className="predictions-layout">
        <div className="tabs-container">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'predict' ? 'active' : ''}`}
              onClick={() => setActiveTab('predict')}
            >
              <Target size={18} />
              Predict Outcomes
            </button>
            <button
              className={`tab ${activeTab === 'trajectory' ? 'active' : ''}`}
              onClick={() => setActiveTab('trajectory')}
            >
              <TrendingUp size={18} />
              Trajectory
            </button>
            <button
              className={`tab ${activeTab === 'simulate' ? 'active' : ''}`}
              onClick={() => setActiveTab('simulate')}
            >
              <Play size={18} />
              Simulate Treatment
            </button>
            <button
              className={`tab ${activeTab === 'models' ? 'active' : ''}`}
              onClick={() => setActiveTab('models')}
            >
              <BarChart3 size={18} />
              Models
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'predict' && (
              <Card title="Predict Patient Outcomes" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Predict patient outcomes including readmission risk, mortality risk, and ejection fraction.</span>
                </div>
                <div className="patient-form">
                  <div className="form-row">
                    <Input
                      label="Age"
                      type="number"
                      value={patientData.age || ''}
                      onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
                      placeholder="65"
                    />
                    <Input
                      label="Sex"
                      type="text"
                      value={patientData.sex || ''}
                      onChange={(e) => handleInputChange('sex', e.target.value)}
                      placeholder="M or F"
                    />
                  </div>
                  <div className="form-row">
                    <Input
                      label="Ejection Fraction (%)"
                      type="number"
                      step="0.01"
                      value={patientData.ejection_fraction ? (patientData.ejection_fraction * 100).toFixed(0) : ''}
                      onChange={(e) => handleInputChange('ejection_fraction', parseFloat(e.target.value) / 100)}
                      placeholder="35"
                    />
                    <Input
                      label="Systolic BP"
                      type="number"
                      value={patientData.systolic_bp || ''}
                      onChange={(e) => handleInputChange('systolic_bp', parseFloat(e.target.value))}
                      placeholder="140"
                    />
                  </div>
                  <div className="form-section">
                    <h3>Prediction Tasks</h3>
                    <div className="checkbox-group">
                      <label className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedTasks.includes('readmission_risk')}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedTasks([...selectedTasks, 'readmission_risk'])
                            } else {
                              setSelectedTasks(selectedTasks.filter(t => t !== 'readmission_risk'))
                            }
                          }}
                        />
                        <span>Readmission Risk</span>
                      </label>
                      <label className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedTasks.includes('mortality_risk')}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedTasks([...selectedTasks, 'mortality_risk'])
                            } else {
                              setSelectedTasks(selectedTasks.filter(t => t !== 'mortality_risk'))
                            }
                          }}
                        />
                        <span>Mortality Risk</span>
                      </label>
                      <label className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedTasks.includes('ejection_fraction')}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedTasks([...selectedTasks, 'ejection_fraction'])
                            } else {
                              setSelectedTasks(selectedTasks.filter(t => t !== 'ejection_fraction'))
                            }
                          }}
                        />
                        <span>Ejection Fraction</span>
                      </label>
                    </div>
                  </div>
                  <Button onClick={handlePredict} disabled={loading}>
                    {loading ? 'Predicting...' : 'Predict Outcomes'}
                  </Button>
                </div>
                {results && results.predictions && (
                  <div className="predictions-results">
                    <h3>Prediction Results</h3>
                    <div className="predictions-grid">
                      {results.predictions.readmission_risk !== undefined && (
                        <div className="prediction-item">
                          <Activity size={24} />
                          <div>
                            <span className="prediction-label">Readmission Risk</span>
                            <span className="prediction-value">
                              {(results.predictions.readmission_risk * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      )}
                      {results.predictions.mortality_risk !== undefined && (
                        <div className="prediction-item">
                          <AlertTriangle size={24} />
                          <div>
                            <span className="prediction-label">Mortality Risk</span>
                            <span className="prediction-value">
                              {(results.predictions.mortality_risk * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      )}
                      {results.predictions.ejection_fraction !== undefined && (
                        <div className="prediction-item">
                          <Heart size={24} />
                          <div>
                            <span className="prediction-label">Ejection Fraction</span>
                            <span className="prediction-value">
                              {(results.predictions.ejection_fraction * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {hfRisk && (
                  <div className="predictions-results" style={{ marginTop: 'var(--spacing-md)', borderTop: '2px solid var(--color-border)', paddingTop: 'var(--spacing-md)' }}>
                    <h3>Heart Failure Risk (ExtraTrees Classifier)</h3>
                    <div className="predictions-grid">
                      <div className={`prediction-item ${hfRisk.has_heart_failure_risk ? 'high-risk' : 'low-risk'}`}>
                        <Heart size={24} color={hfRisk.has_heart_failure_risk ? "var(--color-alert)" : "var(--color-positive)"} />
                        <div>
                          <span className="prediction-label">Failure Probability</span>
                          <span className="prediction-value" style={{ color: hfRisk.has_heart_failure_risk ? "var(--color-alert)" : "var(--color-positive)" }}>
                            {(hfRisk.risk_probability * 100).toFixed(1)}%
                          </span>
                          <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                            Based on model trained with {hfRisk.features_used?.Age}yo, ST Slope: {hfRisk.features_used?.ST_Slope}, MaxHR: {hfRisk.features_used?.MaxHR}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'trajectory' && (
              <Card title="Predict Patient Trajectory" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Predict how patient parameters will change over time.</span>
                </div>
                <PatientInfoForm
                  patientInfo={patientData}
                  onChange={handleInputChange}
                  showComorbidities={false}
                  compact={true}
                />
                <Button onClick={handlePredictTrajectory} disabled={loading} style={{ marginTop: 'var(--spacing-lg)' }}>
                  {loading ? 'Predicting...' : 'Predict Trajectory'}
                </Button>
                {results && results.trajectory && trajectoryData.length > 0 && (
                  <div className="chart-container">
                    <h3>Predicted Trajectory</h3>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={trajectoryData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral)" />
                        <XAxis dataKey="time" stroke="var(--color-text-secondary)" />
                        <YAxis stroke="var(--color-text-secondary)" />
                        <Tooltip
                          contentStyle={{
                            background: 'var(--color-bg-card)',
                            border: '1px solid var(--color-highlight)',
                            borderRadius: 'var(--radius-md)',
                          }}
                        />
                        <Legend />
                        {results.trajectory.ejection_fraction && (
                          <Line
                            type="monotone"
                            dataKey="ejection_fraction"
                            stroke="var(--color-positive)"
                            strokeWidth={2}
                            name="Ejection Fraction (%)"
                            dot={{ r: 4 }}
                          />
                        )}
                        {results.trajectory.bnp && (
                          <Line
                            type="monotone"
                            dataKey="bnp"
                            stroke="var(--color-secondary)"
                            strokeWidth={2}
                            name="BNP"
                            dot={{ r: 4 }}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'simulate' && (
              <Card title="Simulate Treatment Effect" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Simulate the effect of a treatment on patient trajectory.</span>
                </div>
                <div className="patient-form">
                  <div className="form-row">
                    <Input
                      label="Treatment"
                      type="text"
                      value={treatment}
                      onChange={(e) => setTreatment(e.target.value)}
                      placeholder="e.g., ace_inhibitor, beta_blocker"
                    />
                    <Input
                      label="Dose"
                      type="number"
                      step="0.1"
                      value={treatmentDose}
                      onChange={(e) => setTreatmentDose(parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="form-row">
                    <Input
                      label="Time Horizon (days)"
                      type="number"
                      value={timeHorizon}
                      onChange={(e) => setTimeHorizon(parseInt(e.target.value))}
                    />
                    <Input
                      label="Ejection Fraction (%)"
                      type="number"
                      step="0.01"
                      value={patientData.ejection_fraction ? (patientData.ejection_fraction * 100).toFixed(0) : ''}
                      onChange={(e) => handleInputChange('ejection_fraction', parseFloat(e.target.value) / 100)}
                    />
                  </div>
                  <Button onClick={handleSimulate} disabled={loading || !treatment}>
                    {loading ? 'Simulating...' : 'Simulate Treatment'}
                  </Button>
                </div>
                {results && results.trajectories && simulationData.length > 0 && (
                  <div className="chart-container">
                    <h3>Simulated Trajectory: {results.treatment}</h3>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={simulationData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral)" />
                        <XAxis dataKey="day" stroke="var(--color-text-secondary)" />
                        <YAxis stroke="var(--color-text-secondary)" />
                        <Tooltip
                          contentStyle={{
                            background: 'var(--color-bg-card)',
                            border: '1px solid var(--color-highlight)',
                            borderRadius: 'var(--radius-md)',
                          }}
                        />
                        <Legend />
                        {results.trajectories.ejection_fraction && (
                          <Line
                            type="monotone"
                            dataKey="ejection_fraction"
                            stroke="var(--color-positive)"
                            strokeWidth={2}
                            name="Ejection Fraction (%)"
                            dot={{ r: 4 }}
                          />
                        )}
                        {results.trajectories.mortality_risk && (
                          <Line
                            type="monotone"
                            dataKey="mortality_risk"
                            stroke="var(--color-negative)"
                            strokeWidth={2}
                            name="Mortality Risk (%)"
                            dot={{ r: 4 }}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'models' && (
              <Card title="Available Models" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>List all available prediction models and their versions.</span>
                </div>
                <Button onClick={handleListModels} disabled={loading}>
                  {loading ? 'Loading...' : 'List Models'}
                </Button>
                {results && results.models && (
                  <div className="models-list">
                    <h3>Models</h3>
                    <div className="models-grid">
                      {results.models.map((model: any, idx: number) => (
                        <div key={idx} className="model-item">
                          <BarChart3 size={20} />
                          <div>
                            <span className="model-name">{model.name}</span>
                            <span className="model-version">v{model.version}</span>
                          </div>
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
