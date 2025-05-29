
@echo off
setlocal
call .venv\Scripts\activate
pip install -r requirements.txt
call .venv\Scripts\deactivate
endlocal