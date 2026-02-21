import { useEffect } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import AnalysisPageHybrid from './pages/AnalysisPageHybrid';
import ComparePage from './pages/ComparePage';
import WhatIfPage from './pages/WhatIfPage';

function App() {
  return (
    <div style={{ background: '#02060a', minHeight: '100vh' }}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/analysis" element={<AnalysisPageHybrid />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/what-if" element={<WhatIfPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
