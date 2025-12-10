@echo off
echo Остановка всех процессов Python...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Удаление старой установки...
pip uninstall discordself -y 2>nul

echo Установка библиотеки...
pip install -e .

echo.
echo Готово! Библиотека установлена.
pause

