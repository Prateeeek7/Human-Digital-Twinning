import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Beaker, FileText, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { createDigitalTwinEncounter } from '../services/api';
import './NewEncounter.css';

const NewEncounter: React.FC = () => {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        // Demographics
        firstName: '',
        lastName: '',
        dob: '',
        gender: 'M',
        phone: '',
        address: '',
        weightKg: '',
        heightCm: '',

        // Vitals
        heartRate: '',
        bpSys: '',
        bpDia: '',
        spo2: '',
        respiratoryRate: '',

        // Critical HF Labs
        ejectionFraction: '',
        creatinine: '',
        sodium: '',
        potassium: '',
        bnp: ''
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const newPatientId = await createDigitalTwinEncounter(formData);
            if (newPatientId) {
                navigate(`/board/${newPatientId}`);
            } else {
                alert("Failed to initialize twin. Check console.");
                setIsSubmitting(false);
            }
        } catch (error) {
            console.error("Submission Error", error);
            alert("API Error capturing encounter. Check console.");
            setIsSubmitting(false);
        }
    };

    return (
        <div className="ne-container">
            <div className="ne-header">
                <button className="ne-back-btn" onClick={() => navigate('/patients')}><ArrowLeft size={16} /> ABORT INTAKE</button>
                <div className="ne-title">
                    <h2>NEW HF-TWIN ENCOUNTER</h2>
                    <p>Initialize baseline physiology parameters for digital modeling.</p>
                </div>
                <div className="ne-status">
                    <span className="ne-badge">LIVE INGESTION MODE</span>
                </div>
            </div>

            <form className="ne-form" onSubmit={handleSubmit}>
                <div className="ne-layout">
                    {/* DEMOGRAPHICS */}
                    <div className="ne-panel">
                        <div className="ne-panel-head">
                            <FileText size={16} /> IDENTIFICATION & ANTHROPOMETRICS
                        </div>
                        <div className="ne-panel-body">
                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label>FIRST NAME</label>
                                    <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} required />
                                </div>
                                <div className="form-group flex-1">
                                    <label>LAST NAME</label>
                                    <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} required />
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label>DATE OF BIRTH</label>
                                    <input type="date" name="dob" value={formData.dob} onChange={handleChange} required />
                                </div>
                                <div className="form-group">
                                    <label>SEX</label>
                                    <select name="gender" value={formData.gender} onChange={handleChange} required>
                                        <option value="M">Male</option>
                                        <option value="F">Female</option>
                                        <option value="O">Other</option>
                                    </select>
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label>WEIGHT (KG)</label>
                                    <input type="number" step="0.1" name="weightKg" value={formData.weightKg} onChange={handleChange} required />
                                </div>
                                <div className="form-group flex-1">
                                    <label>HEIGHT (CM)</label>
                                    <input type="number" name="heightCm" value={formData.heightCm} onChange={handleChange} required />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>PHONE (OPTIONAL)</label>
                                <input type="text" name="phone" value={formData.phone} onChange={handleChange} />
                            </div>
                            <div className="form-group">
                                <label>ADDRESS (OPTIONAL)</label>
                                <input type="text" name="address" value={formData.address} onChange={handleChange} />
                            </div>
                        </div>
                    </div>

                    <div className="ne-right-col">
                        {/* VITALS */}
                        <div className="ne-panel border-red">
                            <div className="ne-panel-head text-red">
                                <Activity size={16} /> BASELINE HEMODYNAMICS (T=0)
                            </div>
                            <div className="ne-panel-body">
                                <div className="form-row">
                                    <div className="form-group flex-1">
                                        <label>HEART RATE (BPM)</label>
                                        <input type="number" name="heartRate" value={formData.heartRate} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>SpO2 (%)</label>
                                        <input type="number" name="spo2" value={formData.spo2} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>RESP RATE</label>
                                        <input type="number" name="respiratoryRate" value={formData.respiratoryRate} onChange={handleChange} required />
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group flex-1">
                                        <label>SYSTOLIC BP</label>
                                        <input type="number" name="bpSys" value={formData.bpSys} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>DIASTOLIC BP</label>
                                        <input type="number" name="bpDia" value={formData.bpDia} onChange={handleChange} required />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* LABS */}
                        <div className="ne-panel border-blue">
                            <div className="ne-panel-head text-blue">
                                <Beaker size={16} /> CRITICAL HF BIOMARKERS (T=0)
                            </div>
                            <div className="ne-panel-body">
                                <div className="form-row">
                                    <div className="form-group flex-1">
                                        <label>EJECTION FRACTION (%)</label>
                                        <input type="number" step="0.1" name="ejectionFraction" value={formData.ejectionFraction} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>CREATININE (mg/dL)</label>
                                        <input type="number" step="0.01" name="creatinine" value={formData.creatinine} onChange={handleChange} required />
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group flex-1">
                                        <label>SODIUM (mEq/L)</label>
                                        <input type="number" name="sodium" value={formData.sodium} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>POTASSIUM (mEq/L)</label>
                                        <input type="number" step="0.1" name="potassium" value={formData.potassium} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group flex-1">
                                        <label>BNP (pg/mL)</label>
                                        <input type="number" name="bnp" value={formData.bnp} onChange={handleChange} required />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="ne-footer">
                    <button type="submit" className="ne-submit-btn" disabled={isSubmitting}>
                        {isSubmitting ? "GENERATING TWIN..." : <><CheckCircle2 size={18} /> INITIALIZE CLINICAL DIGITAL TWIN</>}
                    </button>
                    <p className="ne-footer-note">Submission writes to `hospital_core.db` and triggers `clinical_patients.db` ingestion loop.</p>
                </div>
            </form>
        </div>
    );
};

export default NewEncounter;
