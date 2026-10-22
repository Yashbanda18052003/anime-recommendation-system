@echo off
title Anime Recommendation System - Flask Server
cd /d "%~dp0"
echo ===================================================
echo Starting Anime Recommendation System...
echo Note: Loading 2.7GB ML model into RAM takes ~1-2 minutes.
echo ===================================================
venv\Scripts\python.exe app.py
pause
