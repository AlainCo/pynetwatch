@echo off
call .venv\Scripts\activate
rem --noconsole
rem     --collect-all "tkinter" --collect-all customtkinter  ^
rem    --collect-all "pyttsx3" ^
rem     --hidden-import=pyttsx3.drivers --hidden-import=pyttsx3.drivers.dummy --hidden-import=pyttsx3.drivers.espeak ^
rem     --hidden-import=pyttsx3.drivers.nsss --hidden-import=pyttsx3.drivers.sapi5 ^
pyinstaller --windowed --onefile --clean src\pynetwatch.pyw
call .venv\Scripts\deactivate
pause