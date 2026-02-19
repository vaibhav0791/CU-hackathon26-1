import React, { useEffect, useRef, useState, useCallback } from 'react';
import { RotateCcw, Eye, Loader2, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const STYLES = [
  { id: 'stick', label: 'Stick' },
  { id: 'sphere', label: 'Sphere' },
  { id: 'ballstick', label: 'Ball & Stick' },
  { id: 'surface', label: 'Surface' },
];

const MoleculeViewer = ({ smiles }) => {
  const viewerRef = useRef(null);
  const glviewerRef = useRef(null);
  const [status, setStatus] = useState('idle'); // idle | loading | ready | error
  const [error, setError] = useState('');
  const [activeStyle, setActiveStyle] = useState('ballstick');
  const [scriptLoaded, setScriptLoaded] = useState(false);

  // Load 3Dmol.js from CDN once
  useEffect(() => {
    if (window.$3Dmol) { setScriptLoaded(true); return; }
    const existing = document.getElementById('3dmol-script');
    if (existing) {
      existing.addEventListener('load', () => setScriptLoaded(true));
      return;
    }
    const script = document.createElement('script');
    script.id = '3dmol-script';
    script.src = 'https://3Dmol.org/build/3Dmol-min.js';
    script.async = true;
    script.onload = () => setScriptLoaded(true);
    script.onerror = () => setError('Failed to load 3D viewer library');
    document.head.appendChild(script);
  }, []);

  const applyStyle = useCallback((viewer, styleName) => {
    if (!viewer) return;
    viewer.setStyle({}, {});
    if (styleName === 'stick') {
      viewer.setStyle({}, { stick: { colorscheme: 'Jmol', radius: 0.15 } });
    } else if (styleName === 'sphere') {
      viewer.setStyle({}, { sphere: { colorscheme: 'Jmol', scale: 0.35 } });
    } else if (styleName === 'ballstick') {
      viewer.setStyle({}, { stick: { colorscheme: 'Jmol', radius: 0.12 }, sphere: { colorscheme: 'Jmol', scale: 0.28 } });
    } else if (styleName === 'surface') {
      viewer.setStyle({}, { stick: { colorscheme: 'Jmol', radius: 0.1 } });
      viewer.addSurface(window.$3Dmol.SurfaceType.VDW, {
        opacity: 0.65,
        colorscheme: { gradient: 'rwb', min: -1, max: 1 }
      });
    }
    viewer.render();
  }, []);

  const loadMolecule = useCallback(async (smilesStr) => {
    if (!scriptLoaded || !smilesStr?.trim()) return;
    setStatus('loading');
    setError('');

    try {
      const res = await fetch(`${BACKEND_URL}/api/molecule3d?smiles=${encodeURIComponent(smilesStr)}`);
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || '3D structure not available');
      }
      const { sdf } = await res.json();

      if (!viewerRef.current || !window.$3Dmol) return;

      // Destroy old viewer
      if (glviewerRef.current) {
        try { glviewerRef.current.clear(); } catch (_) {}
      }
      viewerRef.current.innerHTML = '';

      const viewer = window.$3Dmol.createViewer(viewerRef.current, {
        backgroundColor: '0x0a0e14',
        antialias: true,
      });
      glviewerRef.current = viewer;

      viewer.addModel(sdf, 'sdf');
      applyStyle(viewer, activeStyle);
      viewer.zoomTo();
      viewer.zoom(0.85);
      viewer.render();

      // Gentle auto-spin
      viewer.spin('y', 0.5);

      setStatus('ready');
    } catch (err) {
      setError(err.message || '3D structure unavailable for this compound');
      setStatus('error');
    }
  }, [scriptLoaded, activeStyle, applyStyle]);

  // Re-load when smiles changes
  useEffect(() => {
    if (smiles && smiles.trim().length > 5) {
      const timeout = setTimeout(() => loadMolecule(smiles), 600);
      return () => clearTimeout(timeout);
    }
  }, [smiles, loadMolecule]);

  // Apply style changes to existing viewer
  const handleStyleChange = (style) => {
    setActiveStyle(style);
    if (glviewerRef.current && status === 'ready') {
      try {
        if (style !== 'surface') {
          // Remove surfaces first
          glviewerRef.current.removeAllSurfaces();
        }
        applyStyle(glviewerRef.current, style);
      } catch (_) {}
    }
  };

  const handleResetSpin = () => {
    if (!glviewerRef.current) return;
    glviewerRef.current.spin('y', 0.5);
  };

  return (
    <div style={{ marginTop: '16px', borderRadius: '14px', overflow: 'hidden', border: '1px solid rgba(0,242,255,0.15)', background: 'rgba(5,9,14,0.9)' }}>
      {/* Viewer header */}
      <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(0,242,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Eye size={13} color="#00f2ff" />
          <span style={{ color: '#00f2ff', fontSize: '10px', letterSpacing: '1.5px', fontFamily: 'JetBrains Mono, monospace' }}>3D MOLECULAR VIEWER</span>
        </div>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {STYLES.map(s => (
            <button
              key={s.id}
              onClick={() => handleStyleChange(s.id)}
              style={{
                padding: '4px 10px', borderRadius: '12px', fontSize: '10px', cursor: 'pointer', border: 'none',
                background: activeStyle === s.id ? 'rgba(0,242,255,0.18)' : 'rgba(255,255,255,0.04)',
                color: activeStyle === s.id ? '#00f2ff' : '#475569',
                fontWeight: activeStyle === s.id ? 600 : 400,
              }}
            >{s.label}</button>
          ))}
          <button
            onClick={handleResetSpin}
            title="Resume spin"
            style={{ padding: '4px 8px', borderRadius: '8px', background: 'rgba(255,255,255,0.04)', border: 'none', cursor: 'pointer', color: '#475569', display: 'flex', alignItems: 'center' }}
          ><RotateCcw size={11} /></button>
        </div>
      </div>

      {/* Viewer canvas */}
      <div style={{ position: 'relative', height: '280px', background: '#0a0e14' }}>
        <div ref={viewerRef} style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }} />

        {status === 'idle' && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', border: '1px solid rgba(0,242,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '12px' }}>
              <Eye size={20} color="rgba(0,242,255,0.2)" />
            </div>
            <div style={{ color: '#334155', fontSize: '12px', letterSpacing: '0.5px' }}>3D visualization will appear here</div>
            <div style={{ color: '#1e293b', fontSize: '11px', marginTop: '4px' }}>Enter a SMILES string above</div>
          </div>
        )}

        {status === 'loading' && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(10,14,20,0.7)' }}>
            <Loader2 size={28} color="#00f2ff" style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
            <div style={{ color: '#64748b', fontSize: '12px' }}>Fetching 3D coordinates from PubChem...</div>
          </div>
        )}

        {status === 'error' && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
            <AlertCircle size={24} color="rgba(245,158,11,0.6)" style={{ marginBottom: '10px' }} />
            <div style={{ color: '#92400e', fontSize: '12px', textAlign: 'center', lineHeight: 1.5, maxWidth: '280px' }}>
              {error}
            </div>
            <div style={{ color: '#475569', fontSize: '11px', marginTop: '8px', textAlign: 'center' }}>
              3D view is available for known compounds only.
              <br />The analysis will still run on any SMILES.
            </div>
          </div>
        )}
      </div>

      {status === 'ready' && (
        <div style={{ padding: '7px 14px', background: 'rgba(0,242,255,0.04)', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#334155', fontSize: '10px', fontFamily: 'JetBrains Mono, monospace' }}>Drag to rotate · Scroll to zoom · Right-click to pan</span>
          <span style={{ color: '#1e4040', fontSize: '10px' }}>Source: PubChem</span>
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default MoleculeViewer;
