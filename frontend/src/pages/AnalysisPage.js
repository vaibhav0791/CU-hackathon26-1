import React, { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts';
import { Dna, FlaskConical, ArrowLeft, Download, Activity, Brain, Microscope, CheckCircle2, AlertTriangle, Clock, Package, Thermometer, Droplets } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// ─ Glassmorphism Card ───────────────────────────────────────────────────────────
const GlassCard = ({ children, style = {}, accentColor = '#00f2ff' }) => (
  <div style={{
    background: 'rgba(10,14,20,0.85)', backdropFilter: 'blur(24px)',
    border: `1px solid ${accentColor}20`,
    borderRadius: '18px', padding: '28px',
    boxShadow: `0 0 40px ${accentColor}08`,
    ...style
  }}>
    {children}
  </div>
);

const SectionTitle = ({ icon: Icon, title, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '22px' }}>
    <div style={{ width: '34px', height: '34px', borderRadius: '8px', background: color + '18', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Icon size={17} color={color} />
    </div>
    <h3 style={{ fontFamily: 'Manrope, sans-serif', fontSize: '14px', fontWeight: 700, color: '#f8fafc', margin: 0, letterSpacing: '0.5px' }}>{title}</h3>
  </div>
);

const MetricBar = ({ label, value, color = '#00f2ff', unit = '' }) => {
  const numVal = parseFloat(value) || 0;
  const pct = Math.min(numVal, 100);
  return (
    <div style={{ marginBottom: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ color: '#94a3b8', fontSize: '12px' }}>{label}</span>
        <span style={{ color, fontSize: '13px', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>{value}{unit}</span>
      </div>
      <div style={{ height: '5px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '3px', boxShadow: `0 0 8px ${color}60`, transition: 'width 1s ease' }} />
      </div>
    </div>
  );
};

const Tag = ({ children, color }) => (
  <span style={{ display: 'inline-block', background: color + '15', border: `1px solid ${color}30`, color, borderRadius: '20px', padding: '3px 10px', fontSize: '11px', fontWeight: 500, margin: '3px' }}>
    {children}
  </span>
);

// Custom chart tooltip
const CustomTooltip = ({ active, payload, label, color = '#00f2ff' }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: 'rgba(10,14,20,0.95)', border: `1px solid ${color}30`, borderRadius: '8px', padding: '10px 14px' }}>
        <p style={{ color: '#94a3b8', fontSize: '11px', margin: '0 0 4px 0' }}>{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color || color, fontSize: '13px', fontWeight: 600, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>
            {p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// ─ Solubility Panel ────────────────────────────────────────────────────────────────
const SolubilityPanel = ({ data }) => {
  if (!data) return null;
  const score = parseFloat(data.prediction) || 0;
  const accuracy = parseFloat(data.accuracy) || 0;
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <GlassCard accentColor="#00f2ff">
      <SectionTitle icon={FlaskConical} title="SOLUBILITY PREDICTION" color="#00f2ff" />
      <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
        {/* Radial Score */}
        <div style={{ textAlign: 'center', flexShrink: 0 }}>
          <svg width="130" height="130" viewBox="0 0 130 130">
            <circle cx="65" cy="65" r={radius} fill="none" stroke="rgba(0,242,255,0.1)" strokeWidth="8" />
            <circle cx="65" cy="65" r={radius} fill="none" stroke="#00f2ff" strokeWidth="8"
              strokeDasharray={circumference} strokeDashoffset={offset}
              strokeLinecap="round" transform="rotate(-90 65 65)"
              style={{ filter: 'drop-shadow(0 0 6px #00f2ff)' }}
            />
            <text x="65" y="60" textAnchor="middle" fill="#f8fafc" fontSize="20" fontWeight="700" fontFamily="Manrope, sans-serif">{score.toFixed(0)}</text>
            <text x="65" y="78" textAnchor="middle" fill="#00f2ff" fontSize="9" fontFamily="JetBrains Mono" letterSpacing="1">SCORE</text>
          </svg>
          <div style={{ color: '#94a3b8', fontSize: '11px', marginTop: '-8px' }}>Accuracy: <span style={{ color: '#00f2ff', fontWeight: 600 }}>{accuracy}%</span></div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ background: 'rgba(0,242,255,0.06)', borderRadius: '10px', padding: '12px 16px', marginBottom: '14px' }}>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>CLASSIFICATION</div>
            <div style={{ color: '#00f2ff', fontWeight: 700, fontSize: '15px' }}>{data.classification}</div>
            {data.aqueous_solubility_mg_ml && <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>Aqueous: {data.aqueous_solubility_mg_ml} mg/mL | pH opt: {data.ph_optimal}</div>}
          </div>
          {data.mechanisms?.map((m, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
              <CheckCircle2 size={12} color="#00f2ff" style={{ marginTop: '2px', flexShrink: 0 }} />
              <span style={{ color: '#94a3b8', fontSize: '12px', lineHeight: 1.5 }}>{m}</span>
            </div>
          ))}
          {data.enhancement_strategies?.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px' }}>ENHANCEMENT STRATEGIES</div>
              {data.enhancement_strategies.map((s, i) => (
                <Tag key={i} color="#00f2ff">{s}</Tag>
              ))}
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};

// ─ Excipient Panel ────────────────────────────────────────────────────────────────
const ExcipientPanel = ({ data }) => {
  if (!data) return null;
  const categories = [
    { key: 'binders', label: 'Binders', color: '#7000ff' },
    { key: 'fillers', label: 'Fillers', color: '#00f2ff' },
    { key: 'disintegrants', label: 'Disintegrants', color: '#00ff9d' },
    { key: 'lubricants', label: 'Lubricants', color: '#f59e0b' },
  ];

  return (
    <GlassCard accentColor="#7000ff">
      <SectionTitle icon={Microscope} title="EXCIPIENT RECOMMENDATIONS" color="#7000ff" />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ background: 'rgba(112,0,255,0.1)', border: '1px solid rgba(112,0,255,0.25)', borderRadius: '8px', padding: '8px 14px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px' }}>OPTIMAL FORM</div>
          <div style={{ color: '#7000ff', fontWeight: 700, fontSize: '14px', marginTop: '2px' }}>{data.optimal_dosage_form || 'Tablet'}</div>
        </div>
        {data.coating?.recommended && (
          <div style={{ background: 'rgba(0,242,255,0.08)', borderRadius: '8px', padding: '8px 14px', textAlign: 'right' }}>
            <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px' }}>COATING</div>
            <div style={{ color: '#00f2ff', fontWeight: 600, fontSize: '13px', marginTop: '2px' }}>{data.coating.type}</div>
          </div>
        )}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
        {categories.map(({ key, label, color }) => (
          <div key={key} style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '12px', padding: '14px' }}>
            <div style={{ color, fontSize: '10px', letterSpacing: '1px', marginBottom: '10px', fontFamily: 'JetBrains Mono, monospace' }}>{label.toUpperCase()}</div>
            {(data[key] || []).slice(0, 2).map((item, i) => (
              <div key={i} style={{ marginBottom: '10px', paddingBottom: '10px', borderBottom: i < (data[key]?.length - 1) ? '1px solid rgba(255,255,255,0.04)' : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#e2e8f0', fontSize: '12px', fontWeight: 500 }}>{item.name}</span>
                  <span style={{ color, fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }}>{item.recommended_conc}</span>
                </div>
                {item.grade && <div style={{ color: '#475569', fontSize: '10px', marginTop: '2px' }}>{item.grade}</div>}
              </div>
            ))}
          </div>
        ))}
      </div>
      {data.incompatibilities?.length > 0 && (
        <div style={{ marginTop: '16px', background: 'rgba(239,68,68,0.06)', borderRadius: '10px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <AlertTriangle size={12} color="#ef4444" />
            <span style={{ color: '#ef4444', fontSize: '10px', letterSpacing: '1px' }}>INCOMPATIBILITIES TO AVOID</span>
          </div>
          {data.incompatibilities.map((inc, i) => (
            <div key={i} style={{ color: '#fca5a5', fontSize: '12px', marginBottom: '4px' }}>• {inc}</div>
          ))}
        </div>
      )}
    </GlassCard>
  );
};

// ─ Stability Panel ─────────────────────────────────────────────────────────────────
const StabilityPanel = ({ data }) => {
  if (!data) return null;

  const longTermData = (data.accelerated_data || []).filter(d => d.condition === '25C/60%RH');
  const accelData = (data.accelerated_data || []).filter(d => d.condition === '40C/75%RH');

  const chartData = longTermData.map(lt => {
    const acc = accelData.find(a => a.months === lt.months);
    return { month: `M${lt.months}`, longTerm: parseFloat(lt.potency) || 100, accelerated: acc ? parseFloat(acc.potency) || 100 : undefined };
  });

  return (
    <GlassCard accentColor="#00ff9d">
      <SectionTitle icon={Activity} title="STABILITY FORECAST" color="#00ff9d" />
      <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ background: 'rgba(0,255,157,0.08)', borderRadius: '12px', padding: '14px 20px', flex: 1, minWidth: '120px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <Clock size={13} color="#00ff9d" />
            <span style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px' }}>SHELF LIFE</span>
          </div>
          <div style={{ color: '#00ff9d', fontFamily: 'Manrope, sans-serif', fontSize: '24px', fontWeight: 800 }}>{data.shelf_life_years}<span style={{ fontSize: '13px', fontWeight: 400, marginLeft: '4px' }}>yrs</span></div>
        </div>
        <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '12px', padding: '14px 20px', flex: 2, minWidth: '180px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px' }}>STORAGE CONDITIONS</div>
          {data.storage_conditions && (
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Thermometer size={12} color="#f59e0b" />
                <span style={{ color: '#e2e8f0', fontSize: '12px' }}>{data.storage_conditions.temperature}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Droplets size={12} color="#3b82f6" />
                <span style={{ color: '#e2e8f0', fontSize: '12px' }}>{data.storage_conditions.humidity}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Package size={12} color="#94a3b8" />
                <span style={{ color: '#e2e8f0', fontSize: '12px' }}>{data.storage_conditions.container}</span>
              </div>
            </div>
          )}
        </div>
      </div>
      {data.degradation_mechanisms?.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px' }}>DEGRADATION MECHANISMS</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {data.degradation_mechanisms.map((m, i) => <Tag key={i} color="#00ff9d">{m}</Tag>)}
          </div>
        </div>
      )}
      {chartData.length > 0 && (
        <div>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '12px' }}>DEGRADATION PROFILE (% Potency)</div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="month" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[85, 101]} tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip color="#00ff9d" />} />
              <Line type="monotone" dataKey="longTerm" name="25°C/60%RH" stroke="#00ff9d" strokeWidth={2} dot={{ fill: '#00ff9d', r: 3 }} />
              <Line type="monotone" dataKey="accelerated" name="40°C/75%RH" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 3 }} strokeDasharray="4 2" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </GlassCard>
  );
};

// ─ PK Panel ────────────────────────────────────────────────────────────────────────
const PKPanel = ({ data }) => {
  if (!data) return null;
  const bioavScore = parseFloat(data.bioavailability_score) || parseFloat(data.bioavailability_percent) || 0;

  // Normalize curve data
  const curveData = (data.bioavailability_curve || []).map(pt => ({
    time: parseFloat(pt.time) || 0,
    concentration: parseFloat(pt.concentration) || 0
  }));

  return (
    <GlassCard accentColor="#f59e0b">
      <SectionTitle icon={Brain} title="PK-COMPATIBILITY & BIOAVAILABILITY" color="#f59e0b" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
        {[
          { label: 'Bioavailability', value: `${data.bioavailability_percent}%`, color: '#f59e0b' },
          { label: 'Tmax', value: `${data.tmax_hours}h`, color: '#00f2ff' },
          { label: 'T½', value: `${data.t_half_hours}h`, color: '#7000ff' },
          { label: 'Protein Binding', value: `${data.protein_binding_percent}%`, color: '#00ff9d' },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ background: 'rgba(0,0,0,0.35)', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
            <div style={{ color: '#475569', fontSize: '9px', letterSpacing: '1px', marginBottom: '6px' }}>{label}</div>
            <div style={{ color, fontFamily: 'Manrope, sans-serif', fontWeight: 800, fontSize: '18px' }}>{value}</div>
          </div>
        ))}
      </div>
      {curveData.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '12px' }}>PLASMA CONCENTRATION-TIME CURVE</div>
          <ResponsiveContainer width="100%" height={170}>
            <AreaChart data={curveData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <defs>
                <linearGradient id="pkGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="time" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} label={{ value: 'Time (h)', position: 'insideBottomRight', fill: '#334155', fontSize: 10 }} />
              <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip color="#f59e0b" />} />
              <Area type="monotone" dataKey="concentration" name="Conc (ng/mL)" stroke="#f59e0b" strokeWidth={2.5} fill="url(#pkGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '10px', padding: '12px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px' }}>METABOLISM</div>
          {data.metabolism && (
            <>
              <div style={{ color: '#e2e8f0', fontSize: '12px', marginBottom: '4px' }}>{data.metabolism.primary_enzyme}</div>
              <div style={{ color: '#475569', fontSize: '11px' }}>1st Pass: {data.metabolism.first_pass}</div>
              {data.metabolism.metabolites?.slice(0, 2).map((m, i) => <Tag key={i} color="#f59e0b">{m}</Tag>)}
            </>
          )}
        </div>
        <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '10px', padding: '12px' }}>
          <div style={{ color: '#64748b', fontSize: '10px', letterSpacing: '1px', marginBottom: '8px' }}>DOSING RECOMMENDATION</div>
          <div style={{ color: '#e2e8f0', fontSize: '12px', lineHeight: 1.5 }}>{data.recommended_dosage_form}</div>
          <div style={{ color: '#f59e0b', fontSize: '11px', marginTop: '6px', fontWeight: 600 }}>{data.dosing_frequency}</div>
        </div>
      </div>
    </GlassCard>
  );
};

// ─ Main Analysis Page ───────────────────────────────────────────────────────────
const AnalysisPage = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [result, setResult] = useState(state?.result || null);
  const [exporting, setExporting] = useState(false);
  const reportRef = useRef(null);

  const handleExportPDF = async () => {
    if (!result) return;
    setExporting(true);
    try {
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 14;
      let y = margin;

      // Header
      pdf.setFillColor(2, 6, 10);
      pdf.rect(0, 0, pageWidth, 36, 'F');
      pdf.setFontSize(20);
      pdf.setTextColor(0, 242, 255);
      pdf.setFont('helvetica', 'bold');
      pdf.text('PHARMA-AI FORMULATION REPORT', margin, 15);
      pdf.setFontSize(9);
      pdf.setTextColor(148, 163, 184);
      pdf.text(`Generated: ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })} | AI-Driven Formulation Optimizer`, margin, 23);
      pdf.text(`Analysis ID: ${result.id || 'N/A'}`, margin, 30);
      y = 46;

      // Drug Info box
      pdf.setFillColor(10, 14, 20);
      pdf.roundedRect(margin, y, pageWidth - margin * 2, 30, 3, 3, 'F');
      pdf.setDrawColor(0, 242, 255);
      pdf.setLineWidth(0.3);
      pdf.roundedRect(margin, y, pageWidth - margin * 2, 30, 3, 3, 'S');
      pdf.setFontSize(16);
      pdf.setTextColor(248, 250, 252);
      pdf.setFont('helvetica', 'bold');
      pdf.text(result.drug_name, margin + 6, y + 10);
      pdf.setFontSize(9);
      pdf.setTextColor(148, 163, 184);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`SMILES: ${result.smiles?.substring(0, 60)}${result.smiles?.length > 60 ? '...' : ''}`, margin + 6, y + 18);
      pdf.text(`MW: ${result.molecular_weight} g/mol | Dose: ${result.dose_mg} mg | Therapeutic Class: ${result.drug_info?.therapeutic_class || 'N/A'}`, margin + 6, y + 25);
      y += 38;

      const addSection = (title, color, contentFn) => {
        if (y > pageHeight - 30) { pdf.addPage(); y = margin; }
        pdf.setFontSize(11);
        pdf.setTextColor(...color);
        pdf.setFont('helvetica', 'bold');
        pdf.text(title, margin, y);
        pdf.setDrawColor(...color);
        pdf.setLineWidth(0.5);
        pdf.line(margin, y + 2, pageWidth - margin, y + 2);
        y += 8;
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(9);
        pdf.setTextColor(203, 213, 225);
        contentFn();
        y += 6;
      };

      const addLine = (text, indent = 0) => {
        if (y > pageHeight - 16) { pdf.addPage(); y = margin; }
        const lines = pdf.splitTextToSize(text, pageWidth - margin * 2 - indent);
        pdf.text(lines, margin + indent, y);
        y += lines.length * 5;
      };

      // Solubility
      addSection('1. SOLUBILITY PREDICTION', [0, 242, 255], () => {
        if (result.solubility) {
          addLine(`Classification: ${result.solubility.classification}`);
          addLine(`Solubility Score: ${result.solubility.prediction} | Prediction Accuracy: ${result.solubility.accuracy}%`);
          if (result.solubility.aqueous_solubility_mg_ml) addLine(`Aqueous Solubility: ${result.solubility.aqueous_solubility_mg_ml} mg/mL | Optimal pH: ${result.solubility.ph_optimal}`);
          if (result.solubility.mechanisms?.length) {
            addLine('Key Mechanisms:');
            result.solubility.mechanisms.forEach(m => addLine(`• ${m}`, 4));
          }
          if (result.solubility.enhancement_strategies?.length) {
            addLine('Enhancement Strategies:');
            result.solubility.enhancement_strategies.forEach(s => addLine(`• ${s}`, 4));
          }
        }
      });

      // Excipients
      addSection('2. EXCIPIENT RECOMMENDATIONS', [112, 0, 255], () => {
        if (result.excipients) {
          addLine(`Optimal Dosage Form: ${result.excipients.optimal_dosage_form}`);
          if (result.excipients.coating?.recommended) addLine(`Coating: ${result.excipients.coating.type} | ${result.excipients.coating.rationale}`);
          ['binders', 'fillers', 'disintegrants', 'lubricants'].forEach(cat => {
            if (result.excipients[cat]?.length) {
              addLine(`${cat.charAt(0).toUpperCase() + cat.slice(1)}:`);
              result.excipients[cat].forEach(e => addLine(`• ${e.name} (${e.grade}) — ${e.recommended_conc} | ${e.rationale}`, 4));
            }
          });
          if (result.excipients.incompatibilities?.length) {
            addLine('Incompatibilities to Avoid:');
            result.excipients.incompatibilities.forEach(i => addLine(`• ${i}`, 4));
          }
        }
      });

      // Stability
      addSection('3. STABILITY FORECAST', [0, 255, 157], () => {
        if (result.stability) {
          addLine(`Predicted Shelf Life: ${result.stability.shelf_life_years} years`);
          addLine(`Primary Degradation: ${result.stability.primary_degradation}`);
          if (result.stability.storage_conditions) {
            const sc = result.stability.storage_conditions;
            addLine(`Storage: ${sc.temperature} | ${sc.humidity} | Light: ${sc.light} | Container: ${sc.container}`);
          }
          if (result.stability.degradation_mechanisms?.length) {
            addLine('Degradation Mechanisms:');
            result.stability.degradation_mechanisms.forEach(m => addLine(`• ${m}`, 4));
          }
          addLine(`Packaging: ${result.stability.packaging_recommendation}`);
        }
      });

      // PK
      addSection('4. PK-COMPATIBILITY & BIOAVAILABILITY', [245, 158, 11], () => {
        if (result.pk_compatibility) {
          const pk = result.pk_compatibility;
          addLine(`Bioavailability: ${pk.bioavailability_percent}% | Absorption: ${pk.absorption_rate}`);
          addLine(`Tmax: ${pk.tmax_hours}h | T½: ${pk.t_half_hours}h | Vd: ${pk.distribution_vd} L/kg | Protein Binding: ${pk.protein_binding_percent}%`);
          if (pk.metabolism) addLine(`Metabolism: ${pk.metabolism.primary_enzyme} | First-Pass: ${pk.metabolism.first_pass}`);
          if (pk.excretion) addLine(`Excretion: ${pk.excretion.route} | Unchanged: ${pk.excretion.percent_unchanged}%`);
          addLine(`Recommended Form: ${pk.recommended_dosage_form}`);
          addLine(`Dosing Frequency: ${pk.dosing_frequency}`);
        }
      });

      // Footer
      pdf.setFontSize(8);
      pdf.setTextColor(71, 85, 105);
      const totalPages = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        pdf.text(`PHARMA-AI | Formulation Optimizer | Page ${i} of ${totalPages}`, margin, pageHeight - 6);
        pdf.text('For research purposes only. Consult a pharmaceutical scientist before manufacturing.', pageWidth - margin, pageHeight - 6, { align: 'right' });
      }

      pdf.save(`PHARMAI_${result.drug_name.replace(/\s/g,'_')}_Report.pdf`);
    } catch (err) {
      console.error('PDF error:', err);
    } finally {
      setExporting(false);
    }
  };

  if (!result) {
    return (
      <div style={{ background: '#02060a', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: "'IBM Plex Sans', sans-serif" }}>
        <div style={{ color: '#94a3b8', fontSize: '16px', marginBottom: '24px' }}>No analysis data. Please run an analysis first.</div>
        <button data-testid="go-home-btn" onClick={() => navigate('/')} style={{ background: 'linear-gradient(135deg, #00f2ff, #7000ff)', border: 'none', borderRadius: '24px', padding: '12px 28px', color: 'white', fontWeight: 700, cursor: 'pointer' }}>Back to Home</button>
      </div>
    );
  }

  return (
    <div style={{ background: '#02060a', minHeight: '100vh', fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Tech Grid Background */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, backgroundImage: 'linear-gradient(rgba(0,242,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,242,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

      {/* Header */}
      <div style={{ position: 'sticky', top: 0, zIndex: 50, background: 'rgba(2,6,10,0.9)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(0,242,255,0.1)', padding: '0 32px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button data-testid="back-btn" onClick={() => navigate('/')} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '7px 14px', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
            <ArrowLeft size={14} /> Back
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Dna size={20} color="#00f2ff" />
            <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '16px', color: '#f8fafc' }}>
              {result.drug_name} <span style={{ color: '#475569', fontWeight: 400, fontSize: '13px' }}>Analysis</span>
            </span>
          </div>
        </div>
        <button
          data-testid="export-pdf-btn"
          onClick={handleExportPDF}
          disabled={exporting}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: exporting ? 'rgba(245,158,11,0.15)' : 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: '8px', padding: '8px 18px', color: '#f59e0b', cursor: exporting ? 'not-allowed' : 'pointer', fontSize: '13px', fontWeight: 600 }}
        >
          <Download size={15} /> {exporting ? 'Exporting...' : 'Export PDF'}
        </button>
      </div>

      {/* Drug Info Bar */}
      <div style={{ padding: '24px 32px 0', position: 'relative', zIndex: 1 }}>
        <div data-testid="drug-info-bar" style={{ background: 'rgba(10,14,20,0.8)', backdropFilter: 'blur(20px)', border: '1px solid rgba(0,242,255,0.12)', borderRadius: '14px', padding: '20px 24px', display: 'flex', gap: '32px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <div style={{ color: '#475569', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>SMILES</div>
            <code style={{ color: '#00f2ff', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace', wordBreak: 'break-all' }}>{result.smiles?.substring(0, 60)}{result.smiles?.length > 60 ? '...' : ''}</code>
          </div>
          {[{ label: 'MW', value: `${result.molecular_weight} g/mol` }, { label: 'Dose', value: `${result.dose_mg} mg` }, { label: 'BCS Class', value: result.drug_info?.bcs_class }, { label: 'LogP', value: result.drug_info?.logp }, { label: 'Class', value: result.drug_info?.therapeutic_class }].map(({ label, value }) => value && (
            <div key={label}>
              <div style={{ color: '#475569', fontSize: '10px', letterSpacing: '1px', marginBottom: '4px' }}>{label}</div>
              <div style={{ color: '#e2e8f0', fontWeight: 600, fontSize: '14px', fontFamily: 'Manrope, sans-serif' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Dashboard Grid */}
      <div ref={reportRef} style={{ padding: '24px 32px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', position: 'relative', zIndex: 1 }}>
        <SolubilityPanel data={result.solubility} />
        <ExcipientPanel data={result.excipients} />
        <StabilityPanel data={result.stability} />
        <PKPanel data={result.pk_compatibility} />
      </div>

      <div style={{ padding: '0 32px 40px', position: 'relative', zIndex: 1 }}>
        <div style={{ color: '#334155', fontSize: '11px', textAlign: 'center' }}>
          Analysis generated by PHARMA-AI | For research purposes only | {new Date().toLocaleDateString()}
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
      `}</style>
    </div>
  );
};

export default AnalysisPage;
