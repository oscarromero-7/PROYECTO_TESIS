@echo off
REM ======================================================
REM OPTIMON - VERIFICADOR DE ESTADO AUTOMATICO
REM Verifica que todos los servicios esten funcionando
REM ======================================================

echo.
echo ========================================
echo   OPTIMON - VERIFICACION DE ESTADO
echo ========================================
echo.

cd /d "%~dp0"

set ERRORS=0

echo Verificando servicios de OptiMon...
echo.

REM Verificar Docker
docker --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker no esta disponible
    set /a ERRORS+=1
) else (
    echo ✅ Docker disponible
)

REM Verificar Docker Compose
docker-compose --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker Compose no esta disponible
    set /a ERRORS+=1
) else (
    echo ✅ Docker Compose disponible
)

REM Verificar Python
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no esta disponible
    set /a ERRORS+=1
) else (
    echo ✅ Python disponible
)

echo.
echo Verificando archivos necesarios...
echo.

set FILES=optimon_dashboard.py optimon_smtp_service.py docker-compose.yml
for %%f in (%FILES%) do (
    if exist "%%f" (
        echo ✅ %%f encontrado
    ) else (
        echo ❌ %%f NO encontrado
        set /a ERRORS+=1
    )
)

echo.
echo Verificando servicios en ejecucion...
echo.

REM Verificar puertos
set PORTS=9090 3000 9093 8080 5555
for %%p in (%PORTS%) do (
    netstat -an | findstr :%%p > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo ✅ Puerto %%p en uso
    ) else (
        echo ⚠️  Puerto %%p libre
    )
)

echo.
echo ========================================

if %ERRORS% equ 0 (
    echo ✅ SISTEMA VERIFICADO - TODO OK
    echo.
    echo 🌐 Panel de control: http://localhost:8080
    echo 📊 Grafana: http://localhost:3000
    echo 🔍 Prometheus: http://localhost:9090
) else (
    echo ❌ SE ENCONTRARON %ERRORS% PROBLEMAS
    echo.
    echo Para iniciar OptiMon ejecute: start_optimon_auto.bat
)

echo ========================================
echo.
pause