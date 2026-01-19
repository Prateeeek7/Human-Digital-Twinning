import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import { temporalDataApi } from '../services/api'
import { 
  Upload, 
  FileText, 
  Activity, 
  Heart, 
  AlertTriangle,
  Info,
  CheckCircle
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import './TemporalData.css'

export default function TemporalData() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState<'upload' | 'labs' | 'vitals' | 'summary'>('upload')
  const [patientId, setPatientId] = useState<string>(location.state?.patientId || '')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [referenceDate, setReferenceDate] = useState<string>('')
  const [autoImport, setAutoImport] = useState<boolean>(true)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Filters for labs/vitals
  const [labNames, setLabNames] = useState<string>('')
  const [vitalNames, setVitalNames] = useState<string>('')
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUploadPDF = async () => {
    if (!selectedFile || !patientId) {
      setError('Please select a file and enter patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await temporalDataApi.uploadPDF(
        selectedFile,
        patientId,
        referenceDate || undefined,
        autoImport
      )
      setResults(response)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload PDF')
    } finally {
      setLoading(false)
    }
  }

  const handleGetLabs = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const labList = labNames ? labNames.split(',').map((s: string) => s.trim()) : undefined
      const response = await temporalDataApi.getPatientLabs(
        patientId,
        labList,
        startDate || undefined,
        endDate || undefined
      )
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get lab values')
    } finally {
      setLoading(false)
    }
  }

  const handleGetVitals = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const vitalList = vitalNames ? vitalNames.split(',').map((s: string) => s.trim()) : undefined
      const response = await temporalDataApi.getPatientVitals(
        patientId,
        vitalList,
        startDate || undefined,
        endDate || undefined
      )
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get vitals')
    } finally {
      setLoading(false)
    }
  }

  const handleGetSummary = async () => {
    if (!patientId) {
      setError('Please enter a patient ID')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await temporalDataApi.getPatientSummary(patientId)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get summary')
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data for labs
  const prepareLabChartData = () => {
    if (!results || !results.lab_values) return []
    
    // Group by lab name
    const labGroups: Record<string, any[]> = {}
    results.lab_values.forEach((entry: any) => {
      if (!labGroups[entry.lab_name]) {
        labGroups[entry.lab_name] = []
      }
      labGroups[entry.lab_name].push({
        date: entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : 'Unknown',
        value: entry.value,
        unit: entry.unit || '',
      })
    })

    // Convert to chart format
    const allDates = new Set<string>()
    Object.values(labGroups).forEach((entries: any[]) => {
      entries.forEach((e: any) => allDates.add(e.date))
    })

    const chartData = Array.from(allDates).map(date => {
      const dataPoint: any = { date }
      Object.keys(labGroups).forEach(labName => {
        const entry = labGroups[labName].find((e: any) => e.date === date)
        dataPoint[labName] = entry ? entry.value : null
      })
      return dataPoint
    })

    return chartData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  }

  // Prepare chart data for vitals
  const prepareVitalChartData = () => {
    if (!results || !results.vitals) return []
    
    const vitalGroups: Record<string, any[]> = {}
    results.vitals.forEach((entry: any) => {
      if (!vitalGroups[entry.vital_name]) {
        vitalGroups[entry.vital_name] = []
      }
      vitalGroups[entry.vital_name].push({
        date: entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : 'Unknown',
        value: entry.value,
        unit: entry.unit || '',
      })
    })

    const allDates = new Set<string>()
    Object.values(vitalGroups).forEach((entries: any[]) => {
      entries.forEach((e: any) => allDates.add(e.date))
    })

    const chartData = Array.from(allDates).map(date => {
      const dataPoint: any = { date }
      Object.keys(vitalGroups).forEach(vitalName => {
        const entry = vitalGroups[vitalName].find((e: any) => e.date === date)
        dataPoint[vitalName] = entry ? entry.value : null
      })
      return dataPoint
    })

    return chartData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  }

  const labChartData = prepareLabChartData()
  const vitalChartData = prepareVitalChartData()

  // Get unique lab/vital names for chart colors
  const getLabNames = (): string[] => {
    if (!results || !results.lab_values) return []
    const names = results.lab_values.map((e: any) => e.lab_name as string)
    return Array.from(new Set(names)) as string[]
  }

  const getVitalNames = (): string[] => {
    if (!results || !results.vitals) return []
    const names = results.vitals.map((e: any) => e.vital_name as string)
    return Array.from(new Set(names)) as string[]
  }

  const colors = ['#1fa2a6', '#5cb85c', '#f0ad4e', '#d9534f', '#5bc0de', '#9b59b6', '#e74c3c']

  return (
    <div className="temporal-data-page">
      <div className="page-header">
        <h1>Temporal Data & Patient History</h1>
        <p>Upload multi-page PDFs, extract temporal data, and visualize time-series lab values and vitals</p>
      </div>

      <div className="temporal-data-layout">
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
              className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <Upload size={18} />
              Upload PDF
            </button>
            <button
              className={`tab ${activeTab === 'labs' ? 'active' : ''}`}
              onClick={() => setActiveTab('labs')}
            >
              <Activity size={18} />
              Lab Values
            </button>
            <button
              className={`tab ${activeTab === 'vitals' ? 'active' : ''}`}
              onClick={() => setActiveTab('vitals')}
            >
              <Heart size={18} />
              Vitals
            </button>
            <button
              className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              <FileText size={18} />
              Summary
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'upload' && (
              <Card title="Upload Multi-Page PDF" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Upload PDF reports (100s of pages) to extract temporal lab values and vitals with dates.</span>
                </div>
                <div className="upload-form">
                  <div className="file-upload">
                    <label className="file-label">
                      <Upload size={20} />
                      <span>{selectedFile ? selectedFile.name : 'Choose PDF file'}</span>
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="file-input"
                      />
                    </label>
                  </div>
                  <Input
                    label="Reference Date (Optional)"
                    type="date"
                    value={referenceDate}
                    onChange={(e) => setReferenceDate(e.target.value)}
                  />
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={autoImport}
                        onChange={(e) => setAutoImport(e.target.checked)}
                      />
                      <span>Auto-import to database</span>
                    </label>
                  </div>
                  <Button onClick={handleUploadPDF} disabled={loading || !selectedFile || !patientId}>
                    {loading ? 'Uploading...' : 'Upload & Extract'}
                  </Button>
                </div>
                {results && (
                  <div className="upload-results">
                    <div className="result-section">
                      <h3>Extraction Results</h3>
                      <div className="result-grid">
                        <div className="result-item">
                          <span className="result-label">Lab Values Extracted:</span>
                          <span className="result-value">{results.lab_values_count || 0}</span>
                        </div>
                        <div className="result-item">
                          <span className="result-label">Vitals Extracted:</span>
                          <span className="result-value">{results.vitals_count || 0}</span>
                        </div>
                        <div className="result-item">
                          <span className="result-label">Total Pages:</span>
                          <span className="result-value">{results.document_metadata?.total_pages || 0}</span>
                        </div>
                        {results.imported && (
                          <div className="result-item success">
                            <CheckCircle size={16} />
                            <span>Data imported to database</span>
                          </div>
                        )}
                      </div>
                      {results.extraction_quality && (
                        <div className="quality-metrics">
                          <h4>Extraction Quality</h4>
                          <div className="quality-item">
                            <span>Completeness:</span>
                            <span>{(results.extraction_quality.extraction_completeness * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'labs' && (
              <Card title="Time-Series Lab Values" className="tab-card">
                <div className="filters">
                  <Input
                    label="Lab Names (comma-separated, optional)"
                    type="text"
                    value={labNames}
                    onChange={(e) => setLabNames(e.target.value)}
                    placeholder="e.g., Creatinine, BNP, Sodium"
                  />
                  <div className="date-filters">
                    <Input
                      label="Start Date"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                    <Input
                      label="End Date"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={handleGetLabs} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get Lab Values'}
                </Button>
                {results && results.lab_values && (
                  <div className="chart-container">
                    <h3>Lab Values Over Time</h3>
                    {labChartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={labChartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral)" />
                          <XAxis dataKey="date" stroke="var(--color-text-secondary)" />
                          <YAxis stroke="var(--color-text-secondary)" />
                          <Tooltip
                            contentStyle={{
                              background: 'var(--color-bg-card)',
                              border: '1px solid var(--color-highlight)',
                              borderRadius: 'var(--radius-md)',
                            }}
                          />
                          <Legend />
                          {getLabNames().map((labName: string, idx: number) => (
                            <Line
                              key={labName}
                              type="monotone"
                              dataKey={labName as string}
                              stroke={colors[idx % colors.length]}
                              strokeWidth={2}
                              dot={{ r: 4 }}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="no-data">No data to display</p>
                    )}
                    <div className="data-summary">
                      <span>Total entries: {results.count}</span>
                      {results.date_range && (
                        <span>
                          Date range: {new Date(results.date_range.earliest).toLocaleDateString()} - {new Date(results.date_range.latest).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'vitals' && (
              <Card title="Time-Series Vital Signs" className="tab-card">
                <div className="filters">
                  <Input
                    label="Vital Names (comma-separated, optional)"
                    type="text"
                    value={vitalNames}
                    onChange={(e) => setVitalNames(e.target.value)}
                    placeholder="e.g., Heart Rate, Blood Pressure, Temperature"
                  />
                  <div className="date-filters">
                    <Input
                      label="Start Date"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                    <Input
                      label="End Date"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={handleGetVitals} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get Vitals'}
                </Button>
                {results && results.vitals && (
                  <div className="chart-container">
                    <h3>Vital Signs Over Time</h3>
                    {vitalChartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={vitalChartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral)" />
                          <XAxis dataKey="date" stroke="var(--color-text-secondary)" />
                          <YAxis stroke="var(--color-text-secondary)" />
                          <Tooltip
                            contentStyle={{
                              background: 'var(--color-bg-card)',
                              border: '1px solid var(--color-highlight)',
                              borderRadius: 'var(--radius-md)',
                            }}
                          />
                          <Legend />
                          {getVitalNames().map((vitalName: string, idx: number) => (
                            <Line
                              key={vitalName}
                              type="monotone"
                              dataKey={vitalName as string}
                              stroke={colors[idx % colors.length]}
                              strokeWidth={2}
                              dot={{ r: 4 }}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="no-data">No data to display</p>
                    )}
                    <div className="data-summary">
                      <span>Total entries: {results.count}</span>
                      {results.date_range && (
                        <span>
                          Date range: {new Date(results.date_range.earliest).toLocaleDateString()} - {new Date(results.date_range.latest).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'summary' && (
              <Card title="Patient Temporal Summary" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Get a comprehensive summary of all temporal data for a patient.</span>
                </div>
                <Button onClick={handleGetSummary} disabled={loading || !patientId}>
                  {loading ? 'Loading...' : 'Get Summary'}
                </Button>
                {results && (
                  <div className="summary-results">
                    <h3>Patient Summary</h3>
                    <div className="summary-grid">
                      {results.lab_values_count !== undefined && (
                        <div className="summary-item">
                          <Activity size={20} />
                          <div>
                            <span className="summary-label">Lab Values</span>
                            <span className="summary-value">{results.lab_values_count}</span>
                          </div>
                        </div>
                      )}
                      {results.vitals_count !== undefined && (
                        <div className="summary-item">
                          <Heart size={20} />
                          <div>
                            <span className="summary-label">Vitals</span>
                            <span className="summary-value">{results.vitals_count}</span>
                          </div>
                        </div>
                      )}
                      {results.medications_count !== undefined && (
                        <div className="summary-item">
                          <FileText size={20} />
                          <div>
                            <span className="summary-label">Medications</span>
                            <span className="summary-value">{results.medications_count}</span>
                          </div>
                        </div>
                      )}
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
