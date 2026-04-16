import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { getProviderPreferences } from './services/api';
import ClinicalLayout from './components/ClinicalLayout';
import ClinicalBoard from './pages/ClinicalBoard';
import OrdersBoard from './pages/OrdersBoard';
import MasterPatientIndex from './pages/MasterPatientIndex';
import BedBoard from './pages/BedBoard';
import ResultsInbox from './pages/ResultsInbox';
import ScheduleBoard from './pages/ScheduleBoard';
import NewEncounter from './pages/NewEncounter';

import LoginLanding from './pages/LoginLanding';
import PatientSelect from './pages/PatientSelect';

function App() {
  useEffect(() => {
    let timeoutId: any;

    const setupSessionLock = (minutes: number) => {
        const resetTimer = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                window.location.href = '/'; // Redirect to login
            }, minutes * 60 * 1000);
        };
        window.addEventListener('mousemove', resetTimer);
        window.addEventListener('keypress', resetTimer);
        window.addEventListener('click', resetTimer);
        window.addEventListener('scroll', resetTimer);
        resetTimer();

        return () => {
            clearTimeout(timeoutId);
            window.removeEventListener('mousemove', resetTimer);
            window.removeEventListener('keypress', resetTimer);
            window.removeEventListener('click', resetTimer);
            window.removeEventListener('scroll', resetTimer);
        };
    };

    let cleanupLock: any = null;

    getProviderPreferences("DR-SMITH").then(prefs => {
      if (prefs) {
        document.body.setAttribute('data-theme', prefs.theme);
        if (prefs.density === 'comfortable') {
            document.body.setAttribute('data-density', prefs.density);
        } else {
            document.body.removeAttribute('data-density');
        }
        
        // Store alert threshold globally
        localStorage.setItem('hl7_alert_hr', prefs.alert_threshold_hr.toString());
        
        // Init Security Auto-Lock
        cleanupLock = setupSessionLock(prefs.session_timeout_minutes || 15);
      }
    }).catch(console.error);

    return () => {
        if(cleanupLock) cleanupLock();
    };
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Entry & Gateway Routes (No Clinical Layout Sidebar) */}
        <Route path="/" element={<LoginLanding />} />
        <Route path="/patients" element={<PatientSelect />} />
        <Route path="/new-encounter" element={<NewEncounter />} />

        {/* Protected Clinical Working Routes (Wrapped in Hospital Shell) */}
        <Route path="/board/:id" element={<ClinicalLayout><ClinicalBoard /></ClinicalLayout>} />
        <Route path="/board" element={<Navigate to="/board/PT-001" replace />} />
        <Route path="/orders/:id" element={<ClinicalLayout><OrdersBoard /></ClinicalLayout>} />
        <Route path="/orders" element={<Navigate to="/orders/PT-001" replace />} />
        <Route path="/mpi" element={<ClinicalLayout><MasterPatientIndex /></ClinicalLayout>} />
        <Route path="/bedboard" element={<ClinicalLayout><BedBoard /></ClinicalLayout>} />
        <Route path="/results" element={<ClinicalLayout><ResultsInbox /></ClinicalLayout>} />
        <Route path="/schedule" element={<ClinicalLayout><ScheduleBoard /></ClinicalLayout>} />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
