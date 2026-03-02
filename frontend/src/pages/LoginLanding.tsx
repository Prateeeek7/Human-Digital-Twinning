import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Fingerprint, Lock } from 'lucide-react';
import './LoginLanding.css';

const LoginLanding: React.FC = () => {
    const [providerId, setProviderId] = useState('DR-SMITH');
    const [password, setPassword] = useState('••••••••');
    const [isAuthenticating, setIsAuthenticating] = useState(false);
    const navigate = useNavigate();

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setIsAuthenticating(true);

        // Simulate authentication delay
        setTimeout(() => {
            setIsAuthenticating(false);
            // Navigate to Patient Selection Gateway
            navigate('/patients');
        }, 800);
    };

    return (
        <div className="login-container">
            <div className="login-backdrop"></div>
            <div className="login-panel">
                <div className="login-header">
                    <Shield className="login-logo-icon" size={32} />
                    <h1 className="login-brand">HF-DIGITAL TWIN</h1>
                    <span className="login-version">SYSTEM CORE v0.2</span>
                </div>

                <form className="login-form" onSubmit={handleLogin}>
                    <div className="login-warning">
                        <Lock size={12} />
                        AUTHORIZED CLINICAL PERSONNEL ONLY.
                    </div>

                    <div className="form-group">
                        <label>PROVIDER ID (UPN)</label>
                        <input
                            type="text"
                            value={providerId}
                            onChange={(e) => setProviderId(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>PASSPHRASE</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="login-btn" disabled={isAuthenticating}>
                        {isAuthenticating ? (
                            <span className="btn-content">AUTHENTICATING...</span>
                        ) : (
                            <span className="btn-content"><Fingerprint size={16} /> INITIALIZE SESSION</span>
                        )}
                    </button>

                    <div className="login-footer">
                        Secure EHR Integration Layer • Connected to SQLite Core Nodes
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LoginLanding;
