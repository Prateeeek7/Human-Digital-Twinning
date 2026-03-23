import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './ClinicalBoard.css';
import Sparkline from '../components/Sparkline';
import BulletGraph from '../components/BulletGraph';
import { getMedicationRecommendations, getPatientHistory, getPatientSummary } from '../services/api';
import type { PredictionResponse } from '../services/api';

const ClinicalBoard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const patientId = id || 'PT-001';

    const [horizonDays, setHorizonDays] = useState(90);
    const [results, setResults] = useState<PredictionResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Data State
    const [isDataLoaded, setIsDataLoaded] = useState(false);
    const [patientSummary, setPatientSummary] = useState<any>(null);
    const [trends, setTrends] = useState({
        hr: [] as number[],
        bp: [] as number[],
        ef: [] as number[],
        cr: [] as number[],
        na: [] as number[],
        chol: [] as number[]
    });
    const [currentVitals, setCurrentVitals] = useState({
        hr: '--',
        bp: '--',
        ef: '--',
        cr: '--',
        na: '--',
        chol: '--',
        hba1c: '--',
        hgb: '--'
    });

    useEffect(() => {
        const loadPatientData = async () => {
            try {
                const history = await getPatientHistory(patientId);
                const summary = await getPatientSummary(patientId);

                setPatientSummary(summary);

                let hrArr: number[] = [], bpArr: number[] = [], efArr: number[] = [], crArr: number[] = [], naArr: number[] = [], cholArr: number[] = [];
                let currHr = '--', currBp = '--', currEf = '--', currCr = '--', currNa = '--', currChol = '--';

                if (history.vitals) {
                    hrArr = history.vitals.filter((v: any) => v.vital_name === 'Heart Rate').map((v: any) => v.value);
                    if (hrArr.length > 0) currHr = hrArr[hrArr.length - 1].toString();

                    bpArr = history.vitals.filter((v: any) => v.vital_name === 'Systolic BP').map((v: any) => v.value);
                    if (bpArr.length > 0) currBp = bpArr[bpArr.length - 1].toString();
                }

                if (history.labs) {
                    efArr = history.labs.filter((v: any) => v.lab_name === 'Ejection Fraction').map((v: any) => v.value);
                    if (efArr.length > 0) currEf = efArr[efArr.length - 1].toString();

                    crArr = history.labs.filter((v: any) => v.lab_name === 'Creatinine').map((v: any) => v.value);
                    if (crArr.length > 0) currCr = crArr[crArr.length - 1].toString();

                    naArr = history.labs.filter((v: any) => v.lab_name === 'Sodium').map((v: any) => v.value);
                    if (naArr.length > 0) currNa = naArr[naArr.length - 1].toString();

                    cholArr = history.labs.filter((v: any) => v.lab_name === 'Cholesterol').map((v: any) => v.value);
                    if (cholArr.length > 0) currChol = cholArr[cholArr.length - 1].toString();

                    const hba1cArr = history.labs.filter((v: any) => v.lab_name === 'HbA1c').map((v: any) => v.value);
                    const currHba1c = hba1cArr.length > 0 ? hba1cArr[hba1cArr.length - 1].toString() : '--';

                    const hgbArr = history.labs.filter((v: any) => v.lab_name === 'Hemoglobin').map((v: any) => v.value);
                    const currHgb = hgbArr.length > 0 ? hgbArr[hgbArr.length - 1].toString() : '--';

                    setCurrentVitals({ hr: currHr, bp: currBp, ef: currEf, cr: currCr, na: currNa, chol: currChol, hba1c: currHba1c, hgb: currHgb });
                } else {
                    setCurrentVitals({ hr: currHr, bp: currBp, ef: currEf, cr: currCr, na: currNa, chol: currChol, hba1c: '--', hgb: '--' });
                }

                setTrends({ hr: hrArr, bp: bpArr, ef: efArr, cr: crArr, na: naArr, chol: cholArr });
                setIsDataLoaded(true);

            } catch (err) {
                console.error("Failed to load patient data:", err);
            }
        };

        loadPatientData();
    }, [patientId]);

    const handleRunAI = async () => {
        setIsLoading(true);
        try {
            const res = await getMedicationRecommendations({
                patient_info: {
                    age: patientSummary?.demographics?.age || 65,
                    sex: patientSummary?.demographics?.sex || "M",
                    ejection_fraction: parseFloat(currentVitals.ef) / 100 || 0.35,
                    systolic_bp: parseFloat(currentVitals.bp) || 140,
                    diabetes: patientSummary?.comorbidities?.diabetes || false,
                    high_blood_pressure: patientSummary?.comorbidities?.high_blood_pressure || false,
                    anaemia: patientSummary?.comorbidities?.anaemia || false,
                    smoking: patientSummary?.comorbidities?.smoking || false,
                    creatinine: parseFloat(currentVitals.cr) || 1.2,
                    sodium: parseFloat(currentVitals.na) || 140,
                    cholesterol: parseFloat(currentVitals.chol) || 200,
                    hba1c: currentVitals.hba1c !== '--' ? parseFloat(currentVitals.hba1c) : undefined,
                    hemoglobin: currentVitals.hgb !== '--' ? parseFloat(currentVitals.hgb) : undefined
                },
                time_horizon_days: horizonDays
            });
            setResults(res);
        } catch (e) {
            console.error("Failed to run AI", e);
        } finally {
            setIsLoading(false);
        }
    };

    const currentRisk = { mortality: 25, readmission: 30 };
    const targetMortality = results ? currentRisk.mortality + ((results.recommendations[0]?.predicted_effect?.mortality_risk_change || 0) * 100) : currentRisk.mortality;
    const targetReadmission = results ? currentRisk.readmission + ((results.recommendations[0]?.predicted_effect?.readmission_risk_change || 0) * 100) : currentRisk.readmission;

    if (!isDataLoaded) {
        return (
            <div className="clinical-board" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="pane-subheader" style={{ fontSize: '14px', letterSpacing: '1px' }}>SYNCING PATIENT DIGITAL TWIN: {patientId}...</span>
            </div>
        );
    }

    return (
        <div className="clinical-board">

            {/* LEFT PANE: VITALS & LABS */}
            <div className="cb-pane-left">
                <div className="pane-header">
                    <span>VITALS & LABS</span>
                    <span className="pane-subheader">LAST 48H SUMMARY</span>
                </div>

                <table className="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Trend</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Heart Rate</td>
                            <td className="value-highlight">{currentVitals.hr} <span className="pane-subheader">bpm</span></td>
                            <td><Sparkline data={trends.hr} min={60} max={110} /></td>
                        </tr>
                        <tr>
                            <td>Systolic BP</td>
                            <td className="value-highlight">{currentVitals.bp} <span className="pane-subheader">mmHg</span></td>
                            <td><Sparkline data={trends.bp} min={100} max={160} /></td>
                        </tr>
                        <tr className="data-row-critical">
                            <td>Ejection Frac</td>
                            <td className="value-critical">{currentVitals.ef} <span className="pane-subheader">%</span></td>
                            <td><Sparkline data={trends.ef} min={20} max={60} color="var(--color-accent-red)" /></td>
                        </tr>
                        <tr>
                            <td>Creatinine</td>
                            <td className="value-highlight">{currentVitals.cr} <span className="pane-subheader">mg/dL</span></td>
                            <td><Sparkline data={trends.cr} min={0.5} max={2.0} /></td>
                        </tr>
                        <tr>
                            <td>Sodium</td>
                            <td className="value-highlight">{currentVitals.na} <span className="pane-subheader">mEq/L</span></td>
                            <td><Sparkline data={trends.na} min={130} max={150} /></td>
                        </tr>
                        <tr>
                            <td>Cholesterol</td>
                            <td className="value-highlight">{currentVitals.chol} <span className="pane-subheader">mg/dL</span></td>
                            <td><Sparkline data={trends.chol} min={150} max={250} /></td>
                        </tr>
                    </tbody>
                </table>

                <div className="pane-header" style={{ borderTop: '1px solid var(--color-border-strong)', marginTop: 'auto' }}>
                    <span>COMORBIDITIES</span>
                </div>
                <table className="data-table">
                    <tbody>
                        <tr><td>Diabetes</td><td className={patientSummary?.comorbidities?.diabetes ? "value-critical" : ""}>{patientSummary?.comorbidities?.diabetes ? "TRUE" : "FALSE"}</td></tr>
                        <tr><td>High BP</td><td className={patientSummary?.comorbidities?.high_blood_pressure ? "value-critical" : ""}>{patientSummary?.comorbidities?.high_blood_pressure ? "TRUE" : "FALSE"}</td></tr>
                        <tr><td>Anaemia</td><td className={patientSummary?.comorbidities?.anaemia ? "value-critical" : ""}>{patientSummary?.comorbidities?.anaemia ? "TRUE" : "FALSE"}</td></tr>
                        <tr><td>Smoking</td><td className={patientSummary?.comorbidities?.smoking ? "value-critical" : ""}>{patientSummary?.comorbidities?.smoking ? "TRUE" : "FALSE"}</td></tr>
                    </tbody>
                </table>
            </div>


            {/* CENTER PANE: AI ANALYSIS */}
            <div className="cb-pane-center">
                <div className="pane-header">
                    <span>AI TRAJECTORY ANALYSIS</span>
                    <span className="pane-subheader">{patientId} • HRZ: {horizonDays} DAYS • CF: {results ? '0.92' : '--'}</span>
                </div>
                <div style={{ padding: 'var(--spacing-md)', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>

                    <div style={{ marginBottom: 'var(--spacing-md)', padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-base)', border: '1px solid var(--color-border-strong)', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                        <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Predicted Trajectory</h3>
                        <div style={{ flexGrow: 1, backgroundColor: 'var(--color-bg-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <span className="pane-subheader">
                                {results ? `[Trajectory Graph for EF +${((results.recommendations[0]?.predicted_effect?.ejection_fraction_change || 0) * 100).toFixed(1)}% over ${horizonDays}d]` : '[AWAITING AI COMPILE]'}
                            </span>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                        <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-base)', border: '1px solid var(--color-border-strong)' }}>
                            <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Risk Factors</h3>
                            <div style={{ marginBottom: '8px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-xs)' }}>
                                    <span className="pane-subheader">Mortality Risk</span>
                                    {results && <span className="value-highlight" style={{ marginRight: 'auto', marginLeft: '4px' }}>→ {targetMortality.toFixed(1)}%</span>}
                                    <span className="value-critical">{currentRisk.mortality}%</span>
                                </div>
                                <BulletGraph value={results ? targetMortality : currentRisk.mortality} min={0} max={100} normalLow={0} normalHigh={10} width="100%" />
                            </div>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-xs)' }}>
                                    <span className="pane-subheader">Readmission</span>
                                    {results && <span className="value-highlight" style={{ marginRight: 'auto', marginLeft: '4px' }}>→ {targetReadmission.toFixed(1)}%</span>}
                                    <span className="value-highlight">{currentRisk.readmission}%</span>
                                </div>
                                <BulletGraph value={results ? targetReadmission : currentRisk.readmission} min={0} max={100} normalLow={0} normalHigh={15} width="100%" />
                            </div>
                        </div>

                        <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-base)', border: '1px solid var(--color-border-strong)' }}>
                            <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Current Medications</h3>
                            {patientSummary?.current_medications && patientSummary.current_medications.length > 0 ? (
                                patientSummary.current_medications.map((med: string, idx: number) => (
                                    <span key={idx} style={{ display: 'inline-block', backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-strong)', padding: '2px 6px', fontSize: 'var(--font-size-xs)', borderRadius: '2px', marginRight: '4px', marginBottom: '4px' }}>
                                        {med.toUpperCase()}
                                    </span>
                                ))
                            ) : (
                                <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>NO ACTIVE MEDICATIONS</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>


            {/* RIGHT PANE: ORDER ENTRY / SCENARIOS */}
            <div className="cb-pane-right">
                <div className="pane-header">
                    <span>TX SCENARIOS & ORDERS</span>
                    <button className="btn btn-primary" style={{ padding: '2px 8px', fontSize: '10px' }} onClick={handleRunAI} disabled={isLoading}>
                        {isLoading ? 'CALCULATING...' : 'RUN AI OVERRIDE'}
                    </button>
                </div>

                <div style={{ padding: 'var(--spacing-md)' }}>
                    <div className="form-group" style={{ padding: '0 0 var(--spacing-sm) 0' }}>
                        <label className="form-label">Time Horizon (Days)</label>
                        <input type="number" className="form-input" value={horizonDays} onChange={(e) => setHorizonDays(parseInt(e.target.value) || 90)} />
                    </div>

                    <h3 style={{ marginTop: 'var(--spacing-lg)', marginBottom: 'var(--spacing-sm)' }}>Recommended Action</h3>
                    {results ? (
                        <div style={{ border: '2px solid var(--color-accent-blue)', backgroundColor: 'var(--color-bg-surface)', padding: 'var(--spacing-md)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-xs)' }}>
                                <span style={{ fontWeight: 700, textTransform: 'uppercase' }}>{results.summary?.top_recommendation?.medication?.replace('_', ' ')}</span>
                                <span style={{ color: results.recommendations[0]?.is_safe ? 'var(--color-accent-green)' : 'var(--color-accent-red)', fontWeight: 700, fontSize: 'var(--font-size-xs)' }}>
                                    {results.recommendations[0]?.is_safe ? 'SAFE' : 'CONTRAINDICATED'}
                                </span>
                            </div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-md)' }}>
                                Expected EF Improvement: +{((results.recommendations[0]?.predicted_effect?.ejection_fraction_change || 0) * 100).toFixed(1)}%<br />
                                Mortality Risk Reduction: {((results.recommendations[0]?.predicted_effect?.mortality_risk_change || 0) * 100).toFixed(1)}%<br />
                                Confidence Score: {(results.summary?.top_recommendation?.score || 0).toFixed(2)}
                            </div>
                            <button className="btn btn-primary" style={{ width: '100%' }}>ACCEPT & ORDER</button>
                        </div>
                    ) : (
                        <div style={{ border: '1px dashed var(--color-border-strong)', padding: 'var(--spacing-lg)', textAlign: 'center', backgroundColor: 'var(--color-bg-surface)' }}>
                            <span className="pane-subheader">Run AI to general physiological digital twin options.</span>
                        </div>
                    )}

                    <h3 style={{ marginTop: 'var(--spacing-lg)', marginBottom: 'var(--spacing-sm)' }}>Document Parse</h3>
                    <div style={{ border: '1px solid var(--color-border-subtle)', padding: 'var(--spacing-md)', textAlign: 'center', backgroundColor: 'var(--color-bg-surface)', cursor: 'pointer' }}>
                        <span className="pane-subheader">Click to inject Prescription/Lab OCR</span>
                    </div>
                </div>
            </div>

        </div>
    );
};

export default ClinicalBoard;
