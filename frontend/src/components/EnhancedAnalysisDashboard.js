import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Beaker, ShieldCheck, Activity, Package } from 'lucide-react';

const EnhancedAnalysisDashboard = ({ data }) => {
  return (
    <div className="p-6 bg-slate-900 text-white min-h-screen font-sans">
      <header className="mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-bold text-cyan-400">PHARMA-AI | Formulation Report</h1>
        <p className="text-slate-400">Molecular ID: {data.smiles}</p>
        <p className="text-sm text-slate-500 mt-2">{data.executive_summary}</p>
      </header>

      {/* 4-Panel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Solubility Panel */}
        <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 backdrop-blur-md">
          <div className="flex items-center gap-3 mb-4 text-cyan-400">
            <Beaker size={24} />
            <h2 className="text-xl font-semibold">Solubility & BCS</h2>
          </div>
          <div className="text-4xl font-bold mb-2">
            {data.solubility_analysis?.score || 'N/A'}/100
          </div>
          <p className="text-slate-300">
            Class: <strong>{data.physicochemical_properties?.bcs_class || 'N/A'}</strong>
          </p>
          <p className="text-sm text-slate-400 mt-2">
            {data.solubility_analysis?.enhancement_strategy || 'No strategy provided'}
          </p>
          <div className="mt-4 text-xs text-slate-500">
            {data.solubility_analysis?.natural_language_summary}
          </div>
        </div>

        {/* PK/PD Simulation Panel */}
        <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 backdrop-blur-md">
          <div className="flex items-center gap-3 mb-4 text-purple-400">
            <Activity size={24} />
            <h2 className="text-xl font-semibold">Pharmacokinetics Curve</h2>
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.pk_pd_simulation?.pk_curve_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" label={{ value: 'Time (h)', position: 'insideBottom', offset: -5 }} />
                <YAxis stroke="#94a3b8" label={{ value: 'Conc (μg/mL)', angle: -90, position: 'insideLeft' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="conc" 
                  stroke="#a855f7" 
                  strokeWidth={3} 
                  dot={{ fill: '#a855f7', r: 4 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="bg-purple-900/20 p-2 rounded">
              <span className="text-slate-400">Tmax:</span> <strong>{data.pk_pd_simulation?.t_max_hours || 'N/A'}h</strong>
            </div>
            <div className="bg-purple-900/20 p-2 rounded">
              <span className="text-slate-400">T½:</span> <strong>{data.pk_pd_simulation?.half_life_hours || 'N/A'}h</strong>
            </div>
          </div>
        </div>

        {/* Excipient Plan */}
        <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 backdrop-blur-md">
          <div className="flex items-center gap-3 mb-4 text-emerald-400">
            <Package size={24} />
            <h2 className="text-xl font-semibold">Optimized Formulation</h2>
          </div>
          <p className="text-sm text-slate-300 mb-3">
            <strong>Form:</strong> {data.formulation_plan?.optimal_dosage_form || 'N/A'}
          </p>
          <ul className="space-y-3">
            {(data.formulation_plan?.excipients || []).map((ex, idx) => (
              <li key={idx} className="text-sm border-l-2 border-emerald-500 pl-3">
                <span className="font-bold">{ex.type}:</span> {ex.name}
                {ex.concentration && <span className="text-emerald-400"> ({ex.concentration})</span>}
                <p className="text-xs text-slate-400 italic mt-1">{ex.rationale}</p>
              </li>
            ))}
          </ul>
          <div className="mt-4 text-xs text-slate-500">
            {data.formulation_plan?.natural_language_summary}
          </div>
        </div>

        {/* Stability Panel */}
        <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 backdrop-blur-md">
          <div className="flex items-center gap-3 mb-4 text-amber-400">
            <ShieldCheck size={24} />
            <h2 className="text-xl font-semibold">Stability Forecast</h2>
          </div>
          <p className="text-lg">
            Est. Shelf Life: <span className="text-amber-400 font-bold">
              {data.stability_report?.shelf_life_estimate_years || 'N/A'}
            </span>
          </p>
          <p className="text-sm text-slate-400 mt-2">
            Risk: {data.stability_report?.degradation_risk || 'N/A'}
          </p>
          <div className="mt-4 p-2 bg-amber-900/20 rounded border border-amber-900/50 text-xs text-amber-200">
            Recommended: {data.stability_report?.packaging_recommendation || 'N/A'}
          </div>
          <div className="mt-4 text-xs text-slate-500">
            {data.stability_report?.natural_language_summary}
          </div>
        </div>
      </div>

      {/* Physicochemical Properties Section */}
      <div className="mt-6 bg-slate-800/50 p-6 rounded-2xl border border-slate-700">
        <h3 className="text-lg font-semibold text-cyan-400 mb-4">Physicochemical Properties</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-slate-400">MW:</span> <strong>{data.physicochemical_properties?.mw || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-400">LogP:</span> <strong>{data.physicochemical_properties?.logp || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-400">HBD:</span> <strong>{data.physicochemical_properties?.hbd || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-400">HBA:</span> <strong>{data.physicochemical_properties?.hba || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-400">TPSA:</span> <strong>{data.physicochemical_properties?.tpsa || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-400">Rotatable Bonds:</span> <strong>{data.physicochemical_properties?.rotatable_bonds || 'N/A'}</strong>
          </div>
          <div className="col-span-2">
            <span className="text-slate-400">Drug-likeness:</span> <strong>{data.physicochemical_properties?.drug_likeness || 'N/A'}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAnalysisDashboard;
