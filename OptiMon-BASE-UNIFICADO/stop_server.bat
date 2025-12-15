@echo off
echo ========================================
echo    OptiMon - Deteniendo Servidor
echo ========================================

echo Buscando procesos de OptiMon...
taskkill /fi "WINDOWTITLE eq OptiMon Server" /f >nul 2>&1
tasklist /fi "IMAGENAME eq python.exe" | findstr app.py >nul 2>&1
if errorlevel 1 (
    echo ✅ No hay servidores OptiMon ejecutándose
) else (
    echo Deteniendo procesos Python relacionados con app.py...
    for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq python.exe" ^| findstr app.py') do (
        taskkill /pid %%i /f >nul 2>&1
    )
    echo ✅ Servidor OptiMon detenido
)

echo.
pause