@echo off
echo Starting Q-SHIELD Backend...
cd backend
..\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
