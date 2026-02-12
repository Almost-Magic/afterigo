@echo off
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "& '%~dp0services.ps1' start workshop"
