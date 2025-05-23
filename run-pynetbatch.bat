@echo off
cd /d %~dp0
start /min %~dp0dist\pyNetWatch.exe --config-file=%~dp0pynetwatch-config.json  --config-create=true --log-file=%~dp0pynetwatch.log
