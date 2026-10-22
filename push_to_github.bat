@echo off
title Push to GitHub
cd /d "%~dp0"
echo Pushing Anime Recommendation System to GitHub...
git push -u origin main
echo.
pause
