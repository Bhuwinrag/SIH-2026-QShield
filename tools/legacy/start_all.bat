@echo off
echo ==============================================
echo           Q-SHIELD STARTUP SCRIPT
echo ==============================================
echo.

echo Note: This script requires PostgreSQL (port 5432) and Redis (port 6379) to be running natively.
echo If they are not running, please start them now.
echo.
pause

start cmd /k "start_backend.bat"
start cmd /k "start_worker.bat"
start cmd /k "start_frontend.bat"

echo.
echo Services have been started in new windows!
echo Backend API: http://localhost:8000/docs
echo Frontend UI: http://localhost:5173
echo.
