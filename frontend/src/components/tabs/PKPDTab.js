import React, { useState } from 'react';
import { TrendingUp, ChevronDown, ChevronUp, Info, CheckCircle2, Clock, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PKPDTab = ({ data, bioavailabilityCurve }) => {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!data) {
    return <div style={{ color: '#94a3b8', textAlign: 'center', padding: '40px' }}>No PK/PD data available</div>;
  }

  const curveData = (bioavailabilityCurve || data.bioavailability_curve || []).map(pt => ({
    time: parseFloat(pt.time) || 0,
    concentration: parseFloat(pt.concentration) || 0
  }));

  return (
    <div>
      {/* Bottom Line */}
      <div style={{ background: 'linear-gradient(135deg, rgba(245,158,11,0.1), transparent)', border: '1px solid rgba(245,158,11,0.3)', borderLeft: '4px solid #f59e0b', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <TrendingUp size={24} color="#f59e0b" />
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '20px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            🎯 BOTTOM LINE
          </h2>
        </div>
        <p style={{ color: '#e2e8f0', fontSize: '16px', lineHeight: 1.6, margin: 0 }}>
          <strong style={{ color: '#f59e0b' }}>{data.bioavailability_percent}%</strong> of the drug reaches the bloodstream.
          This is <strong>{data.bioavailability_percent >= 80 ? 'EXCELLENT' : data.bioavailability_percent >= 60 ? 'GOOD' : 'MODERATE'}</strong> absorption.
        </p>
      </div>

      {/* What This Means */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} color="#f59e0b" />
          📖 WHAT THIS MEANS FOR HEALTHCARE WORKERS
        </h3>
        <div style={{ background: 'rgba(245,158,11,0.05)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(245,158,11,0.15)' }}>
          <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: '0 0 12px 0' }}>
            Pharmacokinetics (PK) describes what your body does to the drug:
          </p>
          <ul style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: 0, paddingLeft: '20px' }}>
            <li><strong>Absorption:</strong> How it enters the bloodstream</li>
            <li><strong>Distribution:</strong> Where it goes in the body</li>
            <li><strong>Metabolism:</strong> How the liver processes it</li>
            <li><strong>Elimination:</strong> How it leaves the body</li>
          </ul>
        </div>
      </div>

      {/* Timeline */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={18} color="#f59e0b" />
          ⏱️ WHAT HAPPENS AFTER PATIENT TAKES IT
        </h3>
        <div style={{ display: 'grid', gap: '12px' }}>
          <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <div style={{ color: '#f59e0b', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>1</div>
            <div>
              <div style={{ color: '#f59e0b', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Absorption</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                The drug enters bloodstream through {data.absorption_mechanism || 'intestinal absorption'}. 
                Rate: {data.absorption_rate}
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <div style={{ color: '#f59e0b', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>2</div>
            <div>
              <div style={{ color: '#f59e0b', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Peak Effect</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                Maximum concentration reached in <strong>{data.tmax_hours} hours</strong>
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <div style={{ color: '#f59e0b', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>3</div>
            <div>
              <div style={{ color: '#f59e0b', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Duration</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                Half of the drug is eliminated every <strong>{data.t_half_hours} hours</strong>
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <div style={{ color: '#f59e0b', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>4</div>
            <div>
              <div style={{ color: '#f59e0b', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Metabolism</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                Processed by {data.metabolism?.primary_enzyme || 'liver enzymes'}
              </div>
            </div>
          </div>
          <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '16px', display: 'flex', gap: '12px' }}>
            <div style={{ color: '#f59e0b', fontSize: '20px', fontWeight: 700, flexShrink: 0 }}>5</div>
            <div>
              <div style={{ color: '#f59e0b', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Elimination</div>
              <div style={{ color: '#cbd5e1', fontSize: '13px' }}>
                Removed via {data.excretion?.route || 'kidneys'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Concentration-Time Curve */}
      {curveData.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} color="#f59e0b" />
            📊 DRUG CONCENTRATION OVER TIME
          </h3>
          <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(245,158,11,0.2)' }}>
            <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '12px' }}>
              This graph shows how much drug is in the bloodstream over time
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={curveData} margin={{ top: 5, right: 10, left: -22, bottom: 5 }}>
                <defs>
                  <linearGradient id="pkGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="time" tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Time (hours)', position: 'insideBottomRight', fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Concentration', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#f59e0b' }} />
                <Area type="monotone" dataKey="concentration" name="Drug Level" stroke="#f59e0b" strokeWidth={2.5} fill="url(#pkGrad)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Dosing Recommendation */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#00ff9d" />
          💊 DOSING RECOMMENDATION
        </h3>
        <div style={{ background: 'rgba(0,255,157,0.08)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '10px', padding: '20px' }}>
          <div style={{ color: '#00ff9d', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
            {data.recommended_dosage_form}
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '13px', marginBottom: '12px' }}>
            Frequency: <strong>{data.dosing_frequency}</strong>
          </div>
          <div style={{ color: '#94a3b8', fontSize: '12px', fontStyle: 'italic' }}>
            Based on {data.t_half_hours}-hour half-life and {data.bioavailability_percent}% bioavailability
          </div>
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
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '16px' }}>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>BIOAVAILABILITY</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.bioavailability_percent}%</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>Tmax</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.tmax_hours} hours</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>T½ (HALF-LIFE)</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.t_half_hours} hours</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>PROTEIN BINDING</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.protein_binding_percent}%</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '6px' }}>Vd</div>
                <div style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 600 }}>{data.distribution_vd} L/kg</div>
              </div>
            </div>
            {data.metabolism?.metabolites?.length > 0 && (
              <div>
                <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, marginBottom: '8px' }}>Major Metabolites:</div>
                <ul style={{ color: '#cbd5e1', fontSize: '12px', lineHeight: 1.6, margin: 0, paddingLeft: '20px' }}>
                  {data.metabolism.metabolites.map((m, i) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PKPDTab;
