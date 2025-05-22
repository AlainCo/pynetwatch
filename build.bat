@echo off
call .venv\Scripts\activate
pyinstaller --windowed --onefile --clean --add-data "icons/*.ico;icons/" --name pyNetWatch src\pynetwatch.pyw
call .venv\Scripts\deactivate