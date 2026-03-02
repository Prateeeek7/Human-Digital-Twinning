import React, { useState, useEffect } from 'react';
import { getBedBoard } from '../services/api';
import { Bed, User, Activity, Clock } from 'lucide-react';
import './HospitalModules.css';

const BedBoard: React.FC = () => {
    const [patients, setPatients] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterUnit, setFilterUnit] = useState('');

    useEffect(() => {
        const fetchBoard = async () => {
            setLoading(true);
            try {
                const data = await getBedBoard(filterUnit);
                setPatients(data);
            } catch (err) {
                console.error("Failed to load bed board", err);
            } finally {
                setLoading(false);
            }
        };
        fetchBoard();
    }, [filterUnit]);

    return (
        <div className="module-container">
            <div className="module-header">
                <h2><Bed size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> INPATIENT CENSUS (BED BOARD)</h2>
                <div className="module-actions">
                    <select
                        value={filterUnit}
                        onChange={(e) => setFilterUnit(e.target.value)}
                        className="hospital-select"
                    >
                        <option value="">All Units</option>
                        <option value="Medical Intensive Care Unit (MICU)">MICU</option>
                        <option value="Surgical Intensive Care Unit (SICU)">SICU</option>
                        <option value="Cardiovascular ICU (CVICU)">CVICU</option>
                        <option value="East Wing Telemetry">East Wing Telemetry</option>
                        <option value="West Wing Med/Surg">West Wing Med/Surg</option>
                    </select>
                    <span className="census-count">TOTAL ADMISSIONS: {patients.length}</span>
                </div>
            </div>

            <div className="module-content">
                {loading ? (
                    <div className="loading-state">[ FETCHING CENSUS DATA... ]</div>
                ) : (
                    <table className="hospital-table">
                        <thead>
                            <tr>
                                <th>UNIT/ROOM</th>
                                <th>PATIENT NAME</th>
                                <th>MRN</th>
                                <th>ACUITY</th>
                                <th>CHIEF COMPLAINT</th>
                                <th>ATTENDING</th>
                                <th>ADMIT TIME</th>
                            </tr>
                        </thead>
                        <tbody>
                            {patients.map(p => (
                                <tr key={p.visit_id} className={p.acuity === 'Critical' ? 'row-critical' : ''}>
                                    <td className="mono">{p.unit}<br /><b>{p.room_bed}</b></td>
                                    <td><b>{p.last_name}, {p.first_name}</b><br /><span className="subtext">{p.gender} | {p.dob}</span></td>
                                    <td className="mono">{p.mrn}</td>
                                    <td>
                                        <span className={`acuity-badge ${p.acuity.toLowerCase()}`}>
                                            {p.acuity.toUpperCase()}
                                        </span>
                                    </td>
                                    <td>{p.chief_complaint}</td>
                                    <td>{p.attending_physician}</td>
                                    <td className="mono">{new Date(p.admission_time).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default BedBoard;
