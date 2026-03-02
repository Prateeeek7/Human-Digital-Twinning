import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import { 
  Activity, 
  Pill, 
  FileText, 
  GitCompare, 
  TrendingUp, 
  Heart, 
  AlertCircle,
  UserCog,
  Target,
  Database,
  Upload,
  Users
} from 'lucide-react'
import './Dashboard.css'

export default function Dashboard() {
  const navigate = useNavigate()
  
  const [stats] = useState({
    totalPatients: 253680,
    recommendationsGenerated: 12450,
    documentsProcessed: 8900,
    avgAccuracy: 0.85,
  })

  const mainActions = [
    {
      title: 'Patient Management',
      description: 'Manage patient information, upload documents, and access all patient features',
      icon: Users,
      action: () => navigate('/patients'),
      color: 'var(--color-secondary)',
      primary: true,
    },
    {
      title: 'Medication Database',
      description: 'Browse and search comprehensive medication database',
      icon: Database,
      action: () => navigate('/medications'),
      color: 'var(--color-accent)',
      primary: true,
    },
  ]

  const quickActions = [
    {
      title: 'Get Recommendations',
      description: 'Personalized medication recommendations',
      icon: Pill,
      action: () => navigate('/recommendations'),
      color: 'var(--color-secondary)',
    },
    {
      title: 'Compare Treatments',
      description: 'Compare treatment scenarios',
      icon: GitCompare,
      action: () => navigate('/comparison'),
      color: 'var(--color-secondary)',
    },
    {
      title: 'Digital Twin',
      description: 'Patient digital twin management',
      icon: UserCog,
      action: () => navigate('/digital-twin'),
      color: 'var(--color-accent)',
    },
    {
      title: 'Temporal Data',
      description: 'View patient history and time-series data',
      icon: TrendingUp,
      action: () => navigate('/temporal-data'),
      color: 'var(--color-secondary)',
    },
    {
      title: 'Predictions',
      description: 'Predict outcomes and trajectories',
      icon: Target,
      action: () => navigate('/predictions'),
      color: 'var(--color-accent)',
    },
    {
      title: 'Upload Documents',
      description: 'Upload and parse medical documents',
      icon: Upload,
      action: () => navigate('/documents'),
      color: 'var(--color-secondary)',
    },
  ]

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>HF-Digital Twin Platform</h1>
        <p className="subtitle">Hospital-Grade AI for Personalized Medication Recommendations</p>
      </div>

      <div className="stats-grid">
        <Card className="stat-card">
          <div className="stat-content">
            <div className="stat-icon" style={{ background: 'rgba(31, 162, 166, 0.2)' }}>
              <Activity color="var(--color-secondary)" size={24} />
            </div>
            <div className="stat-info">
              <h3>{stats.totalPatients.toLocaleString()}</h3>
              <p>Patients in Database</p>
            </div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-content">
            <div className="stat-icon" style={{ background: 'rgba(92, 184, 92, 0.2)' }}>
              <Pill color="var(--color-accent)" size={24} />
            </div>
            <div className="stat-info">
              <h3>{stats.recommendationsGenerated.toLocaleString()}</h3>
              <p>Recommendations Generated</p>
            </div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-content">
            <div className="stat-icon" style={{ background: 'rgba(31, 162, 166, 0.2)' }}>
              <FileText color="var(--color-secondary)" size={24} />
            </div>
            <div className="stat-info">
              <h3>{stats.documentsProcessed.toLocaleString()}</h3>
              <p>Documents Processed</p>
            </div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-content">
            <div className="stat-icon" style={{ background: 'rgba(92, 184, 92, 0.2)' }}>
              <TrendingUp color="var(--color-accent)" size={24} />
            </div>
            <div className="stat-info">
              <h3>{(stats.avgAccuracy * 100).toFixed(1)}%</h3>
              <p>Average Accuracy</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="main-actions">
        <h2>Main Actions</h2>
        <div className="main-actions-grid">
          {mainActions.map((action) => {
            const Icon = action.icon
            return (
              <div key={action.title} className="main-action-card" onClick={action.action}>
                <Card className="main-action-card-inner">
                  <div className="main-action-content">
                    <div className="main-action-icon" style={{ color: action.color }}>
                      <Icon size={48} />
                    </div>
                    <div>
                      <h3>{action.title}</h3>
                      <p>{action.description}</p>
                    </div>
                    <Button variant="primary" className="main-action-button">
                      Access
                    </Button>
                  </div>
                </Card>
              </div>
            )
          })}
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <div key={action.title} className="action-card" onClick={action.action}>
                <Card className="action-card-inner">
                  <div className="action-icon" style={{ color: action.color }}>
                    <Icon size={32} />
                  </div>
                  <h3>{action.title}</h3>
                  <p>{action.description}</p>
                </Card>
              </div>
            )
          })}
        </div>
      </div>

      <div className="features-section">
        <h2>System Capabilities</h2>
        <div className="features-grid">
          <Card className="feature-card">
            <Heart size={24} color="var(--color-secondary)" />
            <h3>Personalized Recommendations</h3>
            <p>AI-powered medication recommendations based on patient characteristics, lab values, and medical history.</p>
          </Card>

          <Card className="feature-card">
            <FileText size={24} color="var(--color-secondary)" />
            <h3>Document Parsing</h3>
            <p>Automatically extract information from prescriptions and lab reports using OCR technology.</p>
          </Card>

          <Card className="feature-card">
            <GitCompare size={24} color="var(--color-secondary)" />
            <h3>Treatment Comparison</h3>
            <p>Compare multiple treatment scenarios to find the optimal medication combination.</p>
          </Card>

          <Card className="feature-card">
            <AlertCircle size={24} color="var(--color-secondary)" />
            <h3>Drug Interaction Checking</h3>
            <p>Automatically check for drug interactions and contraindications before recommending medications.</p>
          </Card>
        </div>
      </div>
    </div>
  )
}
