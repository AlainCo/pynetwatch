@echo off
call .venv\Scripts\activate
pip freeze > requirements.txt
call .venv\Scripts\deactivate
