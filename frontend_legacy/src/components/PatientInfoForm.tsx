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
          <Input
            label="NYHA Class"
            type="text"
            value={patientInfo.nyha_class || ''}
            onChange={(e) => onChange('nyha_class', e.target.value)}
            placeholder="I, II, III, or IV"
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
            label="Diastolic BP"
            type="number"
            value={patientInfo.diastolic_bp || ''}
            onChange={(e) => onChange('diastolic_bp', parseFloat(e.target.value))}
            placeholder="90"
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
        <div className="form-row" style={{ marginTop: '10px' }}>
          <Input
            label="NT-proBNP (pg/mL)"
            type="number"
            value={patientInfo.nt_pro_bnp || ''}
            onChange={(e) => onChange('nt_pro_bnp', parseFloat(e.target.value))}
            placeholder=">450"
          />
          <Input
            label="Troponin (ng/mL)"
            type="number"
            step="0.01"
            value={patientInfo.troponin || ''}
            onChange={(e) => onChange('troponin', parseFloat(e.target.value))}
            placeholder="0.04"
          />
        </div>
        <div className="form-row" style={{ marginTop: '10px' }}>
          <Input
            label="Max Heart Rate (Stress)"
            type="number"
            value={patientInfo.max_hr || ''}
            onChange={(e) => onChange('max_hr', parseFloat(e.target.value))}
            placeholder="150"
          />
          <Input
            label="Oldpeak (ST Depression)"
            type="number"
            step="0.1"
            value={patientInfo.oldpeak || ''}
            onChange={(e) => onChange('oldpeak', parseFloat(e.target.value))}
            placeholder="1.5"
          />
          <div className="input-group">
            <label>ST Slope</label>
            <select
              value={patientInfo.st_slope || 'Flat'}
              onChange={(e) => onChange('st_slope', e.target.value)}
              className="input-field"
              style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '2px solid var(--color-border)', width: '100%' }}
            >
              <option value="Up">Up</option>
              <option value="Flat">Flat</option>
              <option value="Down">Down</option>
            </select>
          </div>
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
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.atrial_fibrillation || false}
                onChange={(e) => onChange('atrial_fibrillation', e.target.checked)}
              />
              <span>Atrial Fibrillation</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.copd || false}
                onChange={(e) => onChange('copd', e.target.checked)}
              />
              <span>COPD</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.ckd || false}
                onChange={(e) => onChange('ckd', e.target.checked)}
              />
              <span>Chronic Kidney Disease</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.anemia || false}
                onChange={(e) => onChange('anemia', e.target.checked)}
              />
              <span>Anemia</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={patientInfo.exercise_angina || false}
                onChange={(e) => onChange('exercise_angina', e.target.checked)}
              />
              <span>Exercise Angina</span>
            </label>
          </div>
        </div>
      )}
    </div>
  )
}
