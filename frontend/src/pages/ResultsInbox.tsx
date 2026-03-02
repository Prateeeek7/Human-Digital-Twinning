import React, { useState, useEffect } from 'react';
import { getInboxResults } from '../services/api';
import { Inbox, AlertCircle, CheckCircle } from 'lucide-react';
import './HospitalModules.css';

const ResultsInbox: React.FC = () => {
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInbox = async () => {
            setLoading(true);
            try {
                const data = await getInboxResults();
                setResults(data);
            } catch (err) {
                console.error("Failed to load results inbox", err);
            } finally {
                setLoading(false);
            }
        };
        fetchInbox();
    }, []);

    // Helper to format JSON details if it's lab data
    const formatDetails = (detailsStr: string) => {
        try {
            const parsed = JSON.parse(detailsStr);
            return Object.entries(parsed).map(([k, v]) => `${k}: ${v}`).join(' | ');
        } catch {
            return detailsStr; // It's just a string, like imaging dictation
        }
    };

    return (
        <div className="module-container">
            <div className="module-header">
                <h2><Inbox size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> PROVIDER INBOX (RESULTS ROUTING)</h2>
                <div className="module-actions">
                    <span className="census-count">PENDING REVIEW: {results.length}</span>
                    <button className="h-action-btn primary">MARK ALL REVIEWED</button>
                </div>
            </div>

            <div className="module-content">
                {loading ? (
                    <div className="loading-state">[ FETCHING INBOX ROUTING... ]</div>
                ) : (
                    <table className="hospital-table">
                        <thead>
                            <tr>
                                <th>STATUS</th>
                                <th>PATIENT</th>
                                <th>ORDER TYPE</th>
                                <th>PANEL / EXAM</th>
                                <th>RESULT DETAILS</th>
                                <th>RESULT TIME</th>
                                <th>ACTIONS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results.map(r => (
                                <tr key={r.result_id} className={r.flag === 'Critical' ? 'row-critical' : ''}>
                                    <td>
                                        <div className="status-flex">
                                            {r.flag === 'Abnormal' || r.flag === 'Critical' ?
                                                <AlertCircle size={14} className="text-critical" /> :
                                                <CheckCircle size={14} className="text-normal" />
                                            }
                                            <span className={`status-text ${r.status === 'Preliminary' ? 'status-prelim' : ''}`}>
                                                {r.status.toUpperCase()}<br />
                                                {r.flag !== 'Normal' && <span className="flag-alert">({r.flag})</span>}
                                            </span>
                                        </div>
                                    </td>
                                    <td><b>{r.last_name}, {r.first_name}</b><br /><span className="mono subtext">{r.mrn}</span></td>
                                    <td>{r.order_type}</td>
                                    <td><b>{r.panel_name}</b><br /><span className="mono subtext">{r.result_id}</span></td>
                                    <td className="result-details">{formatDetails(r.result_details)}</td>
                                    <td className="mono">{new Date(r.result_time).toLocaleString()}</td>
                                    <td>
                                        <button className="h-action-btn">ACKNOWLEDGE</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default ResultsInbox;
