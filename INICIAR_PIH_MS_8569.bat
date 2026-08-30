@echo off
cd /d "%~dp0"
start "" "http://localhost:8569/index.html?v=19"
py -m http.server 8569 --directory docs
