import { useState, useEffect } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import { medicationsApi } from '../services/api'
import { 
  Search, 
  Pill, 
  Database, 
  Loader2,
  AlertTriangle,
  Info,
  CheckCircle,
  Filter
} from 'lucide-react'
import './MedicationDatabase.css'

const MEDICATION_CATEGORIES = [
  'ace_inhibitor',
  'arb',
  'arni',
  'beta_blocker',
  'diuretic',
  'aldosterone_antagonist',
  'digoxin',
  'anticoagulant',
]

export default function MedicationDatabase() {
  const [activeTab, setActiveTab] = useState<'search' | 'category' | 'details' | 'load'>('search')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [, setSelectedMedication] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [medicationDetails, setMedicationDetails] = useState<any>(null)

  const handleSearch = async () => {
    if (!searchQuery || searchQuery.length < 2) {
      setError('Please enter at least 2 characters to search')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await medicationsApi.search(searchQuery, 50)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search medications')
    } finally {
      setLoading(false)
    }
  }

  const handleGetByCategory = async (category: string) => {
    setLoading(true)
    setError(null)
    setSelectedCategory(category)
    try {
      const response = await medicationsApi.getByCategory(category)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get medications by category')
    } finally {
      setLoading(false)
    }
  }

  const handleGetMedication = async (name: string) => {
    setLoading(true)
    setError(null)
    setSelectedMedication(name)
    try {
      const response = await medicationsApi.getMedication(name)
      setMedicationDetails(response)
      setActiveTab('details')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get medication details')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadMedications = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await medicationsApi.loadHFMedications()
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load medications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timeoutId = setTimeout(() => {
        handleSearch()
      }, 500)
      return () => clearTimeout(timeoutId)
    }
  }, [searchQuery])

  return (
    <div className="medication-database-page">
      <div className="page-header">
        <h1>Medication Database</h1>
        <p>Browse and search the comprehensive medication database with 1000s of medications</p>
      </div>

      <div className="medication-database-layout">
        <div className="tabs-container">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={18} />
              Search
            </button>
            <button
              className={`tab ${activeTab === 'category' ? 'active' : ''}`}
              onClick={() => setActiveTab('category')}
            >
              <Filter size={18} />
              By Category
            </button>
            <button
              className={`tab ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              <Pill size={18} />
              Details
            </button>
            <button
              className={`tab ${activeTab === 'load' ? 'active' : ''}`}
              onClick={() => setActiveTab('load')}
            >
              <Database size={18} />
              Load Medications
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'search' && (
              <Card title="Search Medications" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Search for medications by name. Results update as you type.</span>
                </div>
                <div className="search-form">
                  <Input
                    label="Search Medications"
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="e.g., Lisinopril, Metoprolol, Furosemide"
                  />
                  <Button onClick={handleSearch} disabled={loading || !searchQuery || searchQuery.length < 2}>
                    {loading ? 'Searching...' : 'Search'}
                  </Button>
                </div>
                {results && results.medications && (
                  <div className="search-results">
                    <h3>Results ({results.count})</h3>
                    <div className="medications-list">
                      {results.medications.map((med: any, idx: number) => (
                        <div
                          key={idx}
                          className="medication-item"
                          onClick={() => handleGetMedication(med.name)}
                        >
                          <Pill size={16} />
                          <div className="med-info">
                            <span className="med-name">{med.name}</span>
                            {med.category && (
                              <span className="med-category">{med.category.replace(/_/g, ' ')}</span>
                            )}
                          </div>
                          {med.strength && (
                            <span className="med-strength">{med.strength}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'category' && (
              <Card title="Browse by Category" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Browse medications by therapeutic category.</span>
                </div>
                <div className="categories-grid">
                  {MEDICATION_CATEGORIES.map((category) => (
                    <button
                      key={category}
                      className={`category-button ${selectedCategory === category ? 'active' : ''}`}
                      onClick={() => handleGetByCategory(category)}
                    >
                      {category.replace(/_/g, ' ').toUpperCase()}
                    </button>
                  ))}
                </div>
                {loading && (
                  <div className="loading-state">
                    <Loader2 size={20} className="spinner" />
                    <span>Loading medications...</span>
                  </div>
                )}
                {results && results.medications && (
                  <div className="category-results">
                    <h3>{selectedCategory.replace(/_/g, ' ').toUpperCase()} ({results.count})</h3>
                    <div className="medications-list">
                      {results.medications.map((med: any, idx: number) => (
                        <div
                          key={idx}
                          className="medication-item"
                          onClick={() => handleGetMedication(med.name)}
                        >
                          <Pill size={16} />
                          <div className="med-info">
                            <span className="med-name">{med.name}</span>
                            {med.strength && (
                              <span className="med-strength">{med.strength}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'details' && (
              <Card title="Medication Details" className="tab-card">
                {medicationDetails ? (
                  <div className="medication-details">
                    <div className="details-header">
                      <h2>{medicationDetails.name}</h2>
                      {medicationDetails.category && (
                        <span className="category-badge">
                          {medicationDetails.category.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div className="details-grid">
                      {medicationDetails.strength && (
                        <div className="detail-item">
                          <strong>Strength:</strong> {medicationDetails.strength}
                        </div>
                      )}
                      {medicationDetails.dosage_form && (
                        <div className="detail-item">
                          <strong>Dosage Form:</strong> {medicationDetails.dosage_form}
                        </div>
                      )}
                      {medicationDetails.route && (
                        <div className="detail-item">
                          <strong>Route:</strong> {medicationDetails.route}
                        </div>
                      )}
                      {medicationDetails.frequency && (
                        <div className="detail-item">
                          <strong>Frequency:</strong> {medicationDetails.frequency}
                        </div>
                      )}
                      {medicationDetails.mechanism && (
                        <div className="detail-item full-width">
                          <strong>Mechanism:</strong> {medicationDetails.mechanism}
                        </div>
                      )}
                      {medicationDetails.indications && (
                        <div className="detail-item full-width">
                          <strong>Indications:</strong> {medicationDetails.indications}
                        </div>
                      )}
                      {medicationDetails.contraindications && (
                        <div className="detail-item full-width warning">
                          <strong>Contraindications:</strong> {medicationDetails.contraindications}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="no-selection">
                    <Info size={24} />
                    <p>Select a medication from search or category to view details</p>
                  </div>
                )}
              </Card>
            )}

            {activeTab === 'load' && (
              <Card title="Load Heart Failure Medications" className="tab-card">
                <div className="form-info">
                  <Info size={16} />
                  <span>Load heart failure medications from RxNorm API into the database. This may take a few minutes.</span>
                </div>
                <Button onClick={handleLoadMedications} disabled={loading}>
                  {loading ? 'Loading...' : 'Load Medications'}
                </Button>
                {results && (
                  <div className="load-results">
                    <div className="success-message">
                      <CheckCircle size={20} />
                      <div>
                        <strong>Success!</strong>
                        <p>Loaded {results.medications_loaded} medications into the database.</p>
                      </div>
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
