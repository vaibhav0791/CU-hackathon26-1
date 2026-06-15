import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Lightbulb, TrendingUp, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SCENARIOS = [
  { id: 'increase_dose', label: 'Increase Dose', description: 'What if we increase the dosage?', icon: '💊' },
  { id: 'storage_temperature', label: 'Storage Temperature', description: 'What if stored at different temperature?', icon: '🌡️' },
  { id: 'formulation_change', label: 'Change Formulation', description: 'What if we change the pill form?', icon: '📦' }
];

const WhatIfPage = () => {
  const navigate = useNavigate();
  const [smiles, setSmiles] = useState('');
  const [drugName, setDrugName] = useState('');
  const [scenarioType, setScenarioType] = useState('increase_dose');
  const [parameters, setParameters] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!smiles) {
      setError('SMILES string is required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/what-if`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          smiles,
          scenario_type: scenarioType,
          parameters: { ...parameters, drug_name: drugName || 'Test Drug' }
        })
      });

      if (!res.ok) throw new Error('Analysis failed');
      
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
            <Lightbulb size={18} color="#f59e0b" />
            <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>
              What-If Scenario Analysis
            </span>
          </div>
        </div>
      </div>

      <div style={{ padding: '40px 32px', position: 'relative', zIndex: 1, maxWidth: '1000px', margin: '0 auto' }}>
        {!result ? (
          <div>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <h1 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '32px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
                Explore "What-If" Scenarios
              </h1>
              <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                Test different scenarios to see how changes affect drug properties
              </p>
            </div>

            <form onSubmit={handleAnalyze}>
              <div style={{ background: 'rgba(10,14,20,0.88)', backdropFilter: 'blur(24px)', border: '1px solid rgba(0,242,255,0.1)', borderRadius: '18px', padding: '32px' }}>
                {/* Drug Input */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Drug Name (Optional)</label>
                  <input
                    type="text"
                    value={drugName}
                    onChange={e => setDrugName(e.target.value)}
                    placeholder="e.g., Aspirin"
                    style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                  />
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>SMILES String *</label>
                  <textarea
                    value={smiles}
                    onChange={e => setSmiles(e.target.value)}
                    placeholder="CC(=O)Oc1ccccc1C(=O)O"
                    rows={3}
                    style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '12px', outline: 'none', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'JetBrains Mono, monospace' }}
                  />
                </div>

                {/* Scenario Selection */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '12px' }}>Select Scenario</label>
                  <div style={{ display: 'grid', gap: '12px' }}>
                    {SCENARIOS.map(scenario => (
                      <button
                        key={scenario.id}
                        type="button"
                        onClick={() => setScenarioType(scenario.id)}
                        style={{
                          padding: '16px',
                          background: scenarioType === scenario.id ? 'rgba(245,158,11,0.15)' : 'rgba(0,0,0,0.3)',
                          border: scenarioType === scenario.id ? '1px solid rgba(245,158,11,0.4)' : '1px solid rgba(255,255,255,0.05)',
                          borderRadius: '10px',
                          color: scenarioType === scenario.id ? '#f59e0b' : '#94a3b8',
                          cursor: 'pointer',
                          textAlign: 'left',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px'
                        }}
                      >
                        <span style={{ fontSize: '24px' }}>{scenario.icon}</span>
                        <div>
                          <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>{scenario.label}</div>
                          <div style={{ fontSize: '12px', opacity: 0.8 }}>{scenario.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Scenario Parameters */}
                <div style={{ marginBottom: '24px' }}>
                  {scenarioType === 'increase_dose' && (
                    <div>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>New Dose (mg)</label>
                      <input
                        type="number"
                        value={parameters.new_dose || ''}
                        onChange={e => setParameters({ ...parameters, new_dose: parseInt(e.target.value) })}
                        placeholder="500"
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                      />
                    </div>
                  )}
                  {scenarioType === 'storage_temperature' && (
                    <div>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Storage Temperature</label>
                      <select
                        value={parameters.temperature || '30C'}
                        onChange={e => setParameters({ ...parameters, temperature: e.target.value })}
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                      >
                        <option value="30C">30°C (86°F)</option>
                        <option value="40C">40°C (104°F)</option>
                        <option value="50C">50°C (122°F)</option>
                      </select>
                    </div>
                  )}
                  {scenarioType === 'formulation_change' && (
                    <div>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>New Formulation</label>
                      <select
                        value={parameters.new_formulation || 'Capsule'}
                        onChange={e => setParameters({ ...parameters, new_formulation: e.target.value })}
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                      >
                        <option value="Capsule">Capsule</option>
                        <option value="Oral Solution">Oral Solution</option>
                        <option value="Extended-Release Tablet">Extended-Release Tablet</option>
                        <option value="Chewable Tablet">Chewable Tablet</option>
                      </select>
                    </div>
                  )}
                </div>

                {error && (
                  <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '10px', padding: '12px', marginBottom: '20px', color: '#fca5a5', fontSize: '13px' }}>
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '14px',
                    background: loading ? 'rgba(245,158,11,0.1)' : 'linear-gradient(135deg, #f59e0b, #ef4444)',
                    border: 'none',
                    borderRadius: '12px',
                    color: loading ? '#64748b' : 'white',
                    fontWeight: 700,
                    fontSize: '14px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}
                >
                  <Lightbulb size={16} />
                  {loading ? 'Analyzing... This may take 30-60 seconds' : 'Run What-If Analysis'}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h1 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
                Scenario Analysis Results
              </h1>
              <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                {result.scenario_analysis.scenario_description}
              </p>
              <button
                onClick={() => setResult(null)}
                style={{
                  marginTop: '16px',
                  padding: '8px 16px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#94a3b8',
                  fontSize: '12px',
                  cursor: 'pointer'
                }}
              >
                New Scenario
              </button>
            </div>

            {/* Results Comparison */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div style={{ background: 'rgba(10,14,20,0.88)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '14px', padding: '24px' }}>
                <h3 style={{ color: '#00f2ff', fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Base Analysis</h3>
                <div style={{ display: 'grid', gap: '12px' }}>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>SOLUBILITY</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.base_analysis.solubility?.prediction}/100</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>BIOAVAILABILITY</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.base_analysis.pk_compatibility?.bioavailability_percent}%</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>SHELF LIFE</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.base_analysis.stability?.shelf_life_years} years</div>
                  </div>
                </div>
              </div>

              <div style={{ background: 'rgba(10,14,20,0.88)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '14px', padding: '24px' }}>
                <h3 style={{ color: '#f59e0b', fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Scenario Result</h3>
                <div style={{ display: 'grid', gap: '12px' }}>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>SOLUBILITY</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.scenario_analysis.solubility?.prediction}/100</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>BIOAVAILABILITY</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.scenario_analysis.pk_compatibility?.bioavailability_percent}%</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>SHELF LIFE</div>
                    <div style={{ color: '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{result.scenario_analysis.stability?.shelf_life_years} years</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Impact Summary */}
            {result.scenario_analysis.stability?.predicted_impact && (
              <div style={{ marginTop: '24px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '14px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                  <AlertTriangle size={18} color="#f59e0b" />
                  <h3 style={{ color: '#f59e0b', fontSize: '14px', fontWeight: 700, margin: 0 }}>Predicted Impact</h3>
                </div>
                <p style={{ color: '#fbbf24', fontSize: '13px', lineHeight: 1.6, margin: 0 }}>
                  {result.scenario_analysis.stability.predicted_impact}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatIfPage;
