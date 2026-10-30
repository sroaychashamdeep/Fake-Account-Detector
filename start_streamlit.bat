@echo off
echo Starting Streamlit Web Interface...
cd /d "%~dp0"
where py >nul 2>nul && (
    py -3.13 -m streamlit run app_streamlit.py 2>nul || py -m streamlit run app_streamlit.py
) || (
    streamlit run app_streamlit.py
)
pause
