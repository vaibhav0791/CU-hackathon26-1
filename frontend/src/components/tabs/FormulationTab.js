import React, { useState } from 'react';
import { Package, ChevronDown, ChevronUp, Info, CheckCircle2, AlertTriangle } from 'lucide-react';

const FormulationTab = ({ data }) => {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!data) {
    return <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>No formulation data available</div>;
  }

  return (
    <div>
      {/* Bottom Line */}
      <div style={{ background: 'linear-gradient(135deg, rgba(112,0,255,0.1), transparent)', border: '1px solid rgba(112,0,255,0.3)', borderLeft: '4px solid #7000ff', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Package size={24} color="#7000ff" />
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '20px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            🎯 BOTTOM LINE
          </h2>
        </div>
        <p style={{ color: '#e2e8f0', fontSize: '16px', lineHeight: 1.6, margin: 0 }}>
          Best formulated as a <strong style={{ color: '#7000ff' }}>{data.optimal_dosage_form}</strong>
          {data.coating?.recommended && <span> with <strong style={{ color: '#7000ff' }}>{data.coating.type}</strong> coating</span>}
        </p>
      </div>

      {/* What This Means */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} color="#7000ff" />
          📖 WHAT THIS MEANS FOR HEALTHCARE WORKERS
        </h3>
        <div style={{ background: 'rgba(112,0,255,0.05)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(112,0,255,0.15)' }}>
          <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: '0 0 12px 0' }}>
            A drug is not just the active ingredient. It needs other materials (excipients) to:
          </p>
          <ul style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: 0, paddingLeft: '20px' }}>
            <li>Form a stable pill or capsule</li>
            <li>Help it dissolve at the right time</li>
            <li>Make it easy to swallow</li>
            <li>Protect it from breaking down</li>
          </ul>
        </div>
      </div>

      {/* Key Ingredients */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#7000ff" />
          💊 KEY INGREDIENTS (Excipients)
        </h3>
        <div style={{ display: 'grid', gap: '16px' }}>
          {['binders', 'fillers', 'disintegrants', 'lubricants'].map(category => {
            if (!data[category]?.length) return null;
            const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
            const categoryDesc = {
              binders: 'Hold the pill together',
              fillers: 'Add bulk to the pill',
              disintegrants: 'Help pill break apart in stomach',
              lubricants: 'Prevent sticking during manufacturing'
            };
            
            return (
              <div key={category} style={{ background: 'rgba(112,0,255,0.08)', border: '1px solid rgba(112,0,255,0.2)', borderRadius: '10px', padding: '16px' }}>
                <div style={{ color: '#a78bfa', fontSize: '13px', fontWeight: 700, marginBottom: '8px' }}>
                  {categoryName} - {categoryDesc[category]}
                </div>
                {data[category].slice(0, 2).map((item, i) => (
                  <div key={i} style={{ marginBottom: '10px', paddingLeft: '12px', borderLeft: '2px solid rgba(112,0,255,0.3)' }}>
                    <div style={{ color: '#e2e8f0', fontSize: '13px', fontWeight: 600 }}>{item.name}</div>
                    <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '2px' }}>Amount: {item.recommended_conc}</div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginTop: '4px', fontStyle: 'italic' }}>Why: {item.rationale}</div>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      </div>

      {/* Patient Instructions */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#00ff9d" />
          💊 PATIENT INSTRUCTIONS
        </h3>
        <div style={{ display: 'grid', gap: '12px' }}>
          <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <CheckCircle2 size={16} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>How to Take</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                {data.optimal_dosage_form === 'Tablet' && '"Swallow whole with water - do not crush or chew"'}
                {data.optimal_dosage_form === 'Capsule' && '"Swallow whole with water - do not open capsule"'}
                {data.optimal_dosage_form === 'Oral Solution' && '"Measure dose carefully with provided measuring device"'}
              </div>
            </div>
          </div>
          {data.coating?.recommended && (
            <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
              <CheckCircle2 size={16} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Special Coating</div>
                <div style={{ color: '#cbd5e1', fontSize: '13px' }}>This pill has a {data.coating.type} coating - do not break or crush it</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Warnings */}
      {data.incompatibilities?.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={18} color="#ef4444" />
            ⚠️ IMPORTANT WARNINGS
          </h3>
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '10px', padding: '20px' }}>
            <div style={{ color: '#fca5a5', fontSize: '13px', fontWeight: 600, marginBottom: '10px' }}>
              Avoid these combinations:
            </div>
            <ul style={{ color: '#fca5a5', fontSize: '13px', lineHeight: 1.7, margin: 0, paddingLeft: '20px' }}>
              {data.incompatibilities.map((inc, i) => <li key={i}>{inc}</li>)}
            </ul>
          </div>
        </div>
      )}

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

      {/* Technical Details */}
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
            {['binders', 'fillers', 'disintegrants', 'lubricants'].map(category => {
              if (!data[category]?.length) return null;
              return (
                <div key={category} style={{ marginBottom: '16px' }}>
                  <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, marginBottom: '8px', textTransform: 'uppercase' }}>
                    {category}:
                  </div>
                  {data[category].map((item, i) => (
                    <div key={i} style={{ color: '#cbd5e1', fontSize: '12px', marginBottom: '6px', paddingLeft: '12px' }}>
                      • {item.name} ({item.grade || 'USP'}) - {item.recommended_conc}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default FormulationTab;
