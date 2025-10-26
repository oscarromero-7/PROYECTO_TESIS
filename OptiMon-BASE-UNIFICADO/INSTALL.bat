@echo off
:: OptiMon Unified System - Windows Installer
:: Instalador automatico para Windows

echo.
echo =====================================================
echo   OptiMon Sistema Unificado - Instalador Windows
echo =====================================================
echo   Version: 3.0.0-UNIFIED
echo   Configuracion automatica completa
echo.

:: Verificar que estamos en el directorio correcto
if not exist "app.py" (
    echo ERROR: No se encuentra app.py
    echo        Ejecuta este instalador desde el directorio OptiMon-BASE-UNIFICADO
    echo.
    pause
    exit /b 1
)

echo [INFO] Directorio correcto verificado
echo.

:: Verificar Python
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no encontrado
    echo         Instala Python desde https://python.org
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado

:: Verificar Docker
echo [INFO] Verificando Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker no encontrado
    echo         Instala Docker Desktop desde https://docker.com
    echo.
    pause
    exit /b 1
)
echo [OK] Docker encontrado

:: Verificar Docker esta ejecutandose
echo [INFO] Verificando que Docker este ejecutandose...
docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker no esta ejecutandose
    echo         Inicia Docker Desktop y vuelve a intentar
    echo.
    pause
    exit /b 1
)
echo [OK] Docker ejecutandose

echo.
echo [INFO] Todos los requisitos verificados
echo [INFO] Iniciando instalacion automatica...
echo.

:: Ejecutar instalador Python
python install_v2.py

echo.
echo [INFO] Instalacion completada
echo [INFO] OptiMon estara disponible en: http://localhost:5000
echo.
pause