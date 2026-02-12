@echo off
title AMTL - Launching All Apps...
echo Starting all backend services...
powershell -ExecutionPolicy Bypass -File "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\services.ps1" start all
echo Waiting for backends...
timeout /t 10 /nobreak >nul
echo Launching desktop apps...
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\elaine.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\workshop.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\ripple.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\touchstone.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\writer.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\learning.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\peterman.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\genie.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\costanza.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\author-studio.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\junk-drawer.bat"
start "" "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK\desktop-apps\launchers\supervisor.bat"
echo.
echo All apps launching!
timeout /t 5 /nobreak >nul
exit
