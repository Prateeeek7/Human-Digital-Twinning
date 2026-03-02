import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import PatientInfoForm from '../components/PatientInfoForm'
import { recommendationsApi, medicationsApi, PatientInfo } from '../services/api'
import { GitCompare, Plus, X, TrendingUp, AlertTriangle, Shield, Award, BarChart3, Pill, Heart } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './TreatmentComparison.css'

export default function TreatmentComparison() {
  const location = useLocation()
  const [patientInfo, setPatientInfo] = useState<PatientInfo>(
    (location.state?.patientInfo as PatientInfo) || {
      age: 65,
      sex: 'M',
      ejection_fraction: 0.35,
      systolic_bp: 140,
    }
  )
  const [scenarios, setScenarios] = useState<Array<{ medications: string[]; dosages: Record<string, number> }>>([
    { medications: ['ace_inhibitor', 'beta_blocker'], dosages: {} },
    { medications: ['arni', 'beta_blocker'], dosages: {} },
  ])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [medicationSearchQuery, setMedicationSearchQuery] = useState<Record<number, string>>({})
  const [medicationSearchResults, setMedicationSearchResults] = useState<Record<number, any[]>>({})
  const [, setSearchingMedications] = useState<Record<number, boolean>>({})

  const handleInputChange = (field: string, value: any) => {
    setPatientInfo((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const addScenario = () => {
    setScenarios([...scenarios, { medications: [], dosages: {} }])
  }

  const removeScenario = (index: number) => {
    setScenarios(scenarios.filter((_, i) => i !== index))
  }

  const searchMedications = async (query: string, scenarioIndex: number) => {
    if (query.length < 2) {
      setMedicationSearchResults(prev => ({ ...prev, [scenarioIndex]: [] }))
      return
    }
    setSearchingMedications(prev => ({ ...prev, [scenarioIndex]: true }))
    try {
      const response = await medicationsApi.search(query, 10)
      setMedicationSearchResults(prev => ({ ...prev, [scenarioIndex]: response.medications || [] }))
    } catch (err) {
      console.error('Error searching medications:', err)
      setMedicationSearchResults(prev => ({ ...prev, [scenarioIndex]: [] }))
    } finally {
      setSearchingMedications(prev => ({ ...prev, [scenarioIndex]: false }))
    }
  }

  const addMedicationToScenario = (scenarioIndex: number, medicationName?: string) => {
    const med = medicationName || prompt('Enter medication name (e.g., Lisinopril, Metoprolol):')
    if (med) {
      const newScenarios = [...scenarios]
      newScenarios[scenarioIndex].medications.push(med)
      setScenarios(newScenarios)
      setMedicationSearchQuery(prev => ({ ...prev, [scenarioIndex]: '' }))
      setMedicationSearchResults(prev => ({ ...prev, [scenarioIndex]: [] }))
    }
  }

  const removeMedicationFromScenario = (scenarioIndex: number, medIndex: number) => {
    const newScenarios = [...scenarios]
    newScenarios[scenarioIndex].medications.splice(medIndex, 1)
    setScenarios(newScenarios)
  }

  const handleCompare = async () => {
    setLoading(true)
    setError(null)
    setResults([])

    // Client-side validation
    if (!patientInfo.age || patientInfo.age === undefined) {
      setError('Please provide patient age. Age is required for accurate scenario comparison.')
      setLoading(false)
      return
    }

    if (!scenarios || scenarios.length === 0) {
      setError('Please add at least one treatment scenario to compare.')
      setLoading(false)
      return
    }

    for (let i = 0; i < scenarios.length; i++) {
      if (!scenarios[i].medications || scenarios[i].medications.length === 0) {
        setError(`Scenario ${i + 1} has no medications. Please add medications to each scenario.`)
        setLoading(false)
        return
      }
    }

    try {
      // Convert scenarios to combination format
      const combinations = scenarios.map(s => ({
        medications: s.medications,
        dosages: s.dosages || {}
      }))
      
      // Use enhanced combination comparison
      const response = await recommendationsApi.compareCombinations(patientInfo, combinations)
      if (!response || !response.comparisons || response.comparisons.length === 0) {
        setError('No comparison results generated. Please check your input data.')
        setResults([])
      } else {
        setResults(response.comparisons)
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to compare scenarios'
      setError(errorMessage)
      setResults([]) // Clear any previous results
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const chartData = results.map((scenario, idx) => ({
    name: `Scenario ${idx + 1}`,
    benefit: scenario.success_rate ? (scenario.success_rate * 100) : (scenario.total_benefit || 0),
    successRate: scenario.success_rate ? (scenario.success_rate * 100) : 0,
    medications: scenario.medication_names?.join(', ') || scenario.medications?.join(', ') || '',
  }))

  return (
    <div className="treatment-comparison-page">
      <div className="page-header">
        <h1>Treatment Scenario Comparison</h1>
        <p>Compare multiple treatment scenarios side-by-side to identify the optimal medication combination</p>
      </div>

      <div className="comparison-layout">
        <Card title="Patient Information" className="patient-card">
          <PatientInfoForm
            patientInfo={patientInfo}
            onChange={handleInputChange}
            showComorbidities={false}
            compact={true}
          />
        </Card>

        <Card title="Treatment Scenarios" className="scenarios-card">
          <div className="card-info">
            <GitCompare size={16} />
            <span>Create multiple scenarios to compare different medication combinations</span>
          </div>
          <div className="scenarios-list">
            {scenarios.map((scenario, scenarioIdx) => (
              <div key={scenarioIdx} className="scenario-item">
                <div className="scenario-header">
                  <div>
                    <h3>
                      <Award size={18} />
                      Scenario {scenarioIdx + 1}
                    </h3>
                    <p className="scenario-subtitle">Medication combination {scenarioIdx + 1}</p>
                  </div>
                  {scenarios.length > 1 && (
                    <button
                      className="remove-scenario"
                      onClick={() => removeScenario(scenarioIdx)}
                      title="Remove scenario"
                    >
                      <X size={20} />
                    </button>
                  )}
                </div>
                <div className="scenario-medications">
                  {scenario.medications.length > 0 ? (
                    scenario.medications.map((med, medIdx) => (
                      <span key={medIdx} className="med-tag">
                        {med.replace(/_/g, ' ')}
                        <button
                          onClick={() => removeMedicationFromScenario(scenarioIdx, medIdx)}
                          className="remove-med"
                          title="Remove medication"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  ) : (
                    <p className="empty-scenario">No medications added to this scenario</p>
                  )}
                  <div className="add-medication-section">
                    <div className="medication-search">
                      <Input
                        type="text"
                        placeholder="Search medications (e.g., Lisinopril, Metoprolol)"
                        value={medicationSearchQuery[scenarioIdx] || ''}
                        onChange={(e) => {
                          const query = e.target.value
                          setMedicationSearchQuery(prev => ({ ...prev, [scenarioIdx]: query }))
                          searchMedications(query, scenarioIdx)
                        }}
                        onFocus={() => {
                          const query = medicationSearchQuery[scenarioIdx] || ''
                          if (query.length >= 2) {
                            searchMedications(query, scenarioIdx)
                          }
                        }}
                      />
                      {medicationSearchResults[scenarioIdx] && medicationSearchResults[scenarioIdx].length > 0 && (
                        <div className="medication-search-results">
                          {medicationSearchResults[scenarioIdx].map((med: any, medIdx: number) => (
                            <div
                              key={medIdx}
                              className="medication-search-item"
                              onClick={() => addMedicationToScenario(scenarioIdx, med.name)}
                            >
                              <Pill size={14} />
                              <div>
                                <strong>{med.name}</strong>
                                {med.category && (
                                  <span className="med-category">{med.category.replace(/_/g, ' ')}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      {medicationSearchResults[scenarioIdx] && Array.isArray(medicationSearchResults[scenarioIdx]) && medicationSearchResults[scenarioIdx].length > 0 && (
                        <div className="medication-search-results">
                          {medicationSearchResults[scenarioIdx].map((med: any, medIdx: number) => (
                            <div
                              key={medIdx}
                              className="medication-search-item"
                              onClick={() => addMedicationToScenario(scenarioIdx, med.name)}
                            >
                              <Pill size={14} />
                              <div>
                                <strong>{med.name}</strong>
                                {med.category && (
                                  <span className="med-category">{med.category.replace(/_/g, ' ')}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => addMedicationToScenario(scenarioIdx)}
                    >
                      <Plus size={16} />
                      Add Medication Manually
                    </Button>
                  </div>
                </div>
                {scenario.medications.length > 0 && (
                  <div className="scenario-count">
                    <Pill size={14} />
                    <span>{scenario.medications.length} medication(s)</span>
                  </div>
                )}
              </div>
            ))}
            <Button variant="secondary" onClick={addScenario} className="add-scenario-btn">
              <Plus size={20} />
              Add New Scenario
            </Button>
          </div>
        </Card>

        {error && (
          <div className="error-message">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}

        <Button
          variant="primary"
          size="lg"
          onClick={handleCompare}
          isLoading={loading}
          className="compare-button"
        >
          <GitCompare size={20} />
          Compare Scenarios
        </Button>

        {results.length > 0 && (
          <div className="results-section">
            <Card title="Comparison Results" className="results-card">
              <div className="results-summary">
                <div className="summary-item">
                  <BarChart3 size={20} color="var(--color-highlight)" />
                  <div>
                    <strong>{results.length}</strong> scenario(s) compared
                  </div>
                </div>
                <div className="summary-item">
                  <Award size={20} color="var(--color-positive)" />
                  <div>
                    Best: <strong>Scenario {results.findIndex(r => (r.success_rate || r.total_benefit || 0) === Math.max(...results.map(r => r.success_rate || r.total_benefit || 0))) + 1}</strong>
                  </div>
                </div>
              </div>
              <div className="comparison-chart">
                <h4>Success Rate Comparison</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral)" />
                    <XAxis dataKey="name" stroke="var(--color-text-secondary)" />
                    <YAxis stroke="var(--color-text-secondary)" label={{ value: 'Success Rate (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--color-bg-card)',
                        border: '1px solid var(--color-highlight)',
                        borderRadius: 'var(--radius-md)',
                      }}
                    />
                    <Bar dataKey={chartData[0]?.successRate ? "successRate" : "benefit"} fill="var(--color-highlight)" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <div className="scenarios-results">
              {results.map((scenario, idx) => {
                const maxSuccess = Math.max(...results.map(r => r.success_rate || r.total_benefit || 0))
                const isBest = (scenario.success_rate || scenario.total_benefit || 0) === maxSuccess
                const successRate = scenario.success_rate ? (scenario.success_rate * 100) : null
                const medications = scenario.medication_names || scenario.medications || []
                
                return (
                  <Card
                    key={idx}
                    title={
                      <div className="scenario-title">
                        <span>Scenario {idx + 1}</span>
                        {isBest && (
                          <span className="best-badge">
                            <Award size={16} />
                            Best Option
                          </span>
                        )}
                      </div>
                    }
                    className={`scenario-result ${scenario.is_safe !== false ? 'safe' : 'unsafe'} ${isBest ? 'best' : ''}`}
                  >
                    <div className="scenario-meds-display">
                      <strong>Medications:</strong>
                      <div className="meds-list">
                        {medications.map((med: string, i: number) => (
                          <span key={i} className="med-display-tag">
                            {med.replace(/_/g, ' ')}
                            {scenario.dosages && scenario.dosages[med] && (
                              <span className="dosage-badge">{scenario.dosages[med]}</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="scenario-metrics">
                      {successRate !== null ? (
                        <div className="metric">
                          <TrendingUp size={20} color="var(--color-highlight)" />
                          <div className="metric-content">
                            <span className="metric-label">Success Rate</span>
                            <span className="metric-value positive">
                              {successRate.toFixed(1)}%
                            </span>
                            <span className="metric-description">Predicted success probability</span>
                          </div>
                        </div>
                      ) : (
                        <div className="metric">
                          <TrendingUp size={20} color="var(--color-highlight)" />
                          <div className="metric-content">
                            <span className="metric-label">Total Benefit</span>
                            <span className="metric-value positive">
                              {scenario.total_benefit?.toFixed(2) || 'N/A'}
                            </span>
                            <span className="metric-description">Combined benefit score</span>
                          </div>
                        </div>
                      )}
                      <div className="metric">
                        <Shield size={20} color={scenario.is_safe !== false ? "var(--color-positive)" : "var(--color-negative)"} />
                        <div className="metric-content">
                          <span className="metric-label">Safety Status</span>
                          <span className={`metric-value ${scenario.is_safe !== false ? 'positive' : 'negative'}`}>
                            {scenario.is_safe !== false ? 'Safe' : 'Has Interactions'}
                          </span>
                          <span className="metric-description">
                            {scenario.is_safe !== false ? 'No severe interactions detected' : 'Review interactions below'}
                          </span>
                        </div>
                      </div>
                      {scenario.expected_outcomes && (
                        <div className="metric">
                          <Heart size={20} color="var(--color-accent)" />
                          <div className="metric-content">
                            <span className="metric-label">EF Improvement</span>
                            <span className="metric-value positive">
                              +{((scenario.expected_outcomes.ejection_fraction_improvement || 0) * 100).toFixed(1)}%
                            </span>
                            <span className="metric-description">Expected ejection fraction change</span>
                          </div>
                        </div>
                      )}
                    </div>
                    {scenario.interactions && scenario.interactions.length > 0 && (
                      <div className="interactions-list">
                        <div className="interactions-header">
                          <AlertTriangle size={18} />
                          <strong>Drug Interactions Detected ({scenario.interactions.length})</strong>
                        </div>
                        <ul>
                          {scenario.interactions.map((interaction: any, i: number) => (
                            <li key={i}>
                              <span className="interaction-meds">
                                {interaction.medication1} + {interaction.medication2}
                              </span>
                              <span className={`interaction-severity ${interaction.severity}`}>
                                {interaction.severity}
                              </span>
                              <div className="interaction-details">
                                <span>{interaction.effect}</span>
                                {interaction.action && <span className="interaction-action">Action: {interaction.action}</span>}
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {scenario.effects && scenario.effects.length > 0 && (
                      <div className="scenario-effects">
                        <strong>Predicted Effects:</strong>
                        <div className="effects-list">
                          {scenario.effects.map((effect: any, i: number) => (
                            <div key={i} className="effect-item">
                              {effect.predicted_effects && (
                                <>
                                  {effect.predicted_effects.ejection_fraction && (
                                    <span>EF: {(effect.predicted_effects.ejection_fraction * 100).toFixed(1)}%</span>
                                  )}
                                  {effect.predicted_effects.mortality_risk && (
                                    <span>Mortality Risk: {(effect.predicted_effects.mortality_risk * 100).toFixed(1)}%</span>
                                  )}
                                </>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </Card>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

