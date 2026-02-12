@echo off
title AMTL - Starting All Backends...
echo Starting all backend services...
powershell -ExecutionPolicy Bypass -File "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\services.ps1" start all
echo.
echo All backends started. Use The Workshop (http://localhost:5003) to access apps.
echo.
pause
