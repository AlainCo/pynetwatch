
@echo off
setlocal
if not exist .venv\Scripts\activate.bat python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
call .venv\Scripts\deactivate
endlocal