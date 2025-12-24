@echo off
REM Batch runner: run uniform detector system
cd /d "%~dp0"
python.exe uniform_detector_system.py %*
