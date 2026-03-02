import React, { useState, useEffect } from 'react';
import { getSchedule } from '../services/api';
import { Calendar, Clock, MapPin } from 'lucide-react';
import './HospitalModules.css';

const ScheduleBoard: React.FC = () => {
    const [schedule, setSchedule] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSchedule = async () => {
            setLoading(true);
            try {
                const data = await getSchedule();
                setSchedule(data);
            } catch (err) {
                console.error("Failed to load schedule", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSchedule();
    }, []);

    return (
        <div className="module-container">
            <div className="module-header">
                <h2><Calendar size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> SURGICAL & CLINIC SCHEDULE</h2>
                <div className="module-actions">
                    <span className="census-count">TOTAL CASES: {schedule.length}</span>
                </div>
            </div>

            <div className="module-content">
                {loading ? (
                    <div className="loading-state">[ FETCHING DAILY SCHEDULE... ]</div>
                ) : (
                    <table className="hospital-table">
                        <thead>
                            <tr>
                                <th>TIME / DURATION</th>
                                <th>STATUS</th>
                                <th>LOCATION</th>
                                <th>PATIENT</th>
                                <th>EVENT TYPE</th>
                                <th>CLINICAL NOTES</th>
                            </tr>
                        </thead>
                        <tbody>
                            {schedule.map(s => {
                                const st = new Date(s.start_time);
                                return (
                                    <tr key={s.appointment_id} className={s.status === 'In Progress' ? 'row-active' : ''}>
                                        <td className="mono">
                                            <b>{st.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</b><br />
                                            <span className="subtext">{st.toLocaleDateString()} ({s.duration_mins}m)</span>
                                        </td>
                                        <td>
                                            <span className={`status-badge stat-${s.status.replace(' ', '').toLowerCase()}`}>
                                                {s.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td><MapPin size={12} /> <b>{s.location}</b></td>
                                        <td><b>{s.last_name}, {s.first_name}</b><br /><span className="subtext">{s.gender} | {s.dob}</span></td>
                                        <td>{s.event_type}<br /><span className="mono subtext">{s.appointment_id}</span></td>
                                        <td className="notes-col">{s.notes}</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default ScheduleBoard;
