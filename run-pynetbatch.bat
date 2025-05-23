@echo off
cd /d %~dp0
start /min %~dp0dist\pyNetWatch.exe --config-file=%~dp0perso\config.json  --config-create=true --log-file=%~dp0perso\pynetwatch.log
