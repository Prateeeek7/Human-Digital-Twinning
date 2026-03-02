import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ClinicalLayout from './components/ClinicalLayout';
import ClinicalBoard from './pages/ClinicalBoard';
import OrdersBoard from './pages/OrdersBoard';
import MasterPatientIndex from './pages/MasterPatientIndex';
import BedBoard from './pages/BedBoard';
import ResultsInbox from './pages/ResultsInbox';
import ScheduleBoard from './pages/ScheduleBoard';

import LoginLanding from './pages/LoginLanding';
import PatientSelect from './pages/PatientSelect';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Entry & Gateway Routes (No Clinical Layout Sidebar) */}
        <Route path="/" element={<LoginLanding />} />
        <Route path="/patients" element={<PatientSelect />} />

        {/* Protected Clinical Working Routes (Wrapped in Hospital Shell) */}
        <Route path="/board" element={<ClinicalLayout><ClinicalBoard /></ClinicalLayout>} />
        <Route path="/orders" element={<ClinicalLayout><OrdersBoard /></ClinicalLayout>} />
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
