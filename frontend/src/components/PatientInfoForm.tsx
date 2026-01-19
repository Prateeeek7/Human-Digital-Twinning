import { PatientInfo } from '../services/api'
import Input from './Input'
import { Activity, Heart, Droplet, Info } from 'lucide-react'
import './PatientInfoForm.css'

interface PatientInfoFormProps {
  patientInfo: PatientInfo
  onChange: (field: string, value: any) => void
  showComorbidities?: boolean
  compact?: boolean
}

export default function PatientInfoForm({ 
  patientInfo, 
  onChange, 
  showComorbidities = true,
  compact = false 
}: PatientInfoFormProps) {
  return (
    <div className={`patient-info-form ${compact ? 'compact' : ''}`}>
      {!compact && (
        <div className="form-info">
          <Info size={16} />
          <span>Fill in patient information. More data leads to better recommendations.</span>
        </div>
      )}
      
      <div className="form-section">
        <h3>Demographics</h3>
        <div className="form-row">
          <Input
            label="Age"
            type="number"
            value={patientInfo.age || ''}
            onChange={(e) => onChange('age', parseInt(e.target.value))}
            placeholder="65"
          />
          <Input
            label="Sex"
            type="text"
            value={patientInfo.sex || ''}
            onChange={(e) => onChange('sex', e.target.value)}
            placeholder="M or F"
          />
        </div>
      </div>

      <div className="form-section">
        <h3>
          <Activity size={18} />
          Vital Signs
        </h3>
        <div className="form-row">
          <Input
            label="Ejection Fraction (%)"
            type="number"
            step="0.01"
            value={patientInfo.ejection_fraction ? (patientInfo.ejection_fraction * 100).toFixed(0) : ''}
            onChange={(e) => onChange('ejection_fraction', parseFloat(e.target.value) / 100)}
            placeholder="35"
          />
          <Input
            label="Systolic BP"
            type="number"
            value={patientInfo.systolic_bp || ''}
            onChange={(e) => onChange('systolic_bp', parseFloat(e.target.value))}
            placeholder="140"
          />
          <Input
            label="Heart Rate"
            type="number"
            value={patientInfo.heart_rate || ''}
            onChange={(e) => onChange('heart_rate', parseFloat(e.target.value))}
            placeholder="75"
          />
        </div>
      </div>

      <div className="form-section">
        <h3>
          <Droplet size={18} />
          Lab Values
        </h3>
        <div className="form-row">
          <Input
            label="Creatinine"
            type="number"
            step="0.01"
            value={patientInfo.creatinine || ''}
            onChange={(e) => onChange('creatinine', parseFloat(e.target.value))}
            placeholder="1.2"
          />
          <Input
            label="Sodium"
            type="number"
            value={patientInfo.sodium || ''}
            onChange={(e) => onChange('sodium', parseFloat(e.target.value))}
            placeholder="140"
          />
        </div>
      </div>

      {showComorbidities && (
        <div className="form-section">
          <h3>
            <Heart size={18} />
            Comorbidities
          </h3>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.diabetes || false}
                onChange={(e) => onChange('diabetes', e.target.checked)}
              />
              <span>Diabetes</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.high_blood_pressure || false}
                onChange={(e) => onChange('high_blood_pressure', e.target.checked)}
              />
              <span>High Blood Pressure</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.high_cholesterol || false}
                onChange={(e) => onChange('high_cholesterol', e.target.checked)}
              />
              <span>High Cholesterol</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.smoking || false}
                onChange={(e) => onChange('smoking', e.target.checked)}
              />
              <span>Smoking</span>
            </label>
          </div>
        </div>
      )}
    </div>
  )
}
