@echo off
echo Instalando OptiMon Dashboard Service...

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

REM Instalar dependencias de Python si es necesario
python -m pip install schedule requests

REM Crear tarea programada de Windows
schtasks /create /sc minute /mo 5 /tn "OptiMon Dashboard Service" /tr "python "%~dp0optimon_dashboard_service.py" --service" /f

echo.
echo Servicio OptiMon instalado exitosamente!
echo.
echo Para iniciar: schtasks /run /tn "OptiMon Dashboard Service"
echo Para detener: schtasks /end /tn "OptiMon Dashboard Service"
echo Para desinstalar: schtasks /delete /tn "OptiMon Dashboard Service" /f
echo.
pause
