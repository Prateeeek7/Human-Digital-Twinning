import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import PatientBanner from './PatientBanner';
import './ClinicalLayout.css';
import { Activity, Stethoscope, Settings, Menu, Users, Bed, Inbox, Calendar, FileText, X, UserX, Monitor } from 'lucide-react';

interface ClinicalLayoutProps {
    children: React.ReactNode;
}

const ClinicalLayout: React.FC<ClinicalLayoutProps> = ({ children }) => {
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

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
                    <Link to="/board" className={`as-nav-item ${location.pathname === '/board' ? 'active' : ''}`}>
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
                                <button className="sd-item"><Monitor size={14} /> Display Settings</button>
                                <button className="sd-item"><Activity size={14} /> Alert Thresholds</button>
                                <div className="sd-divider"></div>
                                <button className="sd-item text-critical"><UserX size={14} /> Session Lock</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

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
                    <Link to="/board" className="sidebar-link" onClick={() => setIsMenuOpen(false)}>
                        <FileText size={16} /> Patient Chart (PT-001)
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
        </div>
    );
};

export default ClinicalLayout;
