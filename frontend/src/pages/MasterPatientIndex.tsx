import React, { useState, useEffect } from 'react';
import { getMPIPatients } from '../services/api';
import { Users, Search, Phone, MapPin } from 'lucide-react';
import './HospitalModules.css';

// Debounce hook
export const useDebounce = (value: string, delay: number) => {
    const [debouncedValue, setDebouncedValue] = useState(value);
    useEffect(() => {
        const handler = setTimeout(() => { setDebouncedValue(value); }, delay);
        return () => clearTimeout(handler);
    }, [value, delay]);
    return debouncedValue;
};

const MasterPatientIndex: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 400);
    const [patients, setPatients] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

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

    return (
        <div className="module-container">
            <div className="module-header">
                <h2><Users size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> MASTER PATIENT INDEX (MPI)</h2>
                <div className="module-actions search-wrapper">
                    <Search size={14} className="search-icon" />
                    <input
                        type="text"
                        className="hospital-search"
                        placeholder="Search by MRN, Last Name, First Name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="module-content">
                {loading ? (
                    <div className="loading-state">[ SEARCHING MPI DATABASE... ]</div>
                ) : patients.length === 0 ? (
                    <div className="loading-state">No matching records found.</div>
                ) : (
                    <table className="hospital-table">
                        <thead>
                            <tr>
                                <th>MRN / ID</th>
                                <th>PATIENT NAME</th>
                                <th>DOB / GENDER</th>
                                <th>CONTACT</th>
                                <th>ADDRESS</th>
                                <th>PRIMARY CARE (PCP)</th>
                                <th>ACTIONS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {patients.map(p => (
                                <tr key={p.id}>
                                    <td className="mono"><b>{p.mrn}</b><br /><span className="subtext">{p.id}</span></td>
                                    <td style={{ fontSize: '14px' }}><b>{p.last_name}, {p.first_name}</b></td>
                                    <td>{p.dob}<br />{p.gender}</td>
                                    <td><Phone size={12} /> {p.phone}</td>
                                    <td><MapPin size={12} /> {p.address}</td>
                                    <td>{p.pcp_name}</td>
                                    <td>
                                        <button className="h-action-btn">OPEN CHART</button>
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

export default MasterPatientIndex;
