@echo off
echo Starting VeriProfile AI - Fake Account Detector Web Interface...
cd /d "%~dp0"
where py >nul 2>nul && (
    py -3.13 app.py 2>nul || py app.py
) || (
    python app.py
)
pause
