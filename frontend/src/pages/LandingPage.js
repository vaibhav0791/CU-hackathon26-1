import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DNAHelix from '../components/DNAHelix';
import { DRUG_DATABASE } from '../data/drugDatabase';
import { Dna, FlaskConical, Activity, Brain, ChevronDown, Microscope, Search, ChevronRight, Beaker } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const stats = [
  { label: 'Solubility Accuracy', value: '98.2%', color: '#00f2ff' },
  { label: 'Stability Models', value: '500+', color: '#7000ff' },
  { label: 'Drug Database', value: '30 APIs', color: '#00ff9d' },
  { label: 'PK Predictions', value: 'Real-time', color: '#f59e0b' },
];

const features = [
  { icon: FlaskConical, title: 'Solubility Prediction', desc: 'BCS-class based AI prediction with aqueous solubility scoring and enhancement strategies.', color: '#00f2ff' },
  { icon: Microscope, title: 'Excipient Engine', desc: 'Smart recommendations for binders, fillers, disintegrants, and lubricants.', color: '#7000ff' },
  { icon: Activity, title: 'Stability Forecast', desc: 'Shelf-life prediction with ICH accelerated degradation simulation.', color: '#00ff9d' },
  { icon: Brain, title: 'PK-Compatibility', desc: 'Bioavailability curves, T½, Tmax, protein binding, and metabolism analysis.', color: '#f59e0b' },
];

// Example experimental SMILES for quick demo
const EXPERIMENTAL_EXAMPLES = [
  { label: 'Example 1 — Kinase Inhibitor scaffold', smiles: 'c1ccc2c(c1)cc(=O)n2Cc1ccc(cc1)C(=O)N1CCCC1', name: 'Experimental Kinase Inhibitor' },
  { label: 'Example 2 — Anticancer candidate', smiles: 'O=C(Nc1ccc(N2CCN(c3ncnc4ccccc34)CC2)cc1)c1ccc(Cl)cc1', name: 'Experimental Anticancer Drug X' },
  { label: 'Example 3 — CNS penetrant compound', smiles: 'COc1ccc(CCN(C)CCC2=CN=CC=C2)cc1OC', name: 'Experimental CNS Compound' },
];

const LandingPage = () => {
  const [scrollY, setScrollY] = useState(0);
  // Form state
  const [smiles, setSmiles] = useState('');
  const [drugName, setDrugName] = useState('');
  const [dose, setDose] = useState('');
  const [mode, setMode] = useState('smiles'); // 'smiles' | 'database'
  const [dbSearch, setDbSearch] = useState('');
  const [showDbDropdown, setShowDbDropdown] = useState(false);
  const [selectedDbDrug, setSelectedDbDrug] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const dropdownRef = useRef(null);

  const drugEntries = Object.entries(DRUG_DATABASE);
  const filteredDrugs = drugEntries.filter(([name]) =>
    name.toLowerCase().includes(dbSearch.toLowerCase())
  ).slice(0, 10);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowDbDropdown(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectDbDrug = (name, info) => {
    setSelectedDbDrug({ name, ...info });
    setSmiles(info.smiles);
    setDrugName(name);
    setDbSearch(name);
    setShowDbDropdown(false);
  };

  const handleLoadExample = (ex) => {
    setSmiles(ex.smiles);
    setDrugName(ex.name);
    setMode('smiles');
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!smiles.trim()) { setError('Please enter a SMILES string or select from the database.'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          smiles: smiles.trim(),
          drug_name: drugName.trim() || undefined,
          dose_mg: dose ? parseFloat(dose) : undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Analysis failed');
      navigate('/analysis', { state: { result: data } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const scrollRotation = scrollY * 0.35;

  return (
    <div style={{ background: '#02060a', minHeight: '100vh', overflowX: 'hidden', fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Tech Grid */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, backgroundImage: 'linear-gradient(rgba(0,242,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,242,255,0.04) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

      {/* Navbar */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, background: 'rgba(2,6,10,0.88)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(0,242,255,0.1)', padding: '0 48px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Dna size={24} color="#00f2ff" />
          <span style={{ fontFamily: "'Manrope', sans-serif", fontWeight: 800, fontSize: '17px', letterSpacing: '2px', color: '#f8fafc' }}>PHARMA<span style={{ color: '#00f2ff' }}>-AI</span></span>
        </div>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          {['Platform', 'Science', 'Database'].map(item => (
            <span key={item} style={{ color: '#64748b', fontSize: '13px', cursor: 'pointer' }}>{item}</span>
          ))}
          <button
            data-testid="nav-analyze-btn"
            onClick={() => document.getElementById('analyze-section').scrollIntoView({ behavior: 'smooth' })}
            style={{ background: 'linear-gradient(135deg, #00f2ff, #0070ff)', border: 'none', borderRadius: '20px', padding: '8px 22px', color: '#02060a', fontWeight: 700, fontSize: '13px', cursor: 'pointer', letterSpacing: '0.3px' }}
          >Start Analysis</button>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '100px 80px 60px', position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: '560px', flex: 1 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(0,242,255,0.08)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '20px', padding: '6px 16px', marginBottom: '32px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#00ff9d', boxShadow: '0 0 8px #00ff9d', animation: 'pulse 2s infinite' }} />
            <span style={{ color: '#00f2ff', fontSize: '11px', letterSpacing: '2px', fontFamily: 'JetBrains Mono, monospace' }}>AI-POWERED FORMULATION SCIENCE</span>
          </div>
          <h1 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 'clamp(38px, 5vw, 66px)', fontWeight: 800, lineHeight: 1.08, color: '#f8fafc', margin: '0 0 24px 0', letterSpacing: '-2px' }}>
            Optimize
            <span style={{ display: 'block', background: 'linear-gradient(90deg, #00f2ff, #7000ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}> Formulation</span>
            with AI
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '16px', lineHeight: 1.75, marginBottom: '40px', maxWidth: '480px' }}>
            Paste any SMILES — known drug or experimental compound — and get a complete AI-driven formulation analysis in seconds. Bridging the gap between the lab and the clinic.
          </p>
          <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap', marginBottom: '44px' }}>
            {stats.map(s => (
              <div key={s.label}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: s.color, fontFamily: 'Manrope, sans-serif', letterSpacing: '-1px' }}>{s.value}</div>
                <div style={{ fontSize: '10px', color: '#475569', letterSpacing: '1px', marginTop: '2px' }}>{s.label}</div>
              </div>
            ))}
          </div>
          <button
            data-testid="hero-cta-btn"
            onClick={() => document.getElementById('analyze-section').scrollIntoView({ behavior: 'smooth' })}
            style={{ background: 'linear-gradient(135deg, #00f2ff, #7000ff)', border: 'none', borderRadius: '30px', padding: '15px 34px', color: 'white', fontWeight: 700, fontSize: '15px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '10px', boxShadow: '0 0 30px rgba(0,242,255,0.2)' }}
          >
            <FlaskConical size={18} /> Analyze a Molecule
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
          <DNAHelix scrollRotation={scrollRotation} />
        </div>
      </section>

      {/* Scroll indicator */}
      <div style={{ textAlign: 'center', paddingBottom: '20px', zIndex: 1, position: 'relative' }}>
        <ChevronDown size={22} color="rgba(0,242,255,0.35)" style={{ animation: 'bounce 2s infinite' }} />
      </div>

      {/* Feature Cards */}
      <section style={{ padding: '60px 80px', position: 'relative', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '38px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-1px', margin: 0 }}>Core Platform Modules</h2>
          <p style={{ color: '#475569', marginTop: '10px', fontSize: '15px' }}>AI-driven analysis across every critical formulation parameter</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '18px' }}>
          {features.map(({ icon: Icon, title, desc, color }) => (
            <div key={title}
              style={{ background: 'rgba(10,14,20,0.8)', backdropFilter: 'blur(20px)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '14px', padding: '26px 22px', transition: 'border-color 0.3s, transform 0.3s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = color + '50'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ width: '40px', height: '40px', borderRadius: '9px', background: color + '18', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
                <Icon size={20} color={color} />
              </div>
              <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '15px', fontWeight: 600, color: '#f8fafc', margin: '0 0 8px 0' }}>{title}</h3>
              <p style={{ color: '#64748b', fontSize: '12px', lineHeight: 1.6, margin: 0 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ─── ANALYSIS FORM ─────────────────────────────────────────────── */}
      <section id="analyze-section" style={{ padding: '60px 80px 100px', position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: '700px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '36px', fontWeight: 700, color: '#f8fafc', margin: '0 0 10px 0', letterSpacing: '-1px' }}>Start Your Molecular Analysis</h2>
            <p style={{ color: '#64748b', fontSize: '14px' }}>Works for known drugs AND experimental compounds — just provide the SMILES structure</p>
          </div>

          {/* Mode Toggle */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '28px' }}>
            {[
              { id: 'smiles', label: 'Enter SMILES Manually', icon: Beaker },
              { id: 'database', label: 'Pick from Database', icon: Search },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                data-testid={`mode-${id}-btn`}
                onClick={() => { setMode(id); setError(''); }}
                style={{
                  display: 'flex', alignItems: 'center', gap: '8px',
                  padding: '10px 22px', borderRadius: '24px', fontSize: '13px', fontWeight: 600,
                  cursor: 'pointer', border: 'none',
                  background: mode === id ? 'linear-gradient(135deg, #00f2ff22, #7000ff22)' : 'rgba(255,255,255,0.04)',
                  color: mode === id ? '#00f2ff' : '#64748b',
                  boxShadow: mode === id ? 'inset 0 0 0 1px rgba(0,242,255,0.4)' : 'inset 0 0 0 1px rgba(255,255,255,0.07)',
                  transition: 'all 0.2s'
                }}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </div>

          <div style={{ background: 'rgba(10,14,20,0.92)', backdropFilter: 'blur(24px)', border: '1px solid rgba(0,242,255,0.12)', borderRadius: '20px', padding: '36px 40px' }}>
            <form onSubmit={handleAnalyze}>

              {/* DATABASE PICKER MODE */}
              {mode === 'database' && (
                <div style={{ marginBottom: '22px', position: 'relative' }} ref={dropdownRef}>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '10px', letterSpacing: '1.5px', marginBottom: '8px', fontFamily: 'JetBrains Mono, monospace' }}>SEARCH DRUG DATABASE (30 COMPOUNDS)</label>
                  <div style={{ position: 'relative' }}>
                    <Search size={15} color="#475569" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', zIndex: 1 }} />
                    <input
                      data-testid="db-search-input"
                      type="text"
                      value={dbSearch}
                      onChange={e => { setDbSearch(e.target.value); setShowDbDropdown(true); setSelectedDbDrug(null); }}
                      onFocus={() => setShowDbDropdown(true)}
                      placeholder="Search by drug name (e.g. Aspirin, Ibuprofen)..."
                      style={{ width: '100%', padding: '13px 14px 13px 40px', background: 'rgba(0,0,0,0.45)', border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px', color: '#f8fafc', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                    />
                  </div>
                  {showDbDropdown && filteredDrugs.length > 0 && (
                    <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 200, background: 'rgba(8,12,18,0.98)', backdropFilter: 'blur(16px)', border: '1px solid rgba(0,242,255,0.15)', borderRadius: '10px', marginTop: '4px', overflow: 'hidden', maxHeight: '280px', overflowY: 'auto' }}>
                      {filteredDrugs.map(([name, info]) => (
                        <div
                          key={name}
                          data-testid={`db-drug-${name}`}
                          onClick={() => handleSelectDbDrug(name, info)}
                          style={{ padding: '12px 16px', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                          onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,242,255,0.07)'}
                          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                          <div style={{ color: '#e2e8f0', fontSize: '13px', fontWeight: 500 }}>{name}</div>
                          <div style={{ color: '#475569', fontSize: '11px', marginTop: '2px', fontFamily: 'JetBrains Mono, monospace' }}>BCS {info.bcs_class} · MW {info.molecular_weight} g/mol · {info.therapeutic_class}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {selectedDbDrug && (
                    <div style={{ marginTop: '12px', background: 'rgba(0,242,255,0.05)', border: '1px solid rgba(0,242,255,0.18)', borderRadius: '10px', padding: '12px 16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ color: '#00f2ff', fontWeight: 600, fontSize: '13px' }}>{selectedDbDrug.name}</span>
                        <span style={{ color: '#475569', fontSize: '11px' }}>BCS Class {selectedDbDrug.bcs_class}</span>
                      </div>
                      <code style={{ color: '#94a3b8', fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', wordBreak: 'break-all', lineHeight: 1.5, display: 'block' }}>{selectedDbDrug.smiles}</code>
                    </div>
                  )}
                </div>
              )}

              {/* SMILES INPUT (always shown, auto-filled when DB selected) */}
              <div style={{ marginBottom: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label style={{ color: '#94a3b8', fontSize: '10px', letterSpacing: '1.5px', fontFamily: 'JetBrains Mono, monospace' }}>SMILES STRING <span style={{ color: '#ef4444' }}>*</span></label>
                  <span style={{ color: '#334155', fontSize: '10px' }}>Primary input · works for any compound</span>
                </div>
                <textarea
                  data-testid="smiles-input"
                  value={smiles}
                  onChange={e => setSmiles(e.target.value)}
                  placeholder="Paste SMILES here — e.g. CC(=O)Oc1ccccc1C(=O)O (Aspirin)
Or for experimental drugs: c1ccc2c(c1)cc(=O)n2Cc1ccc(cc1)C(=O)N1CCCC1"
                  rows={3}
                  style={{ width: '100%', padding: '13px 14px', background: 'rgba(0,0,0,0.45)', border: smiles ? '1px solid rgba(0,242,255,0.3)' : '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', color: '#f8fafc', fontSize: '12.5px', outline: 'none', boxSizing: 'border-box', resize: 'vertical', fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.6 }}
                />
              </div>

              {/* Quick examples */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ color: '#334155', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px', fontFamily: 'JetBrains Mono, monospace' }}>EXPERIMENTAL EXAMPLES — CLICK TO LOAD</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {EXPERIMENTAL_EXAMPLES.map((ex, i) => (
                    <button
                      key={i}
                      type="button"
                      data-testid={`example-${i}-btn`}
                      onClick={() => handleLoadExample(ex)}
                      style={{ textAlign: 'left', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '8px 12px', color: '#64748b', fontSize: '11px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(112,0,255,0.3)'; e.currentTarget.style.color = '#94a3b8'; }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = '#64748b'; }}
                    >
                      <span>{ex.label}</span>
                      <ChevronRight size={13} />
                    </button>
                  ))}
                </div>
              </div>

              {/* Optional fields row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '24px' }}>
                <div>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '10px', letterSpacing: '1.5px', marginBottom: '7px', fontFamily: 'JetBrains Mono, monospace' }}>COMPOUND NAME <span style={{ color: '#475569' }}>(optional)</span></label>
                  <input
                    data-testid="drug-name-input"
                    type="text"
                    value={drugName}
                    onChange={e => setDrugName(e.target.value)}
                    placeholder="e.g. Drug X, Compound 7A..."
                    style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#94a3b8', fontSize: '10px', letterSpacing: '1.5px', marginBottom: '7px', fontFamily: 'JetBrains Mono, monospace' }}>TARGET DOSE (mg) <span style={{ color: '#475569' }}>(optional)</span></label>
                  <input
                    data-testid="dose-input"
                    type="number"
                    value={dose}
                    onChange={e => setDose(e.target.value)}
                    placeholder="e.g. 500"
                    style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit' }}
                  />
                </div>
              </div>

              {error && (
                <div data-testid="analysis-error" style={{ background: 'rgba(239,68,68,0.09)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '8px', padding: '12px 16px', marginBottom: '18px', color: '#fca5a5', fontSize: '13px' }}>
                  {error}
                </div>
              )}

              <button
                data-testid="analyze-submit-btn"
                type="submit"
                disabled={loading}
                style={{ width: '100%', padding: '15px', background: loading ? 'rgba(0,242,255,0.15)' : 'linear-gradient(135deg, #00f2ff, #7000ff)', border: 'none', borderRadius: '12px', color: loading ? '#94a3b8' : 'white', fontWeight: 700, fontSize: '15px', cursor: loading ? 'not-allowed' : 'pointer', letterSpacing: '0.3px', fontFamily: 'Manrope, sans-serif', transition: 'opacity 0.2s' }}
              >
                {loading ? '⟳ Running AI Analysis — please wait ~20s...' : 'Run Full Formulation Analysis'}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(0,242,255,0.07)', padding: '36px 80px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1, position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Dna size={18} color="#00f2ff" />
          <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, color: '#334155', fontSize: '14px', letterSpacing: '1px' }}>PHARMA-AI</span>
        </div>
        <span style={{ color: '#1e293b', fontSize: '12px' }}>Bridging the gap between the lab and the clinic · AI-Powered Formulation Science</span>
      </footer>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(6px); } }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #02060a; } ::-webkit-scrollbar-thumb { background: #00f2ff22; border-radius: 2px; }
        input::placeholder, textarea::placeholder { color: #334155; }
        input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; }
      `}</style>
    </div>
  );
};

export default LandingPage;
