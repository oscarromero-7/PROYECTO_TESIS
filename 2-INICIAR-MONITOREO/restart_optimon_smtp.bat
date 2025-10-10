@echo off
REM Reiniciar OptiMon SMTP Service

echo =========================================
echo  OptiMon SMTP Service - Reiniciar Servicio
echo =========================================

cd /d "%~dp0"

echo 🔄 Reiniciando OptiMon SMTP Service...
python optimon_smtp_daemon.py restart

if errorlevel 1 (
    echo ❌ Error reiniciando el servicio
    pause
    exit /b 1
)

echo ✅ OptiMon SMTP Service reiniciado exitosamente
pause