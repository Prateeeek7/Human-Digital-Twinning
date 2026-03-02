import { CheckCircle, AlertTriangle, TrendingUp, Pill, Info, Heart, Activity, Award, Shield } from 'lucide-react'
import Card from './Card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './RecommendationResults.css'

interface RecommendationResultsProps {
  results: any
}

export default function RecommendationResults({ results }: RecommendationResultsProps) {
  // Check if this is enhanced recommendations (has specific_recommendations)
  const isEnhanced = results.specific_recommendations !== undefined
  
  if (isEnhanced) {
    return <EnhancedRecommendationResults results={results} />
  } else {
    return <StandardRecommendationResults results={results} />
  }
}

function EnhancedRecommendationResults({ results }: { results: any }) {
  const specificRecommendations = results.specific_recommendations || []
  const optimalCombinations = results.optimal_combinations || []
  const topRecommendation = specificRecommendations[0]

  return (
    <div className="recommendation-results">
      {topRecommendation && (
        <Card title="Top Recommendation" className="top-recommendation">
          <div className="recommendation-header">
            <div className="med-name">
              <Pill size={24} color="var(--color-secondary)" />
              <div>
                <h2>{topRecommendation.medication_name}</h2>
                <p className="med-category">{topRecommendation.category?.replace(/_/g, ' ').toUpperCase() || 'Medication'}</p>
              </div>
            </div>
            <div className="safety-badge safe">
              <CheckCircle size={16} />
              <span>Available</span>
            </div>
          </div>

          <div className="recommendation-description">
            <Info size={16} />
            <p>Specific medication recommendation with dosage information based on patient profile and clinical guidelines.</p>
          </div>

          <div className="recommendation-metrics">
            <div className="metric">
              <div className="metric-icon">
                <Pill size={20} />
              </div>
              <div className="metric-content">
                <span className="metric-label">Recommended Dosage</span>
                <span className="metric-value">
                  {topRecommendation.recommended_dosage || 'N/A'}
                </span>
                <span className="metric-description">{topRecommendation.frequency || 'daily'}</span>
              </div>
            </div>
            {topRecommendation.strength && (
              <div className="metric">
                <div className="metric-icon">
                  <Activity size={20} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Strength</span>
                  <span className="metric-value">{topRecommendation.strength}</span>
                  <span className="metric-description">{topRecommendation.dosage_form || 'Oral'}</span>
                </div>
              </div>
            )}
            <div className="metric">
              <div className="metric-icon positive">
                <TrendingUp size={20} />
              </div>
              <div className="metric-content">
                <span className="metric-label">Recommendation Score</span>
                <span className="metric-value positive">
                  {(topRecommendation.recommendation_score * 100).toFixed(1)}%
                </span>
                <span className="metric-description">Confidence in recommendation</span>
              </div>
            </div>
            <div className="metric">
              <div className="metric-icon positive">
                <Heart size={20} />
              </div>
              <div className="metric-content">
                <span className="metric-label">Expected Benefit</span>
                <span className="metric-value positive">
                  +{topRecommendation.expected_benefit?.toFixed(2) || 'N/A'}
                </span>
                <span className="metric-description">Predicted improvement score</span>
              </div>
            </div>
          </div>

          {topRecommendation.indications && (
            <div className="medication-details">
              <strong>Indications:</strong> {topRecommendation.indications}
            </div>
          )}
          {topRecommendation.contraindications && (
            <div className="medication-details warning">
              <strong>Contraindications:</strong> {topRecommendation.contraindications}
            </div>
          )}
        </Card>
      )}

      {optimalCombinations.length > 0 && (
        <Card title="Optimal Medication Combinations" className="optimal-combinations">
          <div className="combinations-list">
            {optimalCombinations.map((combo: any, idx: number) => (
              <div key={idx} className={`combination-card ${idx === 0 ? 'best' : ''}`}>
                {idx === 0 && (
                  <div className="best-badge">
                    <Award size={16} />
                    <span>Best Option</span>
                  </div>
                )}
                <div className="combination-header">
                  <h3>Combination {idx + 1}</h3>
                  <div className="success-rate-badge">
                    <TrendingUp size={16} />
                    <span>{(combo.success_rate * 100).toFixed(1)}% Success Rate</span>
                  </div>
                </div>
                
                <div className="combination-medications">
                  {combo.medication_names?.map((med: string, medIdx: number) => (
                    <div key={medIdx} className="med-item">
                      <Pill size={16} />
                      <div>
                        <strong>{med}</strong>
                        {combo.dosages && combo.dosages[med] && (
                          <span className="dosage-info">{combo.dosages[med]}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {combo.expected_outcomes && (
                  <div className="expected-outcomes">
                    <strong>Expected Outcomes:</strong>
                    <div className="outcomes-grid">
                      {combo.expected_outcomes.ejection_fraction_improvement && (
                        <div className="outcome-item">
                          <span className="outcome-label">EF Improvement:</span>
                          <span className="outcome-value positive">
                            +{(combo.expected_outcomes.ejection_fraction_improvement * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {combo.expected_outcomes.mortality_reduction && (
                        <div className="outcome-item">
                          <span className="outcome-label">Mortality Reduction:</span>
                          <span className="outcome-value positive">
                            {(combo.expected_outcomes.mortality_reduction * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {combo.expected_outcomes.readmission_reduction && (
                        <div className="outcome-item">
                          <span className="outcome-label">Readmission Reduction:</span>
                          <span className="outcome-value positive">
                            {(combo.expected_outcomes.readmission_reduction * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {combo.interactions && combo.interactions.length > 0 && (
                  <div className="interactions-warning">
                    <AlertTriangle size={16} color="var(--color-alert)" />
                    <div>
                      <strong>Interactions ({combo.interactions.length}):</strong>
                      <ul>
                        {combo.interactions.slice(0, 3).map((interaction: any, i: number) => (
                          <li key={i}>
                            {interaction.medication1_name} + {interaction.medication2_name}: {interaction.severity}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                <div className="combination-confidence">
                  <Shield size={14} />
                  <span>Confidence: {combo.confidence || 'medium'}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {specificRecommendations.length > 0 && (
        <Card title="All Recommended Medications" className="all-recommendations">
          <div className="recommendations-list">
            {specificRecommendations.slice(0, 10).map((rec: any, idx: number) => (
              <div key={idx} className="recommendation-item">
                <div className="rec-header">
                  <div>
                    <span className="rec-name">{rec.medication_name}</span>
                    <span className="rec-category">{rec.category?.replace(/_/g, ' ')}</span>
                  </div>
                  <span className={`rec-score ${rec.recommendation_score > 0.7 ? 'high' : 'medium'}`}>
                    {(rec.recommendation_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="rec-details">
                  <span className="dosage-display">
                    <Pill size={14} />
                    {rec.recommended_dosage || 'Dosage TBD'}
                  </span>
                  <span>Benefit: {rec.expected_benefit?.toFixed(2) || 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}

function StandardRecommendationResults({ results }: { results: any }) {
  const topRecommendation = results.summary?.top_recommendation
  const optimalCombination = results.optimal_combination
  const recommendations = results.recommendations || []

  // Prepare trajectory data for chart
  const trajectoryData = topRecommendation?.predicted_effect?.trajectories
    ? topRecommendation.predicted_effect.trajectories.time_days.map((day: number, index: number) => ({
        day,
        ef: (topRecommendation.predicted_effect.trajectories.ejection_fraction[index] * 100).toFixed(1),
        mortality: (topRecommendation.predicted_effect.trajectories.mortality_risk[index] * 100).toFixed(1),
      }))
    : []

  return (
    <div className="recommendation-results">
      {topRecommendation && (
        <Card title="Top Recommendation" className="top-recommendation">
          <div className="recommendation-header">
            <div className="med-name">
              <Pill size={24} color="var(--color-secondary)" />
              <div>
                <h2>{topRecommendation.medication.replace(/_/g, ' ').toUpperCase()}</h2>
                <p className="med-category">Medication Category</p>
              </div>
            </div>
            <div className={`safety-badge ${topRecommendation.is_safe ? 'safe' : 'unsafe'}`}>
              {topRecommendation.is_safe ? (
                <>
                  <CheckCircle size={16} />
                  <span>Safe to Use</span>
                </>
              ) : (
                <>
                  <AlertTriangle size={16} />
                  <span>Has Interactions</span>
                </>
              )}
            </div>
          </div>

          <div className="recommendation-description">
            <Info size={16} />
            <p>This medication is recommended based on the patient's profile, clinical guidelines, and analysis of 253,680+ patient records.</p>
          </div>

          <div className="recommendation-metrics">
            <div className="metric">
              <div className="metric-icon">
                <TrendingUp size={20} />
              </div>
              <div className="metric-content">
                <span className="metric-label">Recommendation Score</span>
                <span className="metric-value">
                  {(topRecommendation.recommendation_score * 100).toFixed(1)}%
                </span>
                <span className="metric-description">Confidence in recommendation</span>
              </div>
            </div>
            <div className="metric">
              <div className="metric-icon positive">
                <Heart size={20} />
              </div>
              <div className="metric-content">
                <span className="metric-label">Expected Benefit</span>
                <span className="metric-value positive">
                  +{topRecommendation.expected_benefit.toFixed(2)}
                </span>
                <span className="metric-description">Predicted improvement score</span>
              </div>
            </div>
            {topRecommendation.optimal_dose && (
              <div className="metric">
                <div className="metric-icon">
                  <Pill size={20} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Optimal Dose</span>
                  <span className="metric-value">{topRecommendation.optimal_dose.toFixed(2)}</span>
                  <span className="metric-description">Recommended dosage (normalized)</span>
                </div>
              </div>
            )}
            {topRecommendation.predicted_effect?.predicted_effects && (
              <div className="metric">
                <div className="metric-icon">
                  <Activity size={20} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">EF Improvement</span>
                  <span className="metric-value positive">
                    +{((topRecommendation.predicted_effect.predicted_effects.ejection_fraction || 0) * 100).toFixed(1)}%
                  </span>
                  <span className="metric-description">Expected ejection fraction change</span>
                </div>
              </div>
            )}
          </div>

          {topRecommendation.interactions && topRecommendation.interactions.length > 0 && (
            <div className="interactions-warning">
              <AlertTriangle size={20} color="var(--color-alert)" />
              <div>
                <strong>Interactions Detected:</strong>
                <ul>
                  {topRecommendation.interactions.map((interaction: any, idx: number) => (
                    <li key={idx}>
                      {interaction.medication1} + {interaction.medication2}: {interaction.severity} - {interaction.effect}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </Card>
      )}

      {optimalCombination && optimalCombination.medications.length > 0 && (
        <Card title="Optimal Combination" className="optimal-combination">
          <div className="combination-meds">
            {optimalCombination.medications.map((med: string, idx: number) => (
              <span key={idx} className="med-badge">
                {med.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
          <div className="combination-benefit">
            <TrendingUp size={20} color="var(--color-accent)" />
            <span>Total Benefit: {optimalCombination.total_benefit.toFixed(2)}</span>
          </div>
        </Card>
      )}

      {trajectoryData.length > 0 && (
        <Card title="Predicted Trajectory (90 days)" className="trajectory-card">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trajectoryData}>
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
              <Line
                type="monotone"
                dataKey="ef"
                stroke="var(--color-positive)"
                strokeWidth={2}
                name="Ejection Fraction (%)"
              />
              <Line
                type="monotone"
                dataKey="mortality"
                stroke="var(--color-negative)"
                strokeWidth={2}
                name="Mortality Risk (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      {recommendations.length > 0 && (
        <Card title="All Recommendations" className="all-recommendations">
          <div className="recommendations-list">
            {recommendations.slice(0, 5).map((rec: any, idx: number) => (
              <div key={idx} className="recommendation-item">
                <div className="rec-header">
                  <span className="rec-name">{rec.medication.replace(/_/g, ' ')}</span>
                  <span className={`rec-score ${rec.recommendation_score > 0.7 ? 'high' : 'medium'}`}>
                    {(rec.recommendation_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="rec-details">
                  <span>Benefit: {rec.expected_benefit?.toFixed(2) || 'N/A'}</span>
                  {rec.is_safe === false && (
                    <span className="warning">⚠ Has interactions</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
