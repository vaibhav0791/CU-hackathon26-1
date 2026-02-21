@echo off
echo ========================================
echo   PHARMA-AI Backend Server
echo ========================================
echo.
echo Starting backend on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.
cd backend
python -m uvicorn server:app --reload --port 8001
pause
