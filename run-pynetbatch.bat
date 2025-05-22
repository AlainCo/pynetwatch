@echo off
cd /d %~dp0
call %~dp0.venv\Scripts\activate.bat
start "PyNetWatch" /min pythonw "%~dp0\pynetwatch.pyw"