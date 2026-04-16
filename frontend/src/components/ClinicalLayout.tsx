import React, { useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import PatientBanner from './PatientBanner';
import ProviderSettings from './ProviderSettings';
import './ClinicalLayout.css';
import { Activity, Stethoscope, Settings, Menu, Users, Bed, Inbox, Calendar, FileText, X, UserX, Monitor, LogOut } from 'lucide-react';

interface ClinicalLayoutProps {
    children: React.ReactNode;
}

const ClinicalLayout: React.FC<ClinicalLayoutProps> = ({ children }) => {
    const location = useLocation();
    const { id } = useParams<{ id: string }>();
    const activeId = id || 'PT-001';
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    // Provider Settings Modal State
    const [isProviderSettingsOpen, setIsProviderSettingsOpen] = useState(false);
    const [providerSettingsTab, setProviderSettingsTab] = useState<'display' | 'alerts' | 'security'>('display');

    // Discharge Modal State
    const [isDischargeModalOpen, setIsDischargeModalOpen] = useState(false);
    const [dischargeRemark, setDischargeRemark] = useState('');

    const openSettings = (tab: 'display' | 'alerts' | 'security') => {
        setProviderSettingsTab(tab);
        setIsProviderSettingsOpen(true);
        setIsSettingsOpen(false); // Close dropdown
    };

    return (
        <div className="app-container">
            {/* Top Application Bar (Very thin, utility only) */}
            <div className="app-statusbar">
                <div className="as-left">
                    <button
                        className={`as-menu-btn ${isMenuOpen ? 'active' : ''}`}
                        title="Main Menu"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                    >
                        {isMenuOpen ? <X size={16} /> : <Menu size={16} />}
                    </button>
                    <span className="as-brand">HF-DIGITAL TWIN <span className="as-version">v0.2</span></span>
                </div>
                <div className="as-nav">
                    <Link to={`/board/${activeId}`} className={`as-nav-item ${location.pathname.startsWith('/board') ? 'active' : ''}`}>
                        <Activity size={14} /> Clinical Board
                    </Link>
                    <Link to={`/orders/${activeId}`} className={`as-nav-item ${location.pathname.startsWith('/orders') ? 'active' : ''}`}>
                        <Stethoscope size={14} /> Orders
                    </Link>
                </div>
                <div className="as-right">
                    <span className="as-status-indicator online"></span>
                    <span className="as-status-text">SYSTEM SECURE</span>
                    <div className="as-settings-wrapper">
                        <button
                            className={`as-icon-btn ${isSettingsOpen ? 'active' : ''}`}
                            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                        >
                            <Settings size={14} />
                        </button>

                        {/* Settings Dropdown */}
                        {isSettingsOpen && (
                            <div className="settings-dropdown">
                                <div className="sd-header">PROVIDER PREFERENCES</div>
                                <button className="sd-item" onClick={() => openSettings('display')}><Monitor size={14} /> Display Settings</button>
                                <button className="sd-item" onClick={() => openSettings('alerts')}><Activity size={14} /> Alert Thresholds</button>
                                <div className="sd-divider"></div>
                                <button className="sd-item" onClick={() => { setIsDischargeModalOpen(true); setIsSettingsOpen(false); }}><LogOut size={14} /> Discharge Patient</button>
                                <button className="sd-item text-critical" onClick={() => openSettings('security')}><UserX size={14} /> Session Lock</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <ProviderSettings
                isOpen={isProviderSettingsOpen}
                onClose={() => setIsProviderSettingsOpen(false)}
                initialTab={providerSettingsTab}
            />

            {/* Slide-out Main Menu overlay */}
            <div className={`app-sidebar ${isMenuOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    HOSPITAL MODULES
                </div>
                <nav className="sidebar-nav">
                    <Link to="/mpi" className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <Users size={16} /> Master Patient Index
                    </Link>
                    <Link to="/bedboard" className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <Bed size={16} /> Bed Board / Unit View
                    </Link>
                    <Link to="/results" className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <Inbox size={16} /> Results Routing
                    </Link>
                    <Link to="/schedule" className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <Calendar size={16} /> Schedule & OR
                    </Link>
                    <div className="sidebar-divider"></div>
                    <Link to={`/board/${activeId}`} className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <FileText size={16} /> Patient Chart ({activeId})
                    </Link>
                    <div className="sidebar-divider"></div>
                    <Link to="/" className="sidebar-link text-critical" onClick={() => setIsMenuOpen(false)}>
                        <LogOut size={16} /> Sign Out
                    </Link>
                </nav>
                <div className="sm-footer">
                    <span>EHR CONNECTION: ACTIVE</span>
                    <span>LAST SYNC: 0.2s</span>
                </div>
            </div>

            {/* Patient Context Banner */}
            <header className="patient-banner">
                <PatientBanner patientId={activeId} />
            </header>

            {/* Main Workspace Grid */}
            <main className="workspace">
                {children}
            </main>

            {/* Discharge Modal */}
            {isDischargeModalOpen && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999,
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                    <div style={{
                        backgroundColor: 'var(--color-bg-base)',
                        padding: 'var(--spacing-xl)',
                        borderRadius: 'var(--radius-md)',
                        width: '400px',
                        border: '1px solid var(--color-border-strong)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
                            <h3 style={{ margin: 0, fontSize: 'var(--font-size-lg)', color: 'var(--color-text-primary)' }}>Discharge Patient</h3>
                            <button onClick={() => setIsDischargeModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}><X size={18} /></button>
                        </div>
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-md)', lineHeight: '1.4' }}>
                            Are you sure you want to discharge patient <strong>{activeId}</strong>? Please provide a discharge remark below.
                        </p>
                        <textarea 
                            value={dischargeRemark}
                            onChange={(e) => setDischargeRemark(e.target.value)}
                            placeholder="Enter discharge remarks / instructions..."
                            style={{
                                width: '100%', minHeight: '80px', padding: 'var(--spacing-sm)',
                                fontSize: 'var(--font-size-sm)', fontFamily: 'inherit',
                                border: '1px solid var(--color-border-strong)', borderRadius: 'var(--radius-sm)',
                                marginBottom: 'var(--spacing-lg)',
                                resize: 'vertical'
                            }}
                        />
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)' }}>
                            <button onClick={() => setIsDischargeModalOpen(false)} style={{ padding: '6px 16px', background: 'transparent', border: '1px solid var(--color-border-strong)', cursor: 'pointer', fontWeight: 600, fontSize: '11px' }}>CANCEL</button>
                            <button onClick={() => {
                                alert(`Patient ${activeId} discharged successfully.\nRemark: ${dischargeRemark}`);
                                setIsDischargeModalOpen(false);
                                setDischargeRemark('');
                            }} style={{ padding: '6px 16px', backgroundColor: 'var(--color-accent-blue)', color: 'white', border: 'none', cursor: 'pointer', fontWeight: 600, borderRadius: 'var(--radius-sm)', fontSize: '11px' }}>
                                CONFIRM DISCHARGE
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div >
    );
};

export default ClinicalLayout;
