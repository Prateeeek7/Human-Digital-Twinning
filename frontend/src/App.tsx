import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ClinicalLayout from './components/ClinicalLayout';
import ClinicalBoard from './pages/ClinicalBoard';
import OrdersBoard from './pages/OrdersBoard';
import MasterPatientIndex from './pages/MasterPatientIndex';
import BedBoard from './pages/BedBoard';
import ResultsInbox from './pages/ResultsInbox';
import ScheduleBoard from './pages/ScheduleBoard';

function App() {
  return (
    <BrowserRouter>
      <ClinicalLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/board" replace />} />
          <Route path="/board" element={<ClinicalBoard />} />
          <Route path="/orders" element={<OrdersBoard />} />
          <Route path="/mpi" element={<MasterPatientIndex />} />
          <Route path="/bedboard" element={<BedBoard />} />
          <Route path="/results" element={<ResultsInbox />} />
          <Route path="/schedule" element={<ScheduleBoard />} />
        </Routes>
      </ClinicalLayout>
    </BrowserRouter>
  );
}

export default App;
