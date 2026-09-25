@echo off
echo Starting Q-SHIELD Celery Worker...
cd backend
..\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info -P solo
