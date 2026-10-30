@echo off
echo Starting Streamlit Web Interface...
cd /d "%~dp0"
py -3.13 -m streamlit run app_streamlit.py
pause
