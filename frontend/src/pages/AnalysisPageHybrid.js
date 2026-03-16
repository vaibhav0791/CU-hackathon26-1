import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, ChevronRight, ChevronLeft, ChevronDown, ChevronUp } from 'lucide-react';
import MoleculeViewer from '../components/MoleculeViewer';
import { exportModernPDF } from '../utils/modernPDFExport';

// Import tab components
import OverviewTab from '../components/tabs/OverviewTab';
import SolubilityTab from '../components/tabs/SolubilityTab';
import FormulationTab from '../components/tabs/FormulationTab';
import StabilityTab from '../components/tabs/StabilityTab';
import PKPDTab from '../components/tabs/PKPDTab';

const TABS = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'solubility', label: 'Solubility', icon: '💧' },
  { id: 'formulation', label: 'Formulation', icon: '💊' },
  { id: 'stability', label: 'Stability', icon: '🛡️' },
  { id: 'pkpd', label: 'PK/PD', icon: '⚡' },
];

const AnalysisPageHybrid = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const result = state?.result || null;
  const [activeTab, setActiveTab] = useState('overview');
  const [exporting, setExporting] = useState(false);

  const handleExportPDF = async () => {
    if (!result) return;
    setExporting(true);
    try {
      exportModernPDF(result);
    } catch (err) {
      console.error('PDF export error:', err);
    } finally {
      setExporting(false);
    }
  };

  const currentTabIndex = TABS.findIndex(t => t.id === activeTab);
  const canGoPrev = currentTabIndex > 0;
  const canGoNext = currentTabIndex < TABS.length - 1;

  const goToPrev = () => canGoPrev && setActiveTab(TABS[currentTabIndex - 1].id);
  const goToNext = () => canGoNext && setActiveTab(TABS[currentTabIndex + 1].id);

  if (!result) {
    return (
      <div style={{ background: '#02060a', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: "'IBM Plex Sans', sans-serif" }}>
        <div style={{ color: '#94a3b8', fontSize: '16px', marginBottom: '24px' }}>No analysis data. Please run an analysis first.</div>
        <button onClick={() => navigate('/')} style={{ background: 'linear-gradient(135deg, #00f2ff, #7000ff)', border: 'none', borderRadius: '24px', padding: '12px 28px', color: 'white', fontWeight: 700, cursor: 'pointer' }}>Back to Home</button>
      </div>
    );
  }

  return (
    <div style={{ background: '#02060a', minHeight: '100vh', fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, backgroundImage: 'linear-gradient(rgba(0,242,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,242,255,0.025) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

      {/* Header */}
      <div style={{ position: 'sticky', top: 0, zIndex: 50, background: 'rgba(2,6,10,0.92)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(0,242,255,0.08)', padding: '0 32px', height: '62px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button onClick={() => navigate('/')} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '8px', padding: '7px 13px', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
            <ArrowLeft size={13} /> Back
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>
              {result.drug_name}
              {result.is_experimental && <span style={{ marginLeft: '8px', background: 'rgba(112,0,255,0.15)', color: '#7000ff', fontSize: '10px', padding: '2px 8px', borderRadius: '10px', fontWeight: 600, letterSpacing: '0.5px' }}>EXPERIMENTAL</span>}
            </span>
          </div>
        </div>
        <button onClick={handleExportPDF} disabled={exporting} style={{ display: 'flex', alignItems: 'center', gap: '7px', background: 'rgba(245,158,11,0.09)', border: '1px solid rgba(245,158,11,0.28)', borderRadius: '8px', padding: '7px 16px', color: '#f59e0b', cursor: exporting ? 'not-allowed' : 'pointer', fontSize: '13px', fontWeight: 600 }}>
          <Download size={14} /> {exporting ? 'Exporting...' : 'Export PDF'}
        </button>
      </div>

      {/* Progress Bar */}
      <div style={{ padding: '16px 32px 0', position: 'relative', zIndex: 1 }}>
        <div style={{ background: 'rgba(10,14,20,0.8)', borderRadius: '10px', padding: '12px 16px', border: '1px solid rgba(0,242,255,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }}>ANALYSIS COMPLETE</span>
            <span style={{ color: '#00ff9d', fontSize: '11px', fontWeight: 600 }}>4/4 Sections Loaded</span>
          </div>
          <div style={{ height: '4px', background: 'rgba(0,242,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '100%', background: 'linear-gradient(90deg, #00f2ff, #00ff9d)', borderRadius: '2px' }} />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ padding: '20px 32px 0', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '2px' }}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '12px 20px',
                borderRadius: '12px 12px 0 0',
                border: 'none',
                background: activeTab === tab.id ? 'rgba(0,242,255,0.12)' : 'rgba(255,255,255,0.03)',
                borderBottom: activeTab === tab.id ? '3px solid #00f2ff' : '3px solid transparent',
                color: activeTab === tab.id ? '#00f2ff' : '#64748b',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: activeTab === tab.id ? 700 : 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s',
                whiteSpace: 'nowrap'
              }}
            >
              <span style={{ fontSize: '16px' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div style={{ padding: '0 32px 40px', position: 'relative', zIndex: 1 }}>
        <div style={{ background: 'rgba(10,14,20,0.88)', backdropFilter: 'blur(24px)', border: '1px solid rgba(0,242,255,0.1)', borderRadius: '0 18px 18px 18px', padding: '32px', minHeight: '500px' }}>
          {activeTab === 'overview' && <OverviewTab result={result} onNavigate={setActiveTab} />}
          {activeTab === 'solubility' && <SolubilityTab data={result.solubility} />}
          {activeTab === 'formulation' && <FormulationTab data={result.excipients} />}
          {activeTab === 'stability' && <StabilityTab data={result.stability} />}
          {activeTab === 'pkpd' && <PKPDTab data={result.pk_compatibility} bioavailabilityCurve={result.bioavailability_curve} />}

          {/* Navigation Buttons */}
          <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '24px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <button
              onClick={goToPrev}
              disabled={!canGoPrev}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '10px 18px', borderRadius: '10px',
                background: canGoPrev ? 'rgba(0,242,255,0.08)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${canGoPrev ? 'rgba(0,242,255,0.2)' : 'rgba(255,255,255,0.05)'}`,
                color: canGoPrev ? '#00f2ff' : '#334155',
                cursor: canGoPrev ? 'pointer' : 'not-allowed',
                fontSize: '13px', fontWeight: 600
              }}
            >
              <ChevronLeft size={16} />
              {canGoPrev ? TABS[currentTabIndex - 1].label : 'Previous'}
            </button>

            <span style={{ color: '#475569', fontSize: '12px' }}>
              {currentTabIndex + 1} of {TABS.length}
            </span>

            <button
              onClick={goToNext}
              disabled={!canGoNext}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '10px 18px', borderRadius: '10px',
                background: canGoNext ? 'rgba(0,242,255,0.08)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${canGoNext ? 'rgba(0,242,255,0.2)' : 'rgba(255,255,255,0.05)'}`,
                color: canGoNext ? '#00f2ff' : '#334155',
                cursor: canGoNext ? 'pointer' : 'not-allowed',
                fontSize: '13px', fontWeight: 600
              }}
            >
              {canGoNext ? TABS[currentTabIndex + 1].label : 'Next'}
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
      `}</style>
    </div>
  );
};

export default AnalysisPageHybrid;
