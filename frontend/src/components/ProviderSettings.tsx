import React, { useState, useEffect } from 'react';
import { getProviderPreferences, updateProviderPreferences } from '../services/api';
import { X, Save, Monitor, AlertTriangle, ShieldAlert } from 'lucide-react';
import './ProviderSettings.css';

interface ProviderSettingsProps {
    isOpen: boolean;
    onClose: () => void;
    initialTab?: 'display' | 'alerts' | 'security';
}

interface Preferences {
    provider_id: string;
    theme: string;
    density: string;
    alert_threshold_hr: number;
    session_timeout_minutes: number;
}

const ProviderSettings: React.FC<ProviderSettingsProps> = ({ isOpen, onClose, initialTab = 'display' }) => {
    const [activeTab, setActiveTab] = useState(initialTab);
    const [prefs, setPrefs] = useState<Preferences | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setActiveTab(initialTab);
            fetchPreferences();
        }
    }, [isOpen, initialTab]);

    const fetchPreferences = async () => {
        setLoading(true);
        try {
            const data = await getProviderPreferences("DR-SMITH");
            setPrefs(data);
        } catch (error) {
            console.error("Failed to load preferences:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!prefs) return;
        setSaving(true);
        try {
            await updateProviderPreferences("DR-SMITH", prefs);
            document.body.setAttribute('data-theme', prefs.theme);
            if (prefs.density === 'comfortable') {
                document.body.setAttribute('data-density', prefs.density);
            } else {
                document.body.removeAttribute('data-density');
            }
            localStorage.setItem('hl7_alert_hr', prefs.alert_threshold_hr.toString());
            onClose(); // Close on successful save
        } catch (error) {
            console.error("Failed to save preferences:", error);
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (field: keyof Preferences, value: any) => {
        if (prefs) {
            setPrefs({ ...prefs, [field]: value });
        }
    };

    if (!isOpen) return null;

    return (
        <div className="ps-overlay">
            <div className="ps-modal">
                <div className="ps-header">
                    <div className="ps-title">Provider Preferences - DR-SMITH</div>
                    <button className="ps-close" onClick={onClose}><X size={16} /></button>
                </div>

                {loading ? (
                    <div className="ps-loading">Loading preferences from EHR core...</div>
                ) : (
                    <div className="ps-content">
                        <div className="ps-sidebar">
                            <button
                                className={`ps-tab ${activeTab === 'display' ? 'active' : ''}`}
                                onClick={() => setActiveTab('display')}
                            >
                                <Monitor size={14} /> Display Settings
                            </button>
                            <button
                                className={`ps-tab ${activeTab === 'alerts' ? 'active' : ''}`}
                                onClick={() => setActiveTab('alerts')}
                            >
                                <AlertTriangle size={14} /> Alert Thresholds
                            </button>
                            <button
                                className={`ps-tab text-critical ${activeTab === 'security' ? 'active' : ''}`}
                                onClick={() => setActiveTab('security')}
                            >
                                <ShieldAlert size={14} /> Session Lock
                            </button>
                        </div>

                        <div className="ps-main">
                            {activeTab === 'display' && (
                                <div className="ps-panel">
                                    <h3 className="ps-panel-title">Display Settings</h3>

                                    <div className="ps-form-group">
                                        <label>UI Theme</label>
                                        <select
                                            value={prefs?.theme || 'system'}
                                            onChange={(e) => handleChange('theme', e.target.value)}
                                        >
                                            <option value="system">System Default</option>
                                            <option value="light">High Contrast Light</option>
                                            <option value="dark">Cinematic Dark</option>
                                        </select>
                                    </div>

                                    <div className="ps-form-group">
                                        <label>Data Density</label>
                                        <select
                                            value={prefs?.density || 'compact'}
                                            onChange={(e) => handleChange('density', e.target.value)}
                                        >
                                            <option value="compact">Compact (Hospital Standard)</option>
                                            <option value="comfortable">Comfortable (Tablet Optimized)</option>
                                        </select>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'alerts' && (
                                <div className="ps-panel">
                                    <h3 className="ps-panel-title">Clinical Alert Thresholds</h3>
                                    <p className="ps-desc">Configure boundaries for real-time temporal pushes.</p>

                                    <div className="ps-form-group inline-number">
                                        <label>Max Heart Rate Threshold (BPM)</label>
                                        <input
                                            type="number"
                                            min="60"
                                            max="200"
                                            value={prefs?.alert_threshold_hr || 100}
                                            onChange={(e) => handleChange('alert_threshold_hr', parseInt(e.target.value))}
                                        />
                                    </div>
                                </div>
                            )}

                            {activeTab === 'security' && (
                                <div className="ps-panel">
                                    <h3 className="ps-panel-title">Session Lock Interface</h3>
                                    <p className="ps-desc text-critical">Modifying security thresholds requires administrative approval on production instances.</p>

                                    <div className="ps-form-group inline-number">
                                        <label>Idle Auto-Lock Timeout (Minutes)</label>
                                        <input
                                            type="number"
                                            min="1"
                                            max="60"
                                            value={prefs?.session_timeout_minutes || 15}
                                            onChange={(e) => handleChange('session_timeout_minutes', parseInt(e.target.value))}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <div className="ps-footer">
                    <button className="btn-secondary" onClick={onClose}>Cancel</button>
                    <button
                        className="btn-primary"
                        onClick={handleSave}
                        disabled={loading || saving}
                    >
                        {saving ? 'Saving to Database...' : <><Save size={14} /> Commit Changes</>}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProviderSettings;
