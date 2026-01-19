import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Activity, UserCog, Database } from 'lucide-react'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/patients', label: 'Patients', icon: UserCog },
    { path: '/medications', label: 'Medications', icon: Database },
  ]

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <img src="/logo.png" alt="HF-Digital Twin Platform" className="logo-icon" />
              <h1>HF-Digital Twin Platform</h1>
            </div>
            <nav className="nav">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`nav-item ${isActive ? 'active' : ''}`}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </header>
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section brand">
              <div className="footer-logo">
                <img src="/logo.png" alt="HF-Digital Twin Platform" className="footer-logo-img" />
                <h3>HF-Digital Twin Platform</h3>
              </div>
              <p className="footer-tagline">
                Hospital-Grade AI for Personalized Medication Recommendations
              </p>
              <p className="footer-about">
                The HF-Digital Twin Platform (PDT) is an AI-powered system designed to provide personalized
                medication recommendations and forecast health trajectories for heart failure patients.
              </p>
            </div>
            <div className="footer-section documentation">
              <h4>Documentation</h4>
              <ul>
                <li><a href="/docs/api-documentation.html" target="_blank" rel="noopener noreferrer">API Documentation</a></li>
                <li><a href="/docs/user-guide.html" target="_blank" rel="noopener noreferrer">User Guide</a></li>
                <li><a href="/docs/technical-documentation.html" target="_blank" rel="noopener noreferrer">Technical Docs</a></li>
                <li><a href="/docs/changelog.html" target="_blank" rel="noopener noreferrer">Changelog</a></li>
              </ul>
            </div>
            <div className="footer-section contact">
              <h4>Contact</h4>
              <ul>
                <li>Email: info@pdt.com</li>
                <li>Support: support@pdt.com</li>
                <li>Version: 0.1.0</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2026 HF-Digital Twin Platform - All rights reserved.</p>
            <p>Disclaimer: This system is for informational purposes only and not a substitute for professional medical advice.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

