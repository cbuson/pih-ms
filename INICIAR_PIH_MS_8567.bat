@echo off
cd /d "%~dp0docs"
start "" "http://localhost:8567/index.html?v=17"
py -m http.server 8567
pause
