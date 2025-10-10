@echo off
echo Iniciando OptiMon Dashboard en segundo plano...
cd /d "%~dp0"

REM Verificar si ya está ejecutándose
netstat -ano | findstr ":5000" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo El dashboard ya está ejecutándose en el puerto 5000
    goto :end
)

REM Iniciar en segundo plano
start "" /min python optimon_dashboard.py

REM Esperar a que se inicie
timeout /t 5 /nobreak >nul

REM Verificar que se inició correctamente
netstat -ano | findstr ":5000" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Dashboard iniciado correctamente en http://localhost:5000
) else (
    echo ❌ Error al iniciar el dashboard
)

:end
pause