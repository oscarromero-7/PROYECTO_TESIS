@echo off
echo Deteniendo OptiMon Dashboard...

REM Buscar y terminar procesos Python que ejecutan optimon_dashboard.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /v "PID"') do (
    wmic process where "ProcessId=%%~i" get CommandLine | findstr "optimon_dashboard.py" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo Terminando proceso %%~i
        taskkill /f /pid %%~i >nul 2>&1
    )
)

REM Verificar que se detuvo
netstat -ano | findstr ":5000" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ❌ El dashboard aún está ejecutándose
) else (
    echo ✅ Dashboard detenido correctamente
)

pause