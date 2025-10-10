@echo off
REM ======================================================
REM OPTIMON - INSTALADOR AUTOMATICO
REM ======================================================

echo.
echo ========================================
echo   OPTIMON - INSTALACION AUTOMATICA
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no esta instalado
    echo.
    echo Por favor instale Python 3.8+ desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python disponible

REM Verificar Docker
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker no esta instalado
    echo.
    echo Por favor instale Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker disponible

REM Instalar dependencias Python
echo.
echo 📦 Instalando dependencias Python...
pip install flask requests psutil

echo.
echo 🧪 Ejecutando pruebas del sistema...
python test_complete_system.py

echo.
echo ========================================
echo   OPTIMON INSTALADO CORRECTAMENTE
echo ========================================
echo.
echo Para iniciar OptiMon ejecute:
echo   start_optimon_auto.bat
echo.
echo Para mas informacion consulte:
echo   README.md
echo.
pause
