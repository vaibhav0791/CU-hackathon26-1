import React, { useState } from 'react';
import { Shield, ChevronDown, ChevronUp, Info, CheckCircle2, Thermometer, Droplets, Sun } from 'lucide-react';

const StabilityTab = ({ data }) => {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!data) {
    return <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>No stability data available</div>;
  }

  return (
    <div>
      {/* Bottom Line */}
      <div style={{ background: 'linear-gradient(135deg, rgba(0,255,157,0.1), transparent)', border: '1px solid rgba(0,255,157,0.3)', borderLeft: '4px solid #00ff9d', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Shield size={24} color="#00ff9d" />
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '20px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            🎯 BOTTOM LINE
          </h2>
        </div>
        <p style={{ color: '#e2e8f0', fontSize: '16px', lineHeight: 1.6, margin: 0 }}>
          This drug stays effective for <strong style={{ color: '#00ff9d' }}>{data.shelf_life_years} YEARS</strong> when stored properly.
          It's stable and safe for long-term use.
        </p>
      </div>

      {/* What This Means */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} color="#00ff9d" />
          📖 WHAT THIS MEANS FOR HEALTHCARE WORKERS
        </h3>
        <div style={{ background: 'rgba(0,255,157,0.05)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(0,255,157,0.15)' }}>
          <ul style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: 0, paddingLeft: '20px' }}>
            <li>The medication won't "go bad" quickly</li>
            <li>Patients can safely use it until the expiration date</li>
            <li>No special refrigeration needed (unless specified)</li>
            <li>Similar stability to common antibiotics and pain relievers</li>
          </ul>
        </div>
      </div>

      {/* Storage Instructions */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#00ff9d" />
          💊 STORAGE INSTRUCTIONS FOR PATIENTS
        </h3>
        <div style={{ display: 'grid', gap: '12px' }}>
          {data.storage_conditions && (
            <>
              <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
                <Thermometer size={18} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Temperature</div>
                  <div style={{ color: '#cbd5e1', fontSize: '13px' }}>{data.storage_conditions.temperature}</div>
                </div>
              </div>
              <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
                <Droplets size={18} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Humidity</div>
                  <div style={{ color: '#cbd5e1', fontSize: '13px' }}>{data.storage_conditions.humidity} - Keep bottle tightly closed</div>
                </div>
              </div>
              <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
                <Sun size={18} color="#00ff9d" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <div style={{ color: '#00ff9d', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Light Protection</div>
                  <div style={{ color: '#cbd5e1', fontSize: '13px' }}>{data.storage_conditions.light}</div>
                </div>
              </div>
            </>
          )}
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '10px', padding: '16px' }}>
            <div style={{ color: '#fca5a5', fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>❌ DO NOT store in bathroom</div>
            <div style={{ color: '#fca5a5', fontSize: '12px' }}>Bathrooms are too humid and can reduce shelf life</div>
          </div>
        </div>
      </div>

      {/* Clinical Considerations */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          ⚠️ THINGS TO WATCH
        </h3>
        <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '20px' }}>
          <ul style={{ color: '#fbbf24', fontSize: '13px', lineHeight: 1.7, margin: 0, paddingLeft: '20px' }}>
            <li>Always check expiration date before dispensing</li>
            <li>If tablets change color or develop an unusual smell, do not use</li>
            <li>Counsel patients living in humid climates about proper storage</li>
            <li>Main degradation risk: {data.primary_degradation}</li>
            <li>Recommended packaging: {data.packaging_recommendation}</li>
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
            {data.degradation_mechanisms?.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, marginBottom: '8px' }}>Degradation Mechanisms:</div>
                <ul style={{ color: '#cbd5e1', fontSize: '12px', lineHeight: 1.6, margin: 0, paddingLeft: '20px' }}>
                  {data.degradation_mechanisms.map((m, i) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            )}
            {data.accelerated_data?.length > 0 && (
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, marginBottom: '8px' }}>ICH Stability Data:</div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '11px', color: '#cbd5e1', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        <th style={{ padding: '8px', textAlign: 'left' }}>Condition</th>
                        <th style={{ padding: '8px', textAlign: 'left' }}>Month</th>
                        <th style={{ padding: '8px', textAlign: 'left' }}>Potency (%)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.accelerated_data.slice(0, 6).map((row, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '8px' }}>{row.condition}</td>
                          <td style={{ padding: '8px' }}>{row.months}</td>
                          <td style={{ padding: '8px', color: parseFloat(row.potency) > 95 ? '#00ff9d' : '#f59e0b' }}>{row.potency}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StabilityTab;
