@echo off
REM ======================================================
REM OPTIMON - SCRIPT DE INICIO AUTOMATICO COMPLETO
REM Inicia todos los servicios necesarios automaticamente
REM ======================================================

echo.
echo ========================================
echo   OPTIMON - INICIO AUTOMATICO
echo ========================================
echo.

REM Cambiar al directorio correcto
cd /d "%~dp0"

REM Verificar si estamos en el directorio correcto
if not exist "optimon_dashboard.py" (
    echo ERROR: No se encontro optimon_dashboard.py
    echo Verifique que este ejecutando desde el directorio correcto
    pause
    exit /b 1
)

echo Iniciando OptiMon automaticamente...
echo.

REM Usar el iniciador automático Python
python optimon_auto_starter.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo   OPTIMON INICIADO CORRECTAMENTE
    echo ========================================
    echo.
    echo Abriendo panel de control en el navegador...
    start http://localhost:8080
    echo.
    echo Para detener OptiMon: stop_optimon.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR AL INICIAR OPTIMON
    echo ========================================
    echo.
    echo Revise los logs para mas detalles
    echo.
)

echo Presione cualquier tecla para salir...
pause > nul