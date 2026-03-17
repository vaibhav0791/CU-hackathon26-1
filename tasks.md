# 🧬 PHARMA-AI — Team Task Board

> **Last updated**: March 16, 2026
> **Sprint**: Sprint 1–2 (Foundation) + Sprint 3–4 (Stage 1 Enhancement + Stage 2 Kickoff)
> **Vision**: Build the open-source Insilico Medicine — desktop-deployable AI drug discovery OS

---

## 👥 Team Roster

| Member | Role | Focus Area |
|--------|------|------------|
| **Rishav** | Full-Stack Lead | Backend architecture, API security, AI service integration |
| **Shantanu** | Frontend Specialist | UI/UX, data visualization, 3D viewers, responsive design |
| **Aditya** | QA & Documentation Lead | Testing, docs, DevOps, environment config, code quality |
| **Ani** | Product Engineer | Feature strategy, UX flows, product decisions, AI agent design |
| **Vaibhav** | Data Engineer | Data pipelines, external API integration, ML model pipelines |
| **Himanshu** | Database & Data Engineer | Drug database expansion, data validation, dataset curation |

---

## 🔥 Rishav — Full-Stack Lead & Security

> *Owns backend architecture, core API services, and the AI engine pipeline*

### Sprint 1–2 Tasks (Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| R-1 | **Refactor `server.py`** — Split the monolith into modular files: `routes/`, `models/`, `services/ai_engine.py`, `data/drug_database.py` | 🔴 Critical | Medium | 1.5 days | [ ] |
| R-2 | **SMILES Validation** — Server-side SMILES format validation before AI API (reject invalid SMILES early) | 🔴 Critical | Easy | 0.5 day | [ ] |
| R-3 | **API Rate Limiting** — Add rate limiting middleware (`slowapi`) | 🔴 Critical | Easy | 0.5 day | [ ] |
| R-4 | **Input Sanitization** — Sanitize all `/api/analyze` inputs against injection | 🔴 Critical | Easy | 0.5 day | [ ] |
| R-5 | **Error Handling & Retry** — AI API retry logic with exponential backoff | 🟡 Medium | Medium | 1 day | [ ] |
| R-6 | **Environment Security Audit** — No API keys in code, rotate HF_API_KEY, `.env` gitignored | 🔴 Critical | Easy | 0.5 day | [ ] |

### Sprint 3–4 Tasks (Stage 1 Enhancement + Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| R-7 | **RDKit Descriptor Engine** — Build `services/rdkit_engine.py`: compute MW, LogP, TPSA, HBD, HBA, Lipinski violations, pKa, aromatic rings from SMILES | 🔴 Critical | Medium | 2 days | [ ] |
| R-8 | **ADMET Prediction Service** — Build `services/admet_service.py`: integrate open-source ADMET models for absorption, distribution, metabolism, excretion, toxicity | 🔴 Critical | Hard | 3 days | [ ] |
| R-9 | **Structural Alerts Engine** — Implement PAINS and Brenk toxicophore filters using RDKit | 🟡 Medium | Medium | 1 day | [ ] |
| R-10 | **Drug Comparison API** — Build `POST /api/compare` for side-by-side analysis of 2+ drugs | 🔴 Critical | Hard | 2 days | [ ] |
| R-11 | **Target Prediction API** — Build `POST /api/predict-targets` using ChEMBL similarity search (Morgan fingerprints + Tanimoto) | 🔴 Critical | Hard | 3 days | [ ] |
| R-12 | **User Authentication** — JWT auth system (FastAPI + React) with signup/login/logout | 🟡 Medium | Hard | 3 days | [ ] |
| R-13 | **WebSocket Streaming** — Real-time progress updates during analysis (parsing → computing → predicting) | 🟡 Medium | Medium | 1.5 days | [ ] |
| R-14 | **CORS Hardening** — Restrict CORS to specific frontend origins | 🟡 Medium | Easy | 0.5 day | [ ] |

### Sprint 5–6 Tasks (Stage 3 Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| R-15 | **Docking Engine** — Build `services/docking_engine.py`: integrate AutoDock Vina for binding affinity prediction | 🔴 Critical | Hard | 4 days | [ ] |
| R-16 | **Molecule Generator API** — Build `POST /api/generate-molecules`: RL-based molecule generation for a target | 🔴 Critical | Very Hard | 5 days | [ ] |
| R-17 | **AI Agent Backend** — Build `services/agent.py`: LangChain orchestrator wrapping all tools | 🟡 Medium | Hard | 4 days | [ ] |

---

## ⚡ Shantanu — Frontend Specialist

> *Owns everything the user sees — design, 3D visualization, data dashboards*

### Sprint 1–2 Tasks (Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| S-1 | **Refactor `AnalysisPage.js`** — Break 729 lines into clean components: `SolubilityPanel.jsx`, `ExcipientPanel.jsx`, `StabilityPanel.jsx`, `PKPanel.jsx`, `MoleculeOverview.jsx`, `DrugInfoBar.jsx` | 🔴 Critical | Medium | 1.5 days | [ ] |
| S-2 | **Loading Experience Overhaul** — Step-by-step progress indicator: *Parsing → Solubility → Excipients → Stability → PK...* | 🔴 Critical | Medium | 1.5 days | [ ] |
| S-3 | **Mobile Responsive Design** — Full responsive layout (768px, 1024px breakpoints) | 🟡 Medium | Medium | 2 days | [ ] |
| S-4 | **Hover & Micro-animations** — Scale/glow on GlassCards, fade-in on scroll | 🟢 Low | Easy | 1 day | [ ] |

### Sprint 3–4 Tasks (Stage 1 Enhancement + Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| S-5 | **ADMET Dashboard Panel** — New panel on AnalysisPage showing ADMET results with color-coded risk bars (green=safe, red=toxic) | 🔴 Critical | Medium | 2 days | [ ] |
| S-6 | **Structural Alerts Panel** — Display PAINS/Brenk alerts with highlighted toxic substructures on 2D molecule drawing | 🟡 Medium | Medium | 1.5 days | [ ] |
| S-7 | **Drug Comparison UI** — Side-by-side comparison page with overlaid PK curves and parameter diff highlighting | 🔴 Critical | Hard | 2.5 days | [ ] |
| S-8 | **Drug-Target Network Graph** — Interactive network visualization (cytoscape.js): Drug → Targets → Pathways → Diseases | 🔴 Critical | Hard | 3 days | [ ] |
| S-9 | **Analysis History Page** — "My Analyses" list with search, filter (Known/Experimental), click-to-reopen | 🟡 Medium | Medium | 2 days | [ ] |
| S-10 | **Target Prediction Results Page** — Display predicted protein targets with confidence bars, pathway cards, disease links | 🔴 Critical | Medium | 2 days | [ ] |
| S-11 | **Interactive Onboarding Tour** — First-time user tooltip walkthrough | 🟢 Low | Easy | 1 day | [ ] |
| S-12 | **Dark/Light Theme Toggle** — CSS variables swap | 🟢 Low | Medium | 1 day | [ ] |

### Sprint 5–6 Tasks (Stage 3)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| S-13 | **Docking Visualization** — 3D protein-ligand docking viewer (3Dmol.js): protein surface + ligand in binding pocket, highlight H-bonds and hydrophobic contacts | 🔴 Critical | Hard | 3 days | [ ] |
| S-14 | **Molecule Generator UI** — Input target protein + constraints → display generated candidates ranked by drug-likeness | 🔴 Critical | Hard | 3 days | [ ] |
| S-15 | **AI Agent Chat UI** — Chat interface with message bubbles, inline tool execution cards, suggested prompts sidebar | 🟡 Medium | Hard | 3 days | [ ] |

---

## 📝 Aditya — QA & Documentation Lead

> *Ensures the product works, is well-documented, and properly deployed*

### Sprint 1–2 Tasks (Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| A-1 | **Backend Unit Tests** — pytest tests for all API routes: `/api/drugs`, `/api/drugs/{name}`, `/api/analyze`, `/api/molecule3d`, `/api/analyses` | 🔴 Critical | Easy | 1.5 days | [ ] |
| A-2 | **Frontend Component Tests** — React Testing Library tests for LandingPage form, MoleculeViewer states, DB search | 🟡 Medium | Medium | 1.5 days | [ ] |
| A-3 | **Update README.md** — Fix outdated info, add setup troubleshooting, screenshots, contribution guide | 🔴 Critical | Easy | 0.5 day | [ ] |
| A-4 | **Docker Setup** — Create `docker-compose.yml` for one-command local setup (backend + frontend + MongoDB) | 🔴 Critical | Medium | 1.5 days | [ ] |
| A-5 | **SEO & Meta Tags** — `<title>`, `<meta description>`, Open Graph tags | 🟢 Low | Easy | 0.5 day | [ ] |
| A-6 | **Error Boundary Components** — Wrap each analysis panel in React error boundaries | 🟡 Medium | Easy | 0.5 day | [ ] |

### Sprint 3–4 Tasks (Stage 1 Enhancement + Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| A-7 | **ADMET Service Tests** — Unit tests for all ADMET prediction endpoints with known drug validation | 🔴 Critical | Medium | 1.5 days | [ ] |
| A-8 | **Target Prediction Tests** — Tests for ChEMBL similarity search and target prediction accuracy on known drugs | 🔴 Critical | Medium | 1.5 days | [ ] |
| A-9 | **Integration Tests** — End-to-end: submit SMILES → verify analysis + ADMET + targets → check MongoDB write | 🟡 Medium | Medium | 1.5 days | [ ] |
| A-10 | **API Documentation** — Auto-generate OpenAPI/Swagger docs with clear descriptions for every endpoint | 🟡 Medium | Easy | 0.5 day | [ ] |
| A-11 | **CI/CD Pipeline** — GitHub Actions: run tests on every PR, lint check, build verification | 🔴 Critical | Medium | 2 days | [ ] |
| A-12 | **Test Coverage Report** — pytest-cov, target 80%+ backend, 60%+ frontend | 🟡 Medium | Easy | 0.5 day | [ ] |
| A-13 | **Performance Benchmarks** — Measure and document API response times for each endpoint under load | 🟡 Medium | Medium | 1 day | [ ] |
| A-14 | **Accessibility Audit** — aria-labels, keyboard navigation, screen reader support | 🟢 Low | Medium | 1 day | [ ] |

### Sprint 5–6 Tasks (Stage 3)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| A-15 | **Docking Engine Tests** — Validate docking results against known crystal structures (PDB) | 🔴 Critical | Hard | 2 days | [ ] |
| A-16 | **Agent Integration Tests** — Test multi-tool agent workflows end-to-end | 🟡 Medium | Hard | 2 days | [ ] |
| A-17 | **Security Penetration Testing** — OWASP Top 10 security audit on all endpoints | 🔴 Critical | Hard | 2 days | [ ] |

---

## 🎯 Ani — Product Engineer

> *Designs features that transform a prototype into a $1B platform*

### Sprint 1–2 Tasks (Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| N-1 | **Analysis Dashboard Redesign** — UX flow for "My Analyses": card layout, favoriting, notes, sorting | 🔴 Critical | Medium | 2 days | [ ] |
| N-2 | **Shareable Report Links** — Unique URL per analysis (`/analysis/:id`), copy-to-clipboard, social sharing | 🔴 Critical | Medium | 1.5 days | [ ] |
| N-3 | **User Journey Mapping** — Flow diagrams: new user → first analysis → comparison → share report | 🟡 Medium | Easy | 1 day | [ ] |
| N-4 | **Feature Prioritization Doc** — RICE framework scoring for entire roadmap backlog | 🟡 Medium | Easy | 0.5 day | [ ] |

### Sprint 3–4 Tasks (Stage 1 Enhancement + Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| N-5 | **ADMET Results UX Design** — Design how ADMET data is presented: traffic-light cards, drill-down panels, risk summary | 🔴 Critical | Medium | 2 days | [ ] |
| N-6 | **Target Prediction UX** — Design the target prediction results page: confidence bars, pathway cards, "explore this target" flow | 🔴 Critical | Medium | 2 days | [ ] |
| N-7 | **Drug-Target Network UX** — Design the interactive network graph: node types, colors, interactions, tooltips, filtering | 🔴 Critical | Medium | 1.5 days | [ ] |
| N-8 | **Drug Interaction Checker** — Design UX for drug-drug interaction checks: input 2+ SMILES → interaction risks | 🟡 Medium | Hard | 2 days | [ ] |
| N-9 | **Batch Analysis Flow** — Design UX for CSV upload → progress bar → downloadable batch report | 🟡 Medium | Medium | 1.5 days | [ ] |
| N-10 | **Feedback & Rating System** — Users rate AI prediction accuracy (👍/👎 per panel), stored for training signal | 🟡 Medium | Medium | 1.5 days | [ ] |
| N-11 | **Analytics Dashboard** — Usage stats: total analyses, popular drugs, avg latency, user retention | 🟡 Medium | Medium | 2 days | [ ] |

### Sprint 5–6 Tasks (Stage 3 + Agent)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| N-12 | **Molecule Generator UX** — Design the "design a drug" wizard: target selection → property constraints → generated results ranking | 🔴 Critical | Hard | 3 days | [ ] |
| N-13 | **Docking Results UX** — Design how docking results are displayed: binding pose viewer, affinity comparison table, interaction list | 🔴 Critical | Medium | 2 days | [ ] |
| N-14 | **AI Agent UX Design** — Design the conversational AI interface: chat bubbles, tool execution cards, "agent is thinking" animations, suggested prompts | 🔴 Critical | Hard | 3 days | [ ] |
| N-15 | **Clinical Trial Prediction UX** — Design Phase I/II/III success probability display with comparable trial cards | 🟡 Medium | Medium | 2 days | [ ] |

---

## 📊 Vaibhav — Data Engineer & ML Pipeline Lead

> *Owns data pipelines, external API integrations, and ML model serving*

### Sprint 1–2 Tasks (Foundation)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| V-1 | **MongoDB Schema Design** — Collections: `users`, `analyses`, `comparisons`, `feedback`, `targets`. Indexes on `smiles`, `drug_name`, `timestamp` | 🔴 Critical | Medium | 1.5 days | [ ] |
| V-2 | **Analysis Data Pipeline** — Enrich analysis results: auto-tag BCS class, flag outlier predictions, compute confidence scores | 🔴 Critical | Hard | 2.5 days | [ ] |
| V-3 | **PubChem Data Scraper** — Bulk-fetch drug properties from PubChem API (MW, LogP, pKa, SMILES) | 🟡 Medium | Medium | 1.5 days | [ ] |
| V-4 | **Data Validation Layer** — Validate AI-returned JSON matches expected schema before MongoDB save | 🔴 Critical | Easy | 1 day | [ ] |

### Sprint 3–4 Tasks (Stage 1 Enhancement + Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| V-5 | **ChEMBL Integration Pipeline** — Build data pipeline to download/update ChEMBL bioactivity data for target prediction (compound → target → IC50 values) | 🔴 Critical | Hard | 3 days | [ ] |
| V-6 | **BindingDB Integration** — Download and index BindingDB data for binding affinity lookups | 🔴 Critical | Hard | 2 days | [ ] |
| V-7 | **Morgan Fingerprint Index** — Pre-compute and cache Morgan fingerprints for all ChEMBL compounds for fast similarity search | 🔴 Critical | Medium | 2 days | [ ] |
| V-8 | **ADMET Model Pipeline** — Download, validate, and serve ADMET prediction models (Caco-2, hERG, CYP, BBB) | 🔴 Critical | Hard | 3 days | [ ] |
| V-9 | **Redis Caching Layer** — Cache AI analysis + ADMET + target prediction results by SMILES hash | 🟡 Medium | Medium | 2 days | [ ] |
| V-10 | **Analytics Collection** — Instrument backend: analysis count, latency, error rates, most-searched SMILES | 🟡 Medium | Medium | 1.5 days | [ ] |
| V-11 | **Data Export API** — `GET /api/export` to download analysis data as CSV/JSON | 🟡 Medium | Easy | 1 day | [ ] |
| V-12 | **Backup & Recovery** — MongoDB daily snapshots, point-in-time recovery setup | 🟡 Medium | Medium | 1 day | [ ] |

### Sprint 5–6 Tasks (Stage 3)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| V-13 | **PDB/AlphaFold Pipeline** — Auto-fetch protein structures for docking targets from PDB and AlphaFold DB | 🔴 Critical | Hard | 3 days | [ ] |
| V-14 | **Docking Results Storage** — Design schema and pipeline for storing/retrieving docking poses and affinities | 🟡 Medium | Medium | 1.5 days | [ ] |
| V-15 | **ML Model Registry** — Centralized registry for all ML models (ADMET, target prediction, molecule generation) with versioning | 🟡 Medium | Hard | 2 days | [ ] |

---

## 💊 Himanshu — Database & Dataset Curator

> *Grows the drug database AND curates training datasets for ML models*

### Sprint 1–2 Tasks (Drug Database Expansion)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| H-1 | **Week 1: Cardiovascular Drugs** — Add 10 drugs: Diltiazem, Verapamil, Digoxin, Spironolactone, Propranolol, Nifedipine, Carvedilol, Ramipril, Candesartan, Bisoprolol | 🟡 Medium | Easy | 1 day | [ ] |
| H-2 | **Week 2: Anti-infective Drugs** — Add 10 drugs: Azithromycin, Levofloxacin, Fluconazole, Acyclovir, Oseltamivir, Rifampicin, Trimethoprim, Nitrofurantoin, Clindamycin, Vancomycin | 🟡 Medium | Easy | 1 day | [ ] |
| H-3 | **Data Verification Script** — Python script to validate all SMILES in database (RDKit parsing, sanitization check) | 🟡 Medium | Easy | 0.5 day | [ ] |
| H-4 | **Drug Category Tags** — Add `category` field to each drug (Cardiovascular, CNS, Anti-infective, Oncology, etc.) | 🟢 Low | Easy | 0.5 day | [ ] |

### Sprint 3–4 Tasks (Dataset Curation for Stage 2)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| H-5 | **Week 3: CNS Drugs** — Add 10 drugs: Levetiracetam, Carbamazepine, Valproic Acid, Lithium, Risperidone, Quetiapine, Duloxetine, Venlafaxine, Bupropion, Escitalopram | 🟡 Medium | Easy | 1 day | [ ] |
| H-6 | **Week 4: Oncology Drugs** — Add 10 drugs: Imatinib, Erlotinib, Sorafenib, Sunitinib, Capecitabine, Cyclophosphamide, Doxorubicin, Paclitaxel, Cisplatin, Rituximab | 🟡 Medium | Easy | 1 day | [ ] |
| H-7 | **ADMET Benchmark Dataset** — Curate a validation dataset of 50 drugs with known ADMET properties (from literature) to test our ADMET predictions against | 🔴 Critical | Medium | 2 days | [ ] |
| H-8 | **Target-Drug Validation Set** — Curate 50 known drug-target pairs (from DrugBank) to validate target prediction accuracy | 🔴 Critical | Medium | 2 days | [ ] |
| H-9 | **DrugBank Integration Research** — Research DrugBank API access for automated property fetching | 🟡 Medium | Easy | 1 day | [ ] |
| H-10 | **KEGG Pathway Mapping** — Map all drugs in our database to KEGG pathway IDs for network graph data | 🔴 Critical | Medium | 2 days | [ ] |
| H-11 | **Disease-Target Dataset** — Curate DisGeNET data: map protein targets to diseases for the network visualization | 🔴 Critical | Medium | 2 days | [ ] |
| H-12 | **Database README** — Document drug database format, required fields, how to add new entries | 🟢 Low | Easy | 0.5 day | [ ] |

### Sprint 5–6 Tasks (Stage 3 Dataset Prep)

| # | Task | Priority | Difficulty | Est. Time | Status |
|---|------|----------|-----------|-----------|--------|
| H-13 | **Docking Validation Set** — Curate 30 known drug-protein pairs with crystal structures (from PDB) to validate docking | 🔴 Critical | Hard | 3 days | [ ] |
| H-14 | **Week 5–8: Expand to 100 drugs** — Diabetes, Respiratory, GI, Endocrine drugs (10 per week) | 🟡 Medium | Easy | 4 days | [ ] |
| H-15 | **Clinical Trial Dataset** — Curate ClinicalTrials.gov data: 500 completed trials with outcomes for training the clinical predictor | 🔴 Critical | Hard | 4 days | [ ] |

---

## 📋 Cross-Team Milestones

| Milestone | Target Date | Owner(s) | Dependencies |
|-----------|------------|----------|-------------|
| Backend refactored into modules | End of Week 1 | Rishav | None |
| Frontend components split | End of Week 1 | Shantanu | None |
| MongoDB schema finalized | End of Week 1 | Vaibhav | None |
| Drug database at 50 drugs | End of Week 2 | Himanshu | None |
| 80%+ test coverage | End of Week 2 | Aditya | Rishav (R-1) |
| Docker one-command setup | End of Week 3 | Aditya | R-1 |
| **RDKit + ADMET integrated** | **End of Week 4** | **Rishav + Vaibhav** | R-7, R-8, V-8 |
| **ADMET dashboard live** | **End of Week 4** | **Shantanu** | R-8, S-5 |
| Comparison feature live | End of Week 5 | Rishav + Shantanu | R-10, S-7 |
| **ChEMBL pipeline operational** | **End of Week 6** | **Vaibhav** | V-5, V-7 |
| **Target prediction live** | **End of Week 7** | **Rishav + Shantanu** | R-11, S-8, S-10 |
| ADMET benchmark validated | End of Week 7 | Himanshu + Aditya | H-7, A-7 |
| Drug database at 100 drugs | End of Week 8 | Himanshu | None |
| CI/CD pipeline active | End of Week 4 | Aditya | A-11 |
| Auth system deployed | End of Week 8 | Rishav | R-12 |
| **Docking engine integrated** | **End of Week 10** | **Rishav + Vaibhav** | R-15, V-13 |
| **Molecule generator live** | **End of Week 12** | **Rishav + Shantanu** | R-16, S-14 |
| **AI Agent MVP** | **End of Week 14** | **Rishav + Ani** | R-17, N-14 |
| Demo-ready full platform | End of Week 16 | All | All above |

---

## 🔄 Daily Standup Format

Each team member posts in group chat daily:
```
🟢 Yesterday: [what you finished]
🔵 Today: [what you're working on]
🔴 Blockers: [anything blocking you]
```

---

## 🛰️ Product Roadmap — Insilico-Inspired Expansion

> **Strategy**: Master each stage before docking the next module. No shortcuts.
> See `IMPLEMENTATION_GUIDE.md` for full technical specifications.

### Stage 1 — Chemistry Intelligence ✅ (Current)
- [x] SMILES parsing & molecular descriptors
- [x] AI formulation engine (Llama-3.3-70B)
- [x] Solubility / Excipient / Stability / PK panels
- [x] 3D Molecular Viewer
- [x] PDF report export
- [ ] RDKit descriptor engine (pKa, TPSA, Lipinski) → **Rishav R-7**
- [ ] ADMET prediction service → **Rishav R-8 + Vaibhav V-8**
- [ ] Structural alerts (PAINS, Brenk) → **Rishav R-9**

### Stage 2 — Target & Mechanism Layer
- [ ] ChEMBL data pipeline → **Vaibhav V-5**
- [ ] Morgan fingerprint index → **Vaibhav V-7**
- [ ] Target prediction API → **Rishav R-11**
- [ ] Drug-target network visualization → **Shantanu S-8**
- [ ] Target results page → **Shantanu S-10**
- [ ] Disease-target dataset → **Himanshu H-11**

### Stage 3 — Drug Discovery Engine
- [ ] Docking engine → **Rishav R-15**
- [ ] Protein structure pipeline → **Vaibhav V-13**
- [ ] Docking visualization → **Shantanu S-13**
- [ ] Molecule generator → **Rishav R-16**
- [ ] Molecule generator UI → **Shantanu S-14**
- [ ] Docking validation dataset → **Himanshu H-13**

### Stage 4–7 — Future
- [ ] Clinical trial predictor
- [ ] Digital lab simulations
- [ ] Enterprise multi-tenant platform
- [ ] AI Research Agent → **Rishav R-17 + Ani N-14 + Shantanu S-15**

---

## 🏗️ Technology Progression

| Stage | New Backend Tech | New Frontend Tech | Models / Datasets |
|-------|-----------------|-------------------|-------------------|
| 1 ✅ | FastAPI, RDKit | React, 3Dmol.js | Llama-3.3-70B |
| 2 | ChEMBL API, BindingDB | cytoscape.js | GNN, Morgan FP |
| 3 | AutoDock Vina, Open Babel | DockingViewer | REINVENT, MolGPT |
| 4 | ClinicalTrials.gov API | Trial dashboard | GBM, Transformer |
| 5 | Population PK solver | Simulation viz | SmartCyp, ProTox |
| 6 | PostgreSQL, Redis, Celery | Auth UI, Workspaces | Multi-tenant infra |
| 7 | LangChain, WebSocket | Chat UI | Claude / GPT-4 agent |

---

> *"Become the best SMILES-analysis engine first. Then expand."*
> — PHARMA-AI Product Philosophy
