import React, { useState } from 'react';
import { Droplets, ChevronDown, ChevronUp, AlertCircle, CheckCircle2, Info } from 'lucide-react';

const SolubilityTab = ({ data }) => {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!data) {
    return <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>No solubility data available</div>;
  }

  const score = parseFloat(data.prediction) || 0;
  const getScoreColor = (score) => {
    if (score >= 70) return '#00ff9d';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div>
      {/* Bottom Line */}
      <div style={{ background: 'linear-gradient(135deg, rgba(0,242,255,0.1), transparent)', border: '1px solid rgba(0,242,255,0.3)', borderLeft: '4px solid #00f2ff', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Droplets size={24} color="#00f2ff" />
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '20px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            🎯 BOTTOM LINE
          </h2>
        </div>
        <p style={{ color: '#e2e8f0', fontSize: '16px', lineHeight: 1.6, margin: 0 }}>
          This drug dissolves <strong style={{ color: getScoreColor(score) }}>{data.classification}</strong> in body fluids
        </p>
        <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ flex: 1, height: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${score}%`, background: getScoreColor(score), borderRadius: '6px', transition: 'width 0.5s' }} />
          </div>
          <span style={{ color: getScoreColor(score), fontSize: '20px', fontWeight: 700, fontFamily: 'Manrope, sans-serif' }}>{score.toFixed(0)}/100</span>
        </div>
      </div>

      {/* What This Means */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} color="#00f2ff" />
          📖 WHAT THIS MEANS FOR HEALTHCARE WORKERS
        </h3>
        <div style={{ background: 'rgba(0,242,255,0.05)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(0,242,255,0.15)' }}>
          <ul style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: 0, paddingLeft: '20px' }}>
            <li>The drug dissolves {score >= 70 ? 'quickly' : score >= 40 ? 'moderately' : 'slowly'} in stomach fluids</li>
            <li>Patients will absorb it {score >= 70 ? 'easily and efficiently' : score >= 40 ? 'adequately with proper administration' : 'with some difficulty - may need special formulation'}</li>
            <li>It starts working within {score >= 70 ? '30-60 minutes' : score >= 40 ? '60-90 minutes' : '90-120 minutes or longer'}</li>
            <li>Similar dissolution profile to common drugs like {score >= 70 ? 'aspirin or ibuprofen' : score >= 40 ? 'acetaminophen' : 'extended-release formulations'}</li>
          </ul>
        </div>
      </div>

      {/* Patient Counseling Points */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#00ff9d" />
          💊 PATIENT COUNSELING POINTS
        </h3>
        <div style={{ display: 'grid', gap: '12px' }}>
          <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <CheckCircle2 size={16} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Water Intake</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>"Take with a full glass of water (8 oz / 240 mL)"</div>
            </div>
          </div>
          <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <CheckCircle2 size={16} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Food Interaction</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>{data.aqueous_solubility_mg_ml > 1 ? '"Can be taken with or without food"' : '"Take on an empty stomach for best absorption"'}</div>
            </div>
          </div>
          <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <CheckCircle2 size={16} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Onset of Action</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>"You should feel effects within {score >= 70 ? '30-60' : score >= 40 ? '60-90' : '90-120'} minutes"</div>
            </div>
          </div>
        </div>
      </div>

      {/* Clinical Considerations */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={18} color="#f59e0b" />
          ⚠️ CLINICAL CONSIDERATIONS
        </h3>
        <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '20px' }}>
          <ul style={{ color: '#fbbf24', fontSize: '13px', lineHeight: 1.7, margin: 0, paddingLeft: '20px' }}>
            <li>Patients with swallowing difficulties: {score >= 60 ? 'Should be able to use this formulation' : 'May need liquid or dispersible formulation'}</li>
            <li>Elderly patients: {score >= 60 ? 'No special considerations' : 'Monitor for delayed onset of action'}</li>
            <li>Pediatric use: {score >= 60 ? 'Age-appropriate dosing applies' : 'Consider liquid formulation for better compliance'}</li>
            {Array.isArray(data.enhancement_strategies) && data.enhancement_strategies.length > 0 && (
              <li>Enhancement options available: {data.enhancement_strategies.slice(0, 2).join(', ')}</li>
            )}
          </ul>
        </div>
      </div>

      {/* Plain English Summary */}
      {data.natural_language_summary && (
        <div style={{ background: 'linear-gradient(135deg, rgba(254,249,195,0.15), transparent)', border: '1px solid rgba(254,249,195,0.3)', borderRadius: '12px', padding: '20px', marginBottom: '32px' }}>
          <div style={{ color: '#fef3c7', fontSize: '11px', letterSpacing: '1.5px', fontFamily: 'JetBrains Mono, monospace', marginBottom: '10px' }}>
            💡 PLAIN ENGLISH SUMMARY
          </div>
          <p style={{ color: '#fef3c7', fontSize: '14px', lineHeight: 1.7, margin: 0, fontStyle: 'italic' }}>
            {data.natural_language_summary}
          </p>
        </div>
      )}

      {/* Technical Details (Collapsible) */}
      <div style={{ border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', overflow: 'hidden' }}>
        <button
          onClick={() => setShowTechnical(!showTechnical)}
          style={{
            width: '100%',
            background: 'rgba(0,0,0,0.3)',
            border: 'none',
            padding: '16px 20px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            color: '#94a3b8',
            fontSize: '14px',
            fontWeight: 600
          }}
        >
          <span>🔬 TECHNICAL DETAILS (For Pharmacists & Scientists)</span>
          {showTechnical ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
        {showTechnical && (
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '20px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>AQUEOUS SOLUBILITY</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.aqueous_solubility_mg_ml} mg/mL</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>OPTIMAL pH</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.ph_optimal}</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>PREDICTION ACCURACY</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.accuracy}%</div>
              </div>
            </div>
            {data.mechanisms?.length > 0 && (
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, marginBottom: '10px' }}>Dissolution Mechanisms:</div>
                <ul style={{ color: '#cbd5e1', fontSize: '12px', lineHeight: 1.6, margin: 0, paddingLeft: '20px' }}>
                  {data.mechanisms.map((m, i) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SolubilityTab;
