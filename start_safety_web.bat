@echo off
echo ========================================
echo   AI Safety Evaluation Lab
echo ========================================
echo.
echo Starting web interface...
echo Open: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

cd /d D:\oliver\Actividades\mcp_perplesity\paper-pipeline
streamlit run web\safety_web.py --server.port 8501
