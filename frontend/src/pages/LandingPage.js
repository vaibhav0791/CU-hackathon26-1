import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DNAHelix from '../components/DNAHelix';
import { getDrugNames } from '../data/drugDatabase';
import { Dna, FlaskConical, Activity, Brain, ChevronDown, Microscope, Search } from 'lucide-react';

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

const LandingPage = () => {
  const [scrollY, setScrollY] = useState(0);
  const [drugSearch, setDrugSearch] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [dose, setDose] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const searchRef = useRef(null);

  const drugNames = getDrugNames();
  const filtered = drugNames.filter(d => d.toLowerCase().includes(drugSearch.toLowerCase())).slice(0, 8);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!drugSearch.trim()) { setError('Please enter a drug name'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          drug_name: drugSearch.trim(),
          dose_mg: dose ? parseFloat(dose) : undefined
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
      {/* Tech Grid Background */}
      <div style={{
        position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0,
        backgroundImage: 'linear-gradient(rgba(0,242,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,242,255,0.04) 1px, transparent 1px)',
        backgroundSize: '60px 60px'
      }} />

      {/* Navbar */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        background: 'rgba(2,6,10,0.85)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(0,242,255,0.1)',
        padding: '0 40px', height: '64px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Dna size={24} color="#00f2ff" />
          <span style={{ fontFamily: "'Manrope', sans-serif", fontWeight: 700, fontSize: '18px', letterSpacing: '2px', color: '#f8fafc' }}>PHARMA<span style={{ color: '#00f2ff' }}>-AI</span></span>
        </div>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          {['Platform', 'Science', 'Database'].map(item => (
            <span key={item} style={{ color: '#94a3b8', fontSize: '14px', cursor: 'pointer', letterSpacing: '0.5px' }}>{item}</span>
          ))}
          <button
            data-testid="nav-analyze-btn"
            onClick={() => document.getElementById('analyze-section').scrollIntoView({ behavior: 'smooth' })}
            style={{
              background: 'linear-gradient(135deg, #00f2ff, #0080ff)',
              border: 'none', borderRadius: '20px', padding: '8px 20px',
              color: '#02060a', fontWeight: 700, fontSize: '13px',
              cursor: 'pointer', letterSpacing: '0.5px'
            }}
          >
            Start Analysis
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '100px 80px 60px', position: 'relative', zIndex: 1 }}>
        {/* Left Content */}
        <div style={{ maxWidth: '560px', flex: 1 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            background: 'rgba(0,242,255,0.08)', border: '1px solid rgba(0,242,255,0.2)',
            borderRadius: '20px', padding: '6px 16px', marginBottom: '32px'
          }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#00ff9d', boxShadow: '0 0 8px #00ff9d', animation: 'pulse 2s infinite' }} />
            <span style={{ color: '#00f2ff', fontSize: '11px', letterSpacing: '2px', fontFamily: 'JetBrains Mono, monospace' }}>AI-POWERED FORMULATION SCIENCE</span>
          </div>

          <h1 style={{
            fontFamily: "'Manrope', sans-serif",
            fontSize: 'clamp(40px, 5vw, 68px)',
            fontWeight: 800, lineHeight: 1.08,
            color: '#f8fafc', margin: '0 0 24px 0',
            letterSpacing: '-2px'
          }}>
            Optimize
            <span style={{ display: 'block', background: 'linear-gradient(90deg, #00f2ff, #7000ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}> Formulation</span>
            with AI
          </h1>

          <p style={{ color: '#94a3b8', fontSize: '17px', lineHeight: 1.7, marginBottom: '40px', maxWidth: '480px' }}>
            Advanced PK-compatible dosage form optimization. Predict solubility, recommend excipients, forecast stability, and model bioavailability — powered by cutting-edge AI.
          </p>

          {/* Stats Row */}
          <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap', marginBottom: '48px' }}>
            {stats.map(s => (
              <div key={s.label}>
                <div style={{ fontSize: '26px', fontWeight: 800, color: s.color, fontFamily: 'Manrope, sans-serif', letterSpacing: '-1px' }}>{s.value}</div>
                <div style={{ fontSize: '11px', color: '#475569', letterSpacing: '1px', marginTop: '2px' }}>{s.label}</div>
              </div>
            ))}
          </div>

          <button
            data-testid="hero-cta-btn"
            onClick={() => document.getElementById('analyze-section').scrollIntoView({ behavior: 'smooth' })}
            style={{
              background: 'linear-gradient(135deg, #00f2ff, #7000ff)',
              border: 'none', borderRadius: '30px', padding: '16px 36px',
              color: 'white', fontWeight: 700, fontSize: '15px',
              cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '10px',
              boxShadow: '0 0 30px rgba(0,242,255,0.25)'
            }}
          >
            <FlaskConical size={18} />
            Analyze a Drug
          </button>
        </div>

        {/* DNA Helix Right */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
          <DNAHelix scrollRotation={scrollRotation} />
        </div>
      </section>

      {/* Scroll Indicator */}
      <div style={{ textAlign: 'center', paddingBottom: '20px', zIndex: 1, position: 'relative' }}>
        <ChevronDown size={24} color="rgba(0,242,255,0.4)" style={{ animation: 'bounce 2s infinite' }} />
      </div>

      {/* Feature Cards */}
      <section style={{ padding: '80px 80px', position: 'relative', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '42px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-1px', margin: 0 }}>Core Platform Modules</h2>
          <p style={{ color: '#475569', marginTop: '12px', fontSize: '16px' }}>AI-driven analysis across every critical formulation parameter</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          {features.map(({ icon: Icon, title, desc, color }) => (
            <div
              key={title}
              style={{
                background: 'rgba(10,14,20,0.8)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: '16px', padding: '28px 24px',
                transition: 'border-color 0.3s, transform 0.3s',
                cursor: 'default'
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = color + '50'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: color + '15', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                <Icon size={22} color={color} />
              </div>
              <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '16px', fontWeight: 600, color: '#f8fafc', margin: '0 0 10px 0' }}>{title}</h3>
              <p style={{ color: '#64748b', fontSize: '13px', lineHeight: 1.6, margin: 0 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Analysis Form */}
      <section id="analyze-section" style={{ padding: '80px', position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: '640px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <h2 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '38px', fontWeight: 700, color: '#f8fafc', margin: '0 0 12px 0', letterSpacing: '-1px' }}>Start Your Analysis</h2>
            <p style={{ color: '#64748b', fontSize: '15px' }}>Select from our drug database or enter a custom compound</p>
          </div>

          <div style={{
            background: 'rgba(10,14,20,0.9)', backdropFilter: 'blur(24px)',
            border: '1px solid rgba(0,242,255,0.15)', borderRadius: '20px', padding: '40px'
          }}>
            <form onSubmit={handleAnalyze}>
              {/* Drug Search */}
              <div style={{ marginBottom: '20px', position: 'relative' }} ref={searchRef}>
                <label style={{ display: 'block', color: '#94a3b8', fontSize: '11px', letterSpacing: '1.5px', marginBottom: '8px', fontFamily: 'JetBrains Mono, monospace' }}>DRUG NAME / COMPOUND</label>
                <div style={{ position: 'relative' }}>
                  <Search size={16} color="#475569" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', zIndex: 1 }} />
                  <input
                    data-testid="drug-search-input"
                    type="text"
                    value={drugSearch}
                    onChange={e => { setDrugSearch(e.target.value); setShowSuggestions(true); }}
                    onFocus={() => setShowSuggestions(true)}
                    placeholder="Search drug (e.g., Aspirin, Ibuprofen...)"
                    style={{
                      width: '100%', padding: '14px 14px 14px 42px',
                      background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,242,255,0.2)',
                      borderRadius: '10px', color: '#f8fafc', fontSize: '15px',
                      outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit'
                    }}
                  />
                </div>
                {showSuggestions && filtered.length > 0 && drugSearch && (
                  <div style={{
                    position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                    background: 'rgba(10,14,20,0.98)', backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(0,242,255,0.2)', borderRadius: '10px',
                    marginTop: '4px', overflow: 'hidden'
                  }}>
                    {filtered.map(drug => (
                      <div
                        key={drug}
                        data-testid={`drug-suggestion-${drug}`}
                        onClick={() => { setDrugSearch(drug); setShowSuggestions(false); }}
                        style={{
                          padding: '12px 16px', cursor: 'pointer', color: '#cbd5e1',
                          fontSize: '14px', borderBottom: '1px solid rgba(255,255,255,0.04)'
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,242,255,0.08)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                      >
                        {drug}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Dose */}
              <div style={{ marginBottom: '28px' }}>
                <label style={{ display: 'block', color: '#94a3b8', fontSize: '11px', letterSpacing: '1.5px', marginBottom: '8px', fontFamily: 'JetBrains Mono, monospace' }}>TARGET DOSE (mg) — Optional</label>
                <input
                  data-testid="dose-input"
                  type="number"
                  value={dose}
                  onChange={e => setDose(e.target.value)}
                  placeholder="e.g., 500"
                  style={{
                    width: '100%', padding: '14px',
                    background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '10px', color: '#f8fafc', fontSize: '15px',
                    outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit'
                  }}
                />
              </div>

              {error && (
                <div data-testid="analysis-error" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', padding: '12px 16px', marginBottom: '20px', color: '#fca5a5', fontSize: '14px' }}>
                  {error}
                </div>
              )}

              <button
                data-testid="analyze-submit-btn"
                type="submit"
                disabled={loading}
                style={{
                  width: '100%', padding: '16px',
                  background: loading ? 'rgba(0,242,255,0.2)' : 'linear-gradient(135deg, #00f2ff, #7000ff)',
                  border: 'none', borderRadius: '12px',
                  color: loading ? '#94a3b8' : 'white',
                  fontWeight: 700, fontSize: '15px', cursor: loading ? 'not-allowed' : 'pointer',
                  letterSpacing: '0.5px', fontFamily: 'Manrope, sans-serif'
                }}
              >
                {loading ? 'Running AI Analysis...' : 'Run Formulation Analysis'}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(0,242,255,0.08)', padding: '40px 80px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1, position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Dna size={18} color="#00f2ff" />
          <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, color: '#475569', fontSize: '14px', letterSpacing: '1px' }}>PHARMA-AI</span>
        </div>
        <span style={{ color: '#334155', fontSize: '13px' }}>AI-Driven Formulation Science Platform</span>
      </footer>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(6px); } }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #02060a; } ::-webkit-scrollbar-thumb { background: #00f2ff30; border-radius: 2px; }
        input::placeholder { color: #334155; }
        input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; }
      `}</style>
    </div>
  );
};

export default LandingPage;
