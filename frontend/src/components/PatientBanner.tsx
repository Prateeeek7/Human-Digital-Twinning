import React, { useState, useEffect } from 'react';
import './PatientBanner.css';
import { AlertTriangle, Info } from 'lucide-react';
import { getPatientSummary } from '../services/api';

interface PatientBannerProps {
    patientId: string;
}

const PatientBanner: React.FC<PatientBannerProps> = ({ patientId }) => {
    const [patientData, setPatientData] = useState<any>(null);

    useEffect(() => {
        const fetchHeader = async () => {
            try {
                const summary = await getPatientSummary(patientId);
                setPatientData(summary);
            } catch (err) {
                console.error("Failed to load banner data:", err);
            }
        };
        if (patientId) {
            fetchHeader();
        }
    }, [patientId]);

    if (!patientData) {
        return (
            <div className="patient-banner-container" style={{ justifyContent: 'center' }}>
                <span className="pb-name" style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>AWAITING PATIENT CONTEXT...</span>
            </div>
        );
    }

    const p = patientData.demographics || {};

    return (
        <div className="patient-banner-container">
            <div className="pb-primary-info">
                <div className="pb-name" title="Patient Name">{p.name || 'UNKNOWN'}</div>
                <div className="pb-mrn" title="Medical Record Number">{p.mrn || 'N/A'}</div>
                <div className="pb-demographics">
                    {p.age || '--'}y {p.sex || '-'} | DOB: {p.dob || '--'}
                </div>
            </div>

            <div className="pb-physical">
                <div className="pb-data-pair">
                    <span className="pb-label">WT</span>
                    <span className="pb-val">{p.weight || '--'}</span>
                </div>
                <div className="pb-data-pair">
                    <span className="pb-label">HT</span>
                    <span className="pb-val">{p.height || '--'}</span>
                </div>
            </div>

            <div className="pb-critical-info">
                <div className="pb-allergies">
                    <AlertTriangle size={14} className="pb-icon-alert" />
                    <span className="pb-label">ALLERGIES:</span>
                    <span className="pb-val-alert">
                        {Array.isArray(p.allergies) 
                            ? (p.allergies.join(', ') || 'NONE RECORDED') 
                            : (p.allergies || 'NONE RECORDED')}
                    </span>
                </div>
                <div className="pb-code-status">
                    <Info size={14} className="pb-icon-info" />
                    <span className="pb-label">CODE:</span>
                    <span className="pb-val-highlight">{p.code_status || 'UNKNOWN'}</span>
                </div>
            </div>
        </div>
    );
};

export default PatientBanner;
