import React from 'react';
import { Activity, Droplets, Package, Shield, TrendingUp } from 'lucide-react';
import MoleculeViewer from '../MoleculeViewer';

const OverviewTab = ({ result, onNavigate }) => {
  const summaryCards = [
    {
      id: 'solubility',
      icon: Droplets,
      color: '#00f2ff',
      title: 'Solubility',
      value: result.solubility ? `${parseFloat(result.solubility.prediction).toFixed(0)}/100` : 'N/A',
      status: result.solubility ? result.solubility.classification : 'N/A',
      description: 'How well it dissolves'
    },
    {
      id: 'formulation',
      icon: Package,
      color: '#7000ff',
      title: 'Formulation',
      value: result.excipients?.optimal_dosage_form || 'N/A',
      status: result.excipients ? 'Optimized' : 'N/A',
      description: 'Best pill form'
    },
    {
      id: 'stability',
      icon: Shield,
      color: '#00ff9d',
      title: 'Stability',
      value: result.stability ? `${result.stability.shelf_life_years} years` : 'N/A',
      status: result.stability ? 'Stable' : 'N/A',
      description: 'How long it lasts'
    },
    {
      id: 'pkpd',
      icon: TrendingUp,
      color: '#f59e0b',
      title: 'Bioavailability',
      value: result.pk_compatibility ? `${result.pk_compatibility.bioavailability_percent}%` : 'N/A',
      status: result.pk_compatibility?.absorption_rate || 'N/A',
      description: 'How well body absorbs it'
    }
  ];

  return (
    <div>
      {/* Quick Summary */}
      <div style={{ background: 'linear-gradient(135deg, rgba(0,242,255,0.08), rgba(112,0,255,0.08))', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '14px', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Activity size={20} color="#00f2ff" />
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '18px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>🎯 QUICK SUMMARY</h2>
        </div>
        <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.7, margin: 0 }}>
          This drug has <strong style={{ color: '#00f2ff' }}>{result.solubility?.classification || 'moderate'} solubility</strong>, 
          is <strong style={{ color: '#00ff9d' }}>stable for {result.stability?.shelf_life_years || '2-3'} years</strong>, 
          and has <strong style={{ color: '#f59e0b' }}>{result.pk_compatibility?.bioavailability_percent || '70-80'}% bioavailability</strong> - 
          meaning it works well in the body. Best taken as a <strong style={{ color: '#7000ff' }}>{result.excipients?.optimal_dosage_form || 'tablet'}</strong>.
        </p>
      </div>

      {/* 3D Molecule Viewer */}
      <div style={{ marginBottom: '32px' }}>
        <MoleculeViewer smiles={result.smiles} />
      </div>

      {/* Summary Cards */}
      <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '14px', fontWeight: 600, color: '#94a3b8', marginBottom: '16px', letterSpacing: '1px', textTransform: 'uppercase' }}>
        Click a card to view details
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {summaryCards.map(card => {
          const Icon = card.icon;
          return (
            <button
              key={card.id}
              onClick={() => onNavigate(card.id)}
              style={{
                background: 'rgba(0,0,0,0.3)',
                border: `1px solid ${card.color}20`,
                borderRadius: '14px',
                padding: '20px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = `${card.color}10`;
                e.currentTarget.style.borderColor = `${card.color}40`;
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'rgba(0,0,0,0.3)';
                e.currentTarget.style.borderColor = `${card.color}20`;
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `${card.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={18} color={card.color} />
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', fontFamily: 'JetBrains Mono, monospace' }}>{card.title.toUpperCase()}</div>
                  <div style={{ color: card.color, fontSize: '18px', fontWeight: 700, fontFamily: 'Manrope, sans-serif', marginTop: '2px' }}>{card.value}</div>
                </div>
              </div>
              <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '6px' }}>{card.status}</div>
              <div style={{ color: '#475569', fontSize: '11px' }}>{card.description}</div>
            </button>
          );
        })}
      </div>

      {/* Key Molecular Info */}
      <div style={{ marginTop: '32px', background: 'rgba(0,0,0,0.3)', borderRadius: '14px', padding: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: '16px' }}>
          Molecular Information
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          <div>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>MOLECULAR WEIGHT</div>
            <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{result.molecular_weight} g/mol</div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>BCS CLASS</div>
            <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{result.drug_info?.bcs_class || 'N/A'}</div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>LogP</div>
            <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{result.drug_info?.logp || 'N/A'}</div>
          </div>
          <div>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>DOSE</div>
            <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{result.dose_mg} mg</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;
