@echo off
title AI Resume Analyzer Server
echo ==============================================================
echo           STARTING AI RESUME ANALYZER LOCAL SERVER
echo ==============================================================
echo.

:: Detect python executable
set PYTHON_EXE=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Users\manoh\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
        set PYTHON_EXE="C:\Users\manoh\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    ) else (
        echo Error: Python was not found in your system PATH or program folders.
        echo Please ensure Python 3.10+ is installed.
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_EXE%
echo Starting Flask App on http://127.0.0.1:5000/
echo Press Ctrl+C in this terminal window to stop the server.
echo.

%PYTHON_EXE% app.py

pause
