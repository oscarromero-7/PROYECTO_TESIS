@echo off
REM ======================================================
REM OPTIMON - SCRIPT DE PARADA COMPLETA
REM Detiene todos los servicios de OptiMon
REM ======================================================

echo.
echo ========================================
echo   OPTIMON - DETENIENDO SERVICIOS
echo ========================================
echo.

cd /d "%~dp0"

echo Deteniendo OptiMon automaticamente...
echo.

REM Usar el detenedor automático Python
python optimon_auto_starter.py --stop

echo.
echo Realizando limpieza adicional...

REM Liberar puertos si están ocupados
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5555') do taskkill /f /pid %%a 2>nul

echo.
echo ========================================
echo   OPTIMON DETENIDO CORRECTAMENTE
echo ========================================
echo.
pause