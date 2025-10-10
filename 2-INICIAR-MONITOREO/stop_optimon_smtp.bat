@echo off
REM Detener OptiMon SMTP Service

echo =========================================
echo  OptiMon SMTP Service - Detener Servicio
echo =========================================

cd /d "%~dp0"

echo 🛑 Deteniendo OptiMon SMTP Service...
python optimon_smtp_daemon.py stop

if errorlevel 1 (
    echo ❌ Error deteniendo el servicio
    pause
    exit /b 1
)

echo ✅ OptiMon SMTP Service detenido exitosamente
pause