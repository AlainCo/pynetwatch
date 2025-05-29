@echo off
setlocal
call .venv\Scripts\activate
pip freeze > requirements.txt
call .venv\Scripts\deactivate
endlocal
