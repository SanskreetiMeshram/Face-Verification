@echo off
echo ===================================================
echo     Starting FaceChain Verify (Universal App)
echo ===================================================
echo.

REM Check if Python virtual environment exists
if not exist "backend_venv" (
    echo Creating Python virtual environment...
    python -m venv backend_venv
    echo Installing dependencies...
    call backend_venv\Scripts\pip install -r backend\requirements.txt
)

echo Starting Universal Server (UI + API + Database)...
call backend_venv\Scripts\python run_server.py
pause
