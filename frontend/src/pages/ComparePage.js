import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, GitCompare, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ComparePage = () => {
  const navigate = useNavigate();
  const [drug1Smiles, setDrug1Smiles] = useState('');
  const [drug2Smiles, setDrug2Smiles] = useState('');
  const [drug1Name, setDrug1Name] = useState('');
  const [drug2Name, setDrug2Name] = useState('');
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState(null);
  const [error, setError] = useState('');

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!drug1Smiles || !drug2Smiles) {
      setError('Both SMILES strings are required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          drug1_smiles: drug1Smiles,
          drug2_smiles: drug2Smiles,
          drug1_name: drug1Name || 'Drug A',
          drug2_name: drug2Name || 'Drug B'
        })
      });

      if (!res.ok) throw new Error('Comparison failed');
      
      const data = await res.json();
      setComparison(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ComparisonMetric = ({ label, value1, value2, unit = '', higherIsBetter = true }) => {
    const val1 = parseFloat(value1) || 0;
    const val2 = parseFloat(value2) || 0;
    const winner = higherIsBetter ? (val1 > val2 ? 1 : val1 < val2 ? 2 : 0) : (val1 < val2 ? 1 : val1 > val2 ? 2 : 0);

    return (
      <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '12px', padding: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', letterSpacing: '1px', marginBottom: '12px', textAlign: 'center' }}>{label}</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '12px', alignItems: 'center' }}>
          <div style={{ textAlign: 'center', padding: '12px', borderRadius: '8px', background: winner === 1 ? 'rgba(0,255,157,0.1)' : 'rgba(0,0,0,0.2)', border: winner === 1 ? '1px solid rgba(0,255,157,0.3)' : '1px solid transparent' }}>
            <div style={{ color: winner === 1 ? '#00ff9d' : '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{val1.toFixed(1)}{unit}</div>
            {winner === 1 && <TrendingUp size={14} color="#00ff9d" style={{ marginTop: '4px' }} />}
          </div>
          <div style={{ color: '#475569', fontSize: '12px' }}>vs</div>
          <div style={{ textAlign: 'center', padding: '12px', borderRadius: '8px', background: winner === 2 ? 'rgba(0,255,157,0.1)' : 'rgba(0,0,0,0.2)', border: winner === 2 ? '1px solid rgba(0,255,157,0.3)' : '1px solid transparent' }}>
            <div style={{ color: winner === 2 ? '#00ff9d' : '#e2e8f0', fontSize: '18px', fontWeight: 700 }}>{val2.toFixed(1)}{unit}</div>
            {winner === 2 && <TrendingUp size={14} color="#00ff9d" style={{ marginTop: '4px' }} />}
          </div>
        </div>
      </div>
    );
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
            <GitCompare size={18} color="#00f2ff" />
            <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>
              Compare Drugs
            </span>
          </div>
        </div>
      </div>

      <div style={{ padding: '40px 32px', position: 'relative', zIndex: 1, maxWidth: '1400px', margin: '0 auto' }}>

        {!comparison ? (
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <h1 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '32px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
                Compare Two Drugs Side-by-Side
              </h1>
              <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                Enter SMILES strings for two drugs to compare their properties, efficacy, and safety profiles
              </p>
            </div>

            <form onSubmit={handleCompare}>
              <div style={{ background: 'rgba(10,14,20,0.88)', backdropFilter: 'blur(24px)', border: '1px solid rgba(0,242,255,0.1)', borderRadius: '18px', padding: '32px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                  {/* Drug 1 */}
                  <div>
                    <h3 style={{ color: '#00f2ff', fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Drug A</h3>
                    <div style={{ marginBottom: '16px' }}>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Drug Name (Optional)</label>
                      <input
                        type="text"
                        value={drug1Name}
                        onChange={e => setDrug1Name(e.target.value)}
                        placeholder="e.g., Aspirin"
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>SMILES String *</label>
                      <textarea
                        value={drug1Smiles}
                        onChange={e => setDrug1Smiles(e.target.value)}
                        placeholder="CC(=O)Oc1ccccc1C(=O)O"
                        rows={3}
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '12px', outline: 'none', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'JetBrains Mono, monospace' }}
                      />
                    </div>
                  </div>

                  {/* Drug 2 */}
                  <div>
                    <h3 style={{ color: '#7000ff', fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>Drug B</h3>
                    <div style={{ marginBottom: '16px' }}>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Drug Name (Optional)</label>
                      <input
                        type="text"
                        value={drug2Name}
                        onChange={e => setDrug2Name(e.target.value)}
                        placeholder="e.g., Ibuprofen"
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(112,0,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>SMILES String *</label>
                      <textarea
                        value={drug2Smiles}
                        onChange={e => setDrug2Smiles(e.target.value)}
                        placeholder="CC(C)Cc1ccc(cc1)C(C)C(=O)O"
                        rows={3}
                        style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(112,0,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '12px', outline: 'none', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'JetBrains Mono, monospace' }}
                      />
                    </div>
                  </div>
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
                    background: loading ? 'rgba(0,242,255,0.1)' : 'linear-gradient(135deg, #00f2ff, #7000ff)',
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
                  <GitCompare size={16} />
                  {loading ? 'Comparing... This may take 30-60 seconds' : 'Compare Drugs'}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h1 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
                Comparison Results
              </h1>
              <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                {comparison.drug1.drug_name} vs {comparison.drug2.drug_name}
              </p>
              <button
                onClick={() => setComparison(null)}
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
                New Comparison
              </button>
            </div>

            {/* Comparison Grid */}
            <div style={{ display: 'grid', gap: '16px', marginBottom: '32px' }}>
              <ComparisonMetric
                label="SOLUBILITY SCORE"
                value1={comparison.drug1.solubility?.prediction}
                value2={comparison.drug2.solubility?.prediction}
                unit="/100"
                higherIsBetter={true}
              />
              <ComparisonMetric
                label="BIOAVAILABILITY"
                value1={comparison.drug1.pk_compatibility?.bioavailability_percent}
                value2={comparison.drug2.pk_compatibility?.bioavailability_percent}
                unit="%"
                higherIsBetter={true}
              />
              <ComparisonMetric
                label="SHELF LIFE"
                value1={comparison.drug1.stability?.shelf_life_years}
                value2={comparison.drug2.stability?.shelf_life_years}
                unit=" years"
                higherIsBetter={true}
              />
              <ComparisonMetric
                label="HALF-LIFE"
                value1={comparison.drug1.pk_compatibility?.t_half_hours}
                value2={comparison.drug2.pk_compatibility?.t_half_hours}
                unit=" hours"
                higherIsBetter={false}
              />
            </div>

            {/* Summary */}
            <div style={{ background: 'linear-gradient(135deg, rgba(0,255,157,0.1), transparent)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: '14px', padding: '24px' }}>
              <h3 style={{ color: '#00ff9d', fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Summary</h3>
              <ul style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.8, margin: 0, paddingLeft: '20px' }}>
                <li><strong>{comparison.comparison_summary.solubility_winner}</strong> has better solubility</li>
                <li><strong>{comparison.comparison_summary.bioavailability_winner}</strong> has higher bioavailability</li>
                <li><strong>{comparison.comparison_summary.stability_winner}</strong> is more stable</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparePage;
