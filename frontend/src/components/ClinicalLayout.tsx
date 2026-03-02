import React, { useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import PatientBanner from './PatientBanner';
import ProviderSettings from './ProviderSettings';
import './ClinicalLayout.css';
import { Activity, Stethoscope, Settings, Menu, Users, Bed, Inbox, Calendar, FileText, X, UserX, Monitor } from 'lucide-react';

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
                    <Link to="/orders" className={`as-nav-item ${location.pathname === '/orders' ? 'active' : ''}`}>
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
                </nav>
                <div className="sm-footer">
                    <span>EHR CONNECTION: ACTIVE</span>
                    <span>LAST SYNC: 0.2s</span>
                </div>
            </div>

            {/* Patient Context Banner */}
            <header className="patient-banner">
                <PatientBanner />
            </header>

            {/* Main Workspace Grid */}
            <main className="workspace">
                {children}
            </main>
        </div >
    );
};

export default ClinicalLayout;
