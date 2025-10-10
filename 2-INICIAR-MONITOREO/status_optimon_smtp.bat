@echo off
REM Ver estado de OptiMon SMTP Service

echo =========================================
echo  OptiMon SMTP Service - Estado del Servicio
echo =========================================

cd /d "%~dp0"

python optimon_smtp_daemon.py status

echo.
if exist "logs\optimon_smtp_daemon.log" (
    echo 📄 Últimas líneas del log:
    echo --------------------------------
    powershell "Get-Content 'logs\optimon_smtp_daemon.log' -Tail 10"
    echo --------------------------------
)

echo.
echo 🧪 Probar envío de emails:
echo    python test_simple_email.py
echo.

pause