@echo off
cd /d %~dp0
call %~dp0.venv\Scripts\activate.bat
start "PyNetWatch" /min python "%~dp0\pynetwatch.py"