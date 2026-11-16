@echo off
rem Збирає Pulse.exe у папку dist\
pip install -r requirements.txt pyinstaller
pyinstaller --noconsole --onefile --name Pulse --collect-all customtkinter main.py
xcopy /E /I /Y extension dist\extension
echo.
echo Готово: dist\Pulse.exe та dist\extension
pause
