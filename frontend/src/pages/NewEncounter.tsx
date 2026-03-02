import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Beaker, FileText, ArrowLeft, CheckCircle2, ShieldAlert, X, Pill, Plus } from 'lucide-react';
import { createDigitalTwinEncounter, getAllergens, searchMedicines } from '../services/api';
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
        allergies: '',
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
        bnp: '',

        medications: [] as any[]
    });

    const [allergenOptions, setAllergenOptions] = useState<string[]>([]);
    const [allergiesList, setAllergiesList] = useState<string[]>([]);
    const [allergenInput, setAllergenInput] = useState('');

    const [medicineOptions, setMedicineOptions] = useState<string[]>([]);
    const [medSearchTimer, setMedSearchTimer] = useState<any>(null);

    useEffect(() => {
        const fetchAllergens = async () => {
            try {
                const data = await getAllergens();
                setAllergenOptions(data);
            } catch (e) {
                console.error("Failed to load allergens", e);
            }
        };
        fetchAllergens();
    }, []);

    const handleAddAllergen = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const val = allergenInput.trim();
            if (val && !allergiesList.includes(val)) {
                const newList = [...allergiesList, val];
                setAllergiesList(newList);
                setFormData({ ...formData, allergies: newList.join(', ') });
            }
            setAllergenInput('');
        }
    };

    const removeAllergen = (item: string) => {
        const newList = allergiesList.filter(a => a !== item);
        setAllergiesList(newList);
        setFormData({ ...formData, allergies: newList.join(', ') });
    };

    const addMedicationRow = () => {
        setFormData({
            ...formData,
            medications: [
                ...formData.medications,
                {
                    name: '',
                    dosage: '',
                    timing: {
                        beforeBreakfast: false,
                        afterBreakfast: false,
                        beforeLunch: false,
                        afterLunch: false,
                        beforeDinner: false,
                        afterDinner: false
                    }
                }
            ]
        });
    };

    const handleMedNameChange = (index: number, val: string) => {
        const newMeds = [...formData.medications];
        newMeds[index].name = val;
        setFormData({ ...formData, medications: newMeds });

        if (medSearchTimer) clearTimeout(medSearchTimer);
        if (val.length > 2) {
            setMedSearchTimer(setTimeout(async () => {
                const results = await searchMedicines(val);
                setMedicineOptions(results);
            }, 300));
        } else {
            setMedicineOptions([]);
        }
    };

    const handleMedDosageChange = (index: number, val: string) => {
        const newMeds = [...formData.medications];
        newMeds[index].dosage = val;
        setFormData({ ...formData, medications: newMeds });
    };

    const handleMedTimingChange = (index: number, timingKey: string, checked: boolean) => {
        const newMeds = [...formData.medications];
        newMeds[index].timing[timingKey] = checked;
        setFormData({ ...formData, medications: newMeds });
    };

    const removeMedicationRow = (index: number) => {
        const newMeds = [...formData.medications];
        newMeds.splice(index, 1);
        setFormData({ ...formData, medications: newMeds });
    };

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

                            <div className="form-group" style={{ marginTop: '16px', padding: '16px', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '4px', backgroundColor: 'rgba(239, 68, 68, 0.05)' }}>
                                <label style={{ color: 'var(--color-accent-red)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <ShieldAlert size={14} /> ALLERGIES (PRESS ENTER TO ADD)
                                </label>
                                <input
                                    type="text"
                                    list="allergen-list"
                                    value={allergenInput}
                                    onChange={(e) => setAllergenInput(e.target.value)}
                                    onKeyDown={handleAddAllergen}
                                    placeholder="Type allergy and press Enter..."
                                    style={{ borderColor: 'rgba(239, 68, 68, 0.5)' }}
                                />
                                <datalist id="allergen-list">
                                    {allergenOptions.map((opt, idx) => <option key={idx} value={opt} />)}
                                </datalist>
                                {allergiesList.length > 0 && (
                                    <div className="allergy-tags">
                                        {allergiesList.map((a, i) => (
                                            <span key={i} className="allergy-tag">
                                                {a} <button type="button" onClick={() => removeAllergen(a)}><X size={12} /></button>
                                            </span>
                                        ))}
                                    </div>
                                )}
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

                {/* MEDICATIONS */}
                <div className="ne-panel border-green" style={{ marginBottom: '24px' }}>
                    <div className="ne-panel-head text-green" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div><Pill size={16} /> CURRENT MEDICATIONS (BASELINE)</div>
                        <button type="button" className="ne-add-btn" onClick={addMedicationRow}>
                            <Plus size={14} /> ADD MEDICATION
                        </button>
                    </div>
                    <div className="ne-panel-body" style={{ padding: '0' }}>
                        {formData.medications.length === 0 ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '13px' }}>
                                No active medications added to profile.
                            </div>
                        ) : (
                            <table className="ne-med-table">
                                <thead>
                                    <tr>
                                        <th>MEDICATION NAME</th>
                                        <th style={{ width: '150px' }}>DOSAGE</th>
                                        <th style={{ width: '400px' }}>TIMING (CHECK ALL THAT APPLY)</th>
                                        <th style={{ width: '60px' }}></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {formData.medications.map((med, idx) => (
                                        <tr key={idx}>
                                            <td>
                                                <input
                                                    type="text"
                                                    value={med.name}
                                                    onChange={(e) => handleMedNameChange(idx, e.target.value)}
                                                    placeholder="Search medicine..."
                                                    list="medicine-list"
                                                    required
                                                />
                                            </td>
                                            <td>
                                                <input
                                                    type="text"
                                                    value={med.dosage}
                                                    onChange={(e) => handleMedDosageChange(idx, e.target.value)}
                                                    placeholder="e.g. 50mg"
                                                    required
                                                />
                                            </td>
                                            <td>
                                                <div className="timing-grid">
                                                    <label><input type="checkbox" checked={med.timing.beforeBreakfast} onChange={(e) => handleMedTimingChange(idx, 'beforeBreakfast', e.target.checked)} /> Before BF</label>
                                                    <label><input type="checkbox" checked={med.timing.afterBreakfast} onChange={(e) => handleMedTimingChange(idx, 'afterBreakfast', e.target.checked)} /> After BF</label>
                                                    <label><input type="checkbox" checked={med.timing.beforeLunch} onChange={(e) => handleMedTimingChange(idx, 'beforeLunch', e.target.checked)} /> Before Lunch</label>
                                                    <label><input type="checkbox" checked={med.timing.afterLunch} onChange={(e) => handleMedTimingChange(idx, 'afterLunch', e.target.checked)} /> After Lunch</label>
                                                    <label><input type="checkbox" checked={med.timing.beforeDinner} onChange={(e) => handleMedTimingChange(idx, 'beforeDinner', e.target.checked)} /> Before Dinner</label>
                                                    <label><input type="checkbox" checked={med.timing.afterDinner} onChange={(e) => handleMedTimingChange(idx, 'afterDinner', e.target.checked)} /> After Dinner</label>
                                                </div>
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <button type="button" className="ne-remove-btn" onClick={() => removeMedicationRow(idx)}>
                                                    <X size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                        <datalist id="medicine-list">
                            {medicineOptions.map((opt, i) => <option key={i} value={opt} />)}
                        </datalist>
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
