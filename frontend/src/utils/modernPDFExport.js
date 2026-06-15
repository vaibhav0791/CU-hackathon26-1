import jsPDF from 'jspdf';

export const exportModernPDF = (result) => {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const W = pdf.internal.pageSize.getWidth();
  const H = pdf.internal.pageSize.getHeight();
  const M = 15;
  let y = 0;

  // ── MODERN COVER PAGE ─────────────────────────────────────────
  pdf.setFillColor(255, 255, 255);
  pdf.rect(0, 0, W, H, 'F');
  
  // Top gradient bar
  pdf.setFillColor(99, 102, 241);
  pdf.rect(0, 0, W, 8, 'F');
  
  // Logo
  pdf.setFontSize(28); pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(30, 30, 30);
  pdf.text('PHARMA-AI', M, 30);
  
  pdf.setFontSize(11); pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(100, 100, 100);
  pdf.text('Pharmaceutical Formulation Analysis Report', M, 38);
  
  // Drug name
  pdf.setFontSize(22); pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(0, 0, 0);
  pdf.text(result.drug_name, M, 55);
  
  // Status badge
  const badgeColor = result.is_experimental ? [147, 51, 234] : [34, 197, 94];
  pdf.setFillColor(...badgeColor);
  pdf.roundedRect(M, 62, 45, 8, 2, 2, 'F');
  pdf.setFontSize(9); pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(255, 255, 255);
  pdf.text(result.is_experimental ? 'EXPERIMENTAL' : 'APPROVED DRUG', M + 22.5, 67.5, { align: 'center' });
  
  // Key info box
  pdf.setDrawColor(220, 220, 220);
  pdf.setLineWidth(0.5);
  pdf.roundedRect(M, 75, W - M * 2, 35, 3, 3, 'S');
  
  pdf.setFontSize(10); pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(0, 0, 0);
  pdf.text('Molecular Information', M + 5, 83);
  
  pdf.setFontSize(9); pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(60, 60, 60);
  const infoY = 90;
  pdf.text(`SMILES: ${(result.smiles || '').substring(0, 55)}`, M + 5, infoY);
  pdf.text(`Molecular Weight: ${result.molecular_weight} g/mol`, M + 5, infoY + 6);
  pdf.text(`BCS Class: ${result.drug_info?.bcs_class || 'N/A'}`, M + 5, infoY + 12);
  pdf.text(`LogP: ${result.drug_info?.logp || 'N/A'}`, M + 5, infoY + 18);
  pdf.text(`Therapeutic Class: ${result.drug_info?.therapeutic_class || 'Unknown'}`, M + 5, infoY + 24);
  
  // Report metadata
  pdf.setFontSize(8);
  pdf.setTextColor(120, 120, 120);
  pdf.text(`Report Generated: ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`, M, 125);
  pdf.text(`Analysis ID: ${result.id || 'N/A'}`, M, 130);
  
  // What's inside
  pdf.setFontSize(11); pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(0, 0, 0);
  pdf.text('What\'s Inside This Report:', M, 145);
  
  pdf.setFontSize(9); pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(60, 60, 60);
  const items = [
    '> Solubility Analysis - How well the drug dissolves',
    '> Formulation Plan - What ingredients are needed',
    '> Stability Forecast - How long it stays effective',
    '> Pharmacokinetics - How it works in your body',
    '> Plain English Explanations - No jargon!'
  ];
  items.forEach((item, i) => {
    pdf.text(item, M + 5, 152 + (i * 7));
  });
  
  // Footer
  pdf.setFontSize(8);
  pdf.setTextColor(150, 150, 150);
  pdf.text('Powered by AI | For Research & Educational Purposes', W / 2, H - 10, { align: 'center' });
  
  // New page
  pdf.addPage();
  y = M;

  // Helper functions
  const addSectionHeader = (title, icon = '') => {
    if (y > H - 30) { pdf.addPage(); y = M; }
    pdf.setFillColor(248, 250, 252);
    pdf.roundedRect(M, y, W - M * 2, 12, 2, 2, 'F');
    pdf.setFontSize(12); pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(0, 0, 0);
    pdf.text(title, M + 5, y + 8);
    y += 18;
  };

  const addSubheading = (text) => {
    if (y > H - 20) { pdf.addPage(); y = M; }
    pdf.setFontSize(10); pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(30, 30, 30);
    pdf.text(text, M + 3, y);
    y += 7;
  };

  const addText = (text, indent = 0, bold = false) => {
    if (y > H - 15) { pdf.addPage(); y = M; }
    pdf.setFontSize(9);
    pdf.setFont('helvetica', bold ? 'bold' : 'normal');
    pdf.setTextColor(50, 50, 50);
    const lines = pdf.splitTextToSize(text, W - M * 2 - indent - 6);
    pdf.text(lines, M + 3 + indent, y);
    y += lines.length * 5 + 2;
  };

  const addHighlight = (text) => {
    if (!text) return;
    if (y > H - 20) { pdf.addPage(); y = M; }
    pdf.setFillColor(254, 249, 195);
    pdf.setFontSize(9); pdf.setFont('helvetica', 'italic');
    pdf.setTextColor(80, 70, 0);
    const lines = pdf.splitTextToSize(`PLAIN ENGLISH: ${text}`, W - M * 2 - 10);
    const textHeight = lines.length * 5 + 4;
    pdf.roundedRect(M, y - 2, W - M * 2, textHeight, 2, 2, 'F');
    pdf.text(lines, M + 5, y + 4);
    y += textHeight + 4;
  };

  const addMetric = (label, value, unit = '') => {
    if (y > H - 15) { pdf.addPage(); y = M; }
    pdf.setFillColor(249, 250, 251);
    pdf.roundedRect(M, y, W - M * 2, 10, 2, 2, 'F');
    pdf.setFontSize(9); pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(100, 100, 100);
    pdf.text(label, M + 4, y + 6.5);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(0, 0, 0);
    pdf.text(`${value}${unit}`, W - M - 4, y + 6.5, { align: 'right' });
    y += 12;
  };

  // ── 1. EXECUTIVE SUMMARY ─────────────────────────────────────
  addSectionHeader('EXECUTIVE SUMMARY');
  addText('This report provides a comprehensive pharmaceutical analysis of ' + result.drug_name + '. Below is a quick overview of the key findings:', 0, false);
  y += 3;
  
  if (result.solubility) {
    const solScore = parseFloat(result.solubility.prediction);
    addText(`- Solubility: ${solScore}/100 - ${result.solubility.classification}`, 3, false);
  }
  if (result.pk_compatibility) {
    addText(`- Bioavailability: ${result.pk_compatibility.bioavailability_percent}% - ${result.pk_compatibility.absorption_rate} absorption`, 3, false);
  }
  if (result.stability) {
    addText(`- Shelf Life: ${result.stability.shelf_life_years} years under proper storage`, 3, false);
  }
  if (result.excipients) {
    addText(`- Dosage Form: ${result.excipients.optimal_dosage_form}`, 3, false);
  }
  y += 5;

  // ── 2. SOLUBILITY ANALYSIS ──────────────────────────────────
  if (result.solubility) {
    addSectionHeader('SOLUBILITY ANALYSIS - Will It Dissolve?');
    const sol = result.solubility;
    
    addSubheading('What This Means:');
    addText('Solubility determines how well the drug dissolves in water. Better solubility means the drug can be absorbed more easily by your body.');
    y += 3;
    
    addMetric('Solubility Score', `${parseFloat(sol.prediction).toFixed(0)}/100`);
    addMetric('Classification', sol.classification);
    addMetric('Water Solubility', `${sol.aqueous_solubility_mg_ml} mg/mL`);
    addMetric('Best pH Range', sol.ph_optimal);
    y += 3;
    
    if (sol.natural_language_summary) {
      addHighlight(sol.natural_language_summary);
    }
    
    if (sol.enhancement_strategies?.length) {
      addSubheading('How to Improve Dissolution:');
      sol.enhancement_strategies.forEach(s => addText(`- ${s}`, 3));
    }
    y += 5;
  }

  // ── 3. FORMULATION PLAN ─────────────────────────────────────
  if (result.excipients) {
    addSectionHeader('FORMULATION PLAN - Making the Pill');
    const exc = result.excipients;
    
    addSubheading('What This Means:');
    addText('A drug is not just the active ingredient. It needs other materials (excipients) to form a pill, help it dissolve, and make it stable.');
    y += 3;
    
    addMetric('Recommended Form', exc.optimal_dosage_form);
    if (exc.coating?.recommended) {
      addMetric('Coating Type', exc.coating.type);
    }
    y += 3;
    
    addSubheading('Key Ingredients:');
    ['binders', 'fillers', 'disintegrants', 'lubricants'].forEach(cat => {
      if (exc[cat]?.length) {
        const catName = cat.charAt(0).toUpperCase() + cat.slice(1);
        exc[cat].forEach(e => {
          addText(`${catName}: ${e.name} (${e.recommended_conc})`, 3);
          addText(`Why: ${e.rationale}`, 6);
        });
      }
    });
    y += 3;
    
    if (exc.natural_language_summary) {
      addHighlight(exc.natural_language_summary);
    }
    y += 5;
  }

  // ── 4. STABILITY & STORAGE ──────────────────────────────────
  if (result.stability) {
    addSectionHeader('STABILITY - How Long It Lasts');
    const sta = result.stability;
    
    addSubheading('What This Means:');
    addText('Stability tells us how long the drug stays effective and safe. Proper storage is crucial to maintain its potency.');
    y += 3;
    
    addMetric('Estimated Shelf Life', `${sta.shelf_life_years} years`);
    addMetric('Main Degradation Risk', sta.primary_degradation);
    addMetric('Recommended Packaging', sta.packaging_recommendation);
    y += 3;
    
    addSubheading('Storage Conditions:');
    if (sta.storage_conditions) {
      addText(`- Temperature: ${sta.storage_conditions.temperature}`, 3);
      addText(`- Humidity: ${sta.storage_conditions.humidity}`, 3);
      addText(`- Light Protection: ${sta.storage_conditions.light}`, 3);
    }
    y += 3;
    
    if (sta.natural_language_summary) {
      addHighlight(sta.natural_language_summary);
    }
    y += 5;
  }

  // ── 5. PHARMACOKINETICS ─────────────────────────────────────
  if (result.pk_compatibility) {
    addSectionHeader('PHARMACOKINETICS - How It Works in Your Body');
    const pk = result.pk_compatibility;
    
    addSubheading('What This Means:');
    addText('Pharmacokinetics describes what your body does to the drug - how it is absorbed, distributed, metabolized, and eliminated.');
    y += 3;
    
    addMetric('Bioavailability', `${pk.bioavailability_percent}%`);
    addMetric('Time to Peak Effect', `${pk.tmax_hours} hours`);
    addMetric('Half-Life', `${pk.t_half_hours} hours`);
    addMetric('Absorption Rate', pk.absorption_rate);
    addMetric('Dosing Frequency', pk.dosing_frequency);
    y += 3;
    
    addSubheading('What Happens After You Take It:');
    addText(`1. Absorption: The drug enters your bloodstream through ${pk.absorption_mechanism}`, 3);
    addText(`2. Peak Effect: Maximum concentration reached in ${pk.tmax_hours} hours`, 3);
    addText(`3. Duration: Half of the drug is eliminated every ${pk.t_half_hours} hours`, 3);
    addText(`4. Metabolism: Processed by ${pk.metabolism?.primary_enzyme || 'liver enzymes'}`, 3);
    addText(`5. Elimination: Removed via ${pk.excretion?.route || 'kidneys'}`, 3);
    y += 3;
    
    if (pk.natural_language_summary) {
      addHighlight(pk.natural_language_summary);
    }
  }

  // Footer
  pdf.setFontSize(8);
  pdf.setTextColor(150, 150, 150);
  pdf.text('This report is generated by AI for research and educational purposes only.', W / 2, H - 15, { align: 'center' });
  pdf.text('Always consult healthcare professionals for medical advice.', W / 2, H - 10, { align: 'center' });

  pdf.save(`${result.drug_name.replace(/\s+/g, '_')}_Analysis_Report.pdf`);
};
