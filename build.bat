@echo off
call .venv\Scripts\activate
pyinstaller --windowed --onefile --clean --add-data "icons/*.ico;icons/"  src\pynetwatch.pyw
call .venv\Scripts\deactivate