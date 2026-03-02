import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import Card from '../components/Card'
import Button from '../components/Button'
import { documentsApi } from '../services/api'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Pill, Info, Eye, FileCheck, Sparkles } from 'lucide-react'
import './DocumentUpload.css'

type DocumentType = 'prescription' | 'lab' | null

export default function DocumentUpload() {
  const [documentType, setDocumentType] = useState<DocumentType>(null)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [getRecommendations, setGetRecommendations] = useState(true)

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setResults(null)
      setError(null)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  })

  const handleUpload = async () => {
    if (!file || !documentType) {
      setError('Please select a document type and file')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      let response
      if (documentType === 'prescription') {
        response = await documentsApi.uploadPrescription(file, getRecommendations)
      } else {
        response = await documentsApi.uploadLabReport(file, getRecommendations)
      }
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process document')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setResults(null)
    setError(null)
  }

  return (
    <div className="document-upload-page">
      <div className="page-header">
        <h1>Document Upload & Parsing</h1>
        <p>Upload prescriptions or lab reports for automatic OCR text extraction, parsing, and medication recommendations</p>
      </div>

      <div className="upload-layout">
        <Card title="Upload Document" className="upload-card">
          <div className="upload-info">
            <FileCheck size={16} />
            <span>Our OCR system uses advanced text recognition to extract information from images and PDFs</span>
          </div>
          <div className="document-type-selector">
            <h3>Select Document Type</h3>
            <p className="type-description">Choose the type of document you're uploading to enable specialized parsing</p>
            <div className="type-buttons">
              <button
                className={`type-button ${documentType === 'prescription' ? 'active' : ''}`}
                onClick={() => {
                  setDocumentType('prescription')
                  reset()
                }}
              >
                <FileText size={24} />
                <div>
                  <span className="type-title">Prescription</span>
                  <span className="type-subtitle">Extracts medications, dosages, frequencies</span>
                </div>
              </button>
              <button
                className={`type-button ${documentType === 'lab' ? 'active' : ''}`}
                onClick={() => {
                  setDocumentType('lab')
                  reset()
                }}
              >
                <FileText size={24} />
                <div>
                  <span className="type-title">Lab Report</span>
                  <span className="type-subtitle">Extracts lab values (EF, creatinine, BNP, etc.)</span>
                </div>
              </button>
            </div>
          </div>

          {documentType && (
            <>
              <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
              >
                <input {...getInputProps()} />
                {file ? (
                  <div className="file-info">
                    <CheckCircle size={48} color="var(--color-positive)" />
                    <p className="file-name">{file.name}</p>
                    <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                ) : (
                  <div className="dropzone-content">
                    <Upload size={48} color="var(--color-highlight)" />
                    <p>Drag & drop a file here, or click to select</p>
                    <p className="file-hint">Supports: JPG, PNG, PDF</p>
                  </div>
                )}
              </div>

              <div className="upload-options">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={getRecommendations}
                    onChange={(e) => setGetRecommendations(e.target.checked)}
                  />
                  <span>Get medication recommendations</span>
                </label>
              </div>

              {error && (
                <div className="error-message">
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              <div className="upload-actions">
                <Button
                  variant="primary"
                  onClick={handleUpload}
                  disabled={!file || loading}
                  isLoading={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="spinner" size={20} />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload size={20} />
                      Process Document
                    </>
                  )}
                </Button>
                {file && (
                  <Button variant="secondary" onClick={reset}>
                    Clear
                  </Button>
                )}
              </div>
            </>
          )}
        </Card>

        {results && (
          <div className="results-section">
            <Card title="Extracted Information" className="results-card">
              <div className="results-header">
                <Sparkles size={20} color="var(--color-highlight)" />
                <span>Information extracted and parsed successfully</span>
              </div>
              {results.parsed_prescription && (
                <div className="parsed-section">
                  <h3>
                    <Pill size={18} />
                    Prescription Details
                  </h3>
                  <p className="section-summary">Found {results.medications?.length || 0} medication(s) in the prescription</p>
                  <div className="medications-found">
                    <strong>Medications Found:</strong>
                    <div className="med-list">
                      {results.medications?.map((med: string, idx: number) => (
                        <span key={idx} className="med-tag">
                          {med.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                  {results.medication_details && (
                    <div className="med-details">
                      {results.medication_details.map((med: any, idx: number) => (
                        <div key={idx} className="med-detail-item">
                          <strong>{med.name}</strong>
                          {med.dosage && <span>Dosage: {med.dosage}</span>}
                          {med.frequency && <span>Frequency: {med.frequency}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {results.parsed_lab_report && (
                <div className="parsed-section">
                  <h3>
                    <FileText size={18} />
                    Lab Report Details
                  </h3>
                  <p className="section-summary">Extracted {Object.keys(results.lab_values || {}).length} lab value(s)</p>
                  <div className="lab-values">
                    {Object.entries(results.lab_values || {}).map(([key, value]: [string, any]) => (
                      <div key={key} className="lab-value-item">
                        <span className="lab-name">{key.replace(/_/g, ' ')}</span>
                        <span className="lab-value">
                          {value.value} {value.unit || ''}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {results.extracted_text && (
                <div className="parsed-section">
                  <h3>
                    <Eye size={18} />
                    Extracted Text (OCR Output)
                  </h3>
                  <p className="section-summary">Raw text extracted from the document using OCR technology</p>
                  <div className="extracted-text">
                    <pre>{results.extracted_text.substring(0, 1000)}{results.extracted_text.length > 1000 ? '...' : ''}</pre>
                    {results.extracted_text.length > 1000 && (
                      <div className="text-truncated">
                        <Info size={14} />
                        <span>Text truncated. Full text available in API response.</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </Card>

            {results.recommendations && !results.recommendations.error && (
              <Card title="Recommendations" className="recommendations-card">
                <div className="recommendations-summary">
                  <div className="rec-summary-item">
                    <Pill size={20} color="var(--color-highlight)" />
                    <span>
                      Top: {results.recommendations.summary?.top_recommendation?.medication?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  {results.recommendations.optimal_combination && (
                    <div className="rec-summary-item">
                      <strong>Optimal Combination:</strong>
                      <div className="combo-meds">
                        {results.recommendations.optimal_combination.medications?.map((med: string, idx: number) => (
                          <span key={idx} className="combo-med-tag">
                            {med.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

