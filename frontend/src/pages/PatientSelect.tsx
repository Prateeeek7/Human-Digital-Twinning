import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMPIPatients } from '../services/api';
import { Search, Phone, MapPin, LogOut, UserPlus, Shield } from 'lucide-react';
import './PatientSelect.css';

// Reuse debounce hook locally to avoid coupling
const useDebounce = (value: string, delay: number) => {
    const [debouncedValue, setDebouncedValue] = useState(value);
    useEffect(() => {
        const handler = setTimeout(() => { setDebouncedValue(value); }, delay);
        return () => clearTimeout(handler);
    }, [value, delay]);
    return debouncedValue;
};

const PatientSelect: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 400);
    const [patients, setPatients] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchMPI = async () => {
            setLoading(true);
            try {
                const data = await getMPIPatients(debouncedSearch);
                setPatients(data);
            } catch (err) {
                console.error("Failed to load MPI", err);
            } finally {
                setLoading(false);
            }
        };
        fetchMPI();
    }, [debouncedSearch]);

    const handleSelectPatient = (patientId: string) => {
        // Log the initialized patient context
        console.log(`Initializing twin for patient context: ${patientId}`);
        // In a real app we'd save this to context, here we'll just navigate
        navigate('/board');
    };

    const handleLogout = () => {
        navigate('/');
    };

    return (
        <div className="gateway-container">
            <header className="gateway-header">
                <div className="gh-brand">
                    <Shield size={20} className="gh-icon" />
                    <span>HF-DIGITAL TWIN SECURE GATEWAY</span>
                </div>
                <div className="gh-user">
                    <span className="gh-provider">DR-SMITH</span>
                    <button className="gh-logout" onClick={handleLogout}><LogOut size={16} /> SIGN OUT</button>
                </div>
            </header>

            <main className="gateway-main">
                <div className="gt-toolbar">
                    <div className="gt-title">
                        <h1>Select Patient Context</h1>
                        <p>Search the Master Patient Index to initialize the digital twin.</p>
                    </div>
                    <div className="gt-actions">
                        <div className="gt-search-box">
                            <Search size={16} className="gt-search-icon" />
                            <input
                                type="text"
                                placeholder="Search Name, MRN, or DOB..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <button className="gt-new-btn"><UserPlus size={16} /> NEW ENCOUNTER</button>
                    </div>
                </div>

                <div className="gt-content">
                    {loading ? (
                        <div className="gt-empty">[ QUERYING CORE NODES... ]</div>
                    ) : patients.length === 0 ? (
                        <div className="gt-empty">No patient records found in MPI.</div>
                    ) : (
                        <table className="gt-table">
                            <thead>
                                <tr>
                                    <th>MRN / ID</th>
                                    <th>PATIENT NAME</th>
                                    <th>DOB / GENDER</th>
                                    <th>CONTACT</th>
                                    <th>ACTION</th>
                                </tr>
                            </thead>
                            <tbody>
                                {patients.slice(0, 15).map(p => (
                                    <tr key={p.id}>
                                        <td className="gt-mono"><b>{p.mrn}</b><br /><span>{p.id}</span></td>
                                        <td className="gt-name">{p.last_name}, {p.first_name}</td>
                                        <td>{p.dob}<br />{p.gender}</td>
                                        <td className="gt-contact">
                                            <div><Phone size={12} /> {p.phone}</div>
                                            <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}><MapPin size={12} /> {p.address.substring(0, 30)}...</div>
                                        </td>
                                        <td>
                                            <button
                                                className="gt-select-btn"
                                                onClick={() => handleSelectPatient(p.id)}
                                            >
                                                INITIALIZE TWIN
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </main>
        </div>
    );
};

export default PatientSelect;
