import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Patients from './pages/Patients'
import Recommendations from './pages/Recommendations'
import DocumentUpload from './pages/DocumentUpload'
import TreatmentComparison from './pages/TreatmentComparison'
import DigitalTwin from './pages/DigitalTwin'
import TemporalData from './pages/TemporalData'
import Predictions from './pages/Predictions'
import MedicationDatabase from './pages/MedicationDatabase'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/documents" element={<DocumentUpload />} />
          <Route path="/comparison" element={<TreatmentComparison />} />
          <Route path="/digital-twin" element={<DigitalTwin />} />
          <Route path="/temporal-data" element={<TemporalData />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/medications" element={<MedicationDatabase />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App



