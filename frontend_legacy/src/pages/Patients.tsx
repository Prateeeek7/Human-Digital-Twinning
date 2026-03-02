import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import PatientInfoForm from '../components/PatientInfoForm'
import { PatientInfo } from '../services/api'
import { 
  UserPlus, 
  Search, 
  FileText, 
  TrendingUp,
  Activity,
  Pill,
  Target,
  UserCog,
  Upload
} from 'lucide-react'
import './Patients.css'

export default function Patients() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'new' | 'search' | 'upload'>('new')
  const [patientId, setPatientId] = useState<string>('')
  const [patientInfo, setPatientInfo] = useState<PatientInfo>({
    age: undefined,
    sex: '',
    ejection_fraction: undefined,
    systolic_bp: undefined,
    heart_rate: undefined,
    creatinine: undefined,
    diabetes: false,
    high_blood_pressure: false,
  })

  const handleInputChange = (field: string, value: any) => {
    setPatientInfo((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const quickActions = [
    {
      title: 'Get Recommendations',
      description: 'Get personalized medication recommendations',
      icon: Pill,
      action: () => navigate('/recommendations', { state: { patientInfo, patientId } }),
      color: 'var(--color-secondary)',
    },
    {
      title: 'Digital Twin',
      description: 'Initialize and manage patient digital twin',
      icon: UserCog,
      action: () => navigate('/digital-twin', { state: { patientInfo, patientId } }),
      color: 'var(--color-accent)',
    },
    {
      title: 'View History',
      description: 'View temporal data and patient history',
      icon: TrendingUp,
      action: () => navigate('/temporal-data', { state: { patientId } }),
      color: 'var(--color-secondary)',
    },
    {
      title: 'Predictions',
      description: 'Predict outcomes and trajectories',
      icon: Target,
      action: () => navigate('/predictions', { state: { patientInfo } }),
      color: 'var(--color-accent)',
    },
    {
      title: 'Compare Treatments',
      description: 'Compare treatment scenarios',
      icon: Activity,
      action: () => navigate('/comparison', { state: { patientInfo } }),
      color: 'var(--color-secondary)',
    },
  ]

  return (
    <div className="patients-page">
      <div className="page-header">
        <h1>Patient Management</h1>
        <p>Manage patient information and access all patient-related features</p>
      </div>

      <div className="patients-layout">
        <div className="tabs-container">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'new' ? 'active' : ''}`}
              onClick={() => setActiveTab('new')}
            >
              <UserPlus size={18} />
              New Patient
            </button>
            <button
              className={`tab ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={18} />
              Search Patient
            </button>
            <button
              className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <Upload size={18} />
              Upload Documents
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'new' && (
              <div className="new-patient-content">
                <Card title="Patient Information" className="form-card">
                  <div className="patient-id-section">
                    <Input
                      label="Patient ID"
                      type="text"
                      value={patientId}
                      onChange={(e) => setPatientId(e.target.value)}
                      placeholder="Enter patient ID (e.g., P001)"
                    />
                  </div>
                  <PatientInfoForm
                    patientInfo={patientInfo}
                    onChange={handleInputChange}
                    showComorbidities={true}
                  />
                </Card>

                <Card title="Quick Actions" className="actions-card">
                  <div className="quick-actions-grid">
                    {quickActions.map((action, idx) => {
                      const Icon = action.icon
                      return (
                        <button
                          key={idx}
                          className="quick-action-button"
                          onClick={action.action}
                          data-title={action.title}
                          style={{ 
                            borderColor: action.color,
                            '--hover-color': action.color
                          } as React.CSSProperties & { '--hover-color': string }}
                        >
                          <Icon size={20} color={action.color} />
                          <div className="tooltip-description">{action.description}</div>
                        </button>
                      )
                    })}
                  </div>
                </Card>
              </div>
            )}

            {activeTab === 'search' && (
              <Card title="Search Patient" className="tab-card">
                <div className="search-section">
                  <Input
                    label="Patient ID"
                    type="text"
                    value={patientId}
                    onChange={(e) => setPatientId(e.target.value)}
                    placeholder="Enter patient ID to search"
                  />
                  <Button onClick={() => {
                    if (patientId) {
                      navigate('/temporal-data', { state: { patientId } })
                    }
                  }}>
                    <Search size={18} />
                    Search & View History
                  </Button>
                </div>
                {patientId && (
                  <div className="patient-actions">
                    <h3>Available Actions for Patient {patientId}</h3>
                    <div className="quick-actions-grid">
                      {quickActions.map((action, idx) => {
                        const Icon = action.icon
                        return (
                          <button
                            key={idx}
                            className="quick-action-button"
                            onClick={action.action}
                            data-title={action.title}
                            style={{ 
                              borderColor: action.color,
                              '--hover-color': action.color
                            } as React.CSSProperties & { '--hover-color': string }}
                          >
                            <Icon size={20} color={action.color} />
                            <div className="tooltip-description">{action.description}</div>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'upload' && (
              <Card title="Upload Documents" className="tab-card">
                <div className="upload-options">
                  <div className="upload-option">
                    <FileText size={32} />
                    <h3>Prescription / Lab Report</h3>
                    <p>Upload single-page prescriptions or lab reports</p>
                    <Button onClick={() => navigate('/documents')}>
                      Go to Document Upload
                    </Button>
                  </div>
                  <div className="upload-option">
                    <Upload size={32} />
                    <h3>Multi-Page PDF</h3>
                    <p>Upload multi-page PDF reports for temporal data extraction</p>
                    <Button onClick={() => navigate('/temporal-data', { state: { patientId } })}>
                      Go to Temporal Data
                    </Button>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
