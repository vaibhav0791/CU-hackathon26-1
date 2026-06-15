# 🚀 PHARMA-AI - Quick Start Guide

## ✅ Production Build Ready!

Your app is now built and ready to run directly from files!

## 📂 What Was Created

1. **`frontend/build/`** - Production-ready static files
2. **`OPEN_THIS.html`** - Launch page (double-click to open)
3. **`START_BACKEND.bat`** - Backend server starter

## 🎯 How to Run (2 Simple Steps)

### Step 1: Start the Backend Server

**Option A - Using Batch File (Easiest):**
- Double-click `START_BACKEND.bat`
- Wait for "Application startup complete" message

**Option B - Manual:**
```bash
cd backend
python -m uvicorn server:app --reload --port 8001
```

### Step 2: Open the Frontend

- Double-click `OPEN_THIS.html`
- Click "🚀 Launch PHARMA-AI" button
- The app will open in your browser!

## 🌐 URLs

- **Frontend:** `file:///path/to/frontend/build/index.html`
- **Backend API:** `http://localhost:8001`
- **API Docs:** `http://localhost:8001/docs`

## 📝 Important Notes

1. ✅ Frontend runs directly from files (no server needed)
2. ⚠️ Backend MUST be running for the app to work
3. 🔑 Add your Hugging Face API key to `backend/.env`:
   ```
   HF_API_KEY=your_actual_key_here
   ```

## 🎨 Features

- **Solubility Analysis** - BCS classification & enhancement strategies
- **PK/PD Simulation** - Pharmacokinetic curves & bioavailability
- **Formulation Plan** - Excipient recommendations with rationale
- **Stability Forecast** - Shelf-life predictions & storage conditions
- **3D Molecular Viewer** - Interactive molecule visualization

## 🐛 Troubleshooting

**Backend won't start?**
- Make sure Python 3.11+ is installed
- Install dependencies: `pip install -r backend/requirements.txt`

**Frontend shows errors?**
- Check that backend is running on port 8001
- Open browser console (F12) to see error details

**API key issues?**
- Get a free key from https://huggingface.co/settings/tokens
- Add it to `backend/.env` file

## 📦 File Structure

```
CU-hackathon26/
├── OPEN_THIS.html          ← Start here!
├── START_BACKEND.bat       ← Run this first
├── backend/
│   ├── server.py           ← FastAPI backend
│   ├── .env                ← Add your API key here
│   └── requirements.txt
└── frontend/
    └── build/              ← Production files
        └── index.html      ← Main app
```

## 🎓 For Judges/Demo

1. Double-click `START_BACKEND.bat`
2. Double-click `OPEN_THIS.html`
3. Click "Launch PHARMA-AI"
4. Try analyzing: Aspirin, Ibuprofen, or any SMILES string!

---

**Built with:** React 18 + FastAPI + Llama-3.3-70B + RDKit
