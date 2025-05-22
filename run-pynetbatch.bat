@echo off
cd /d %~dp0
start /min %~dp0dist\pynetwatch.exe --config-file=%~dp0pynetwatch-config.json --config-create=true