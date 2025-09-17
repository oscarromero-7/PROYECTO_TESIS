@echo off
title OptiMon - Instalador de Dependencias
chcp 65001 >nul

echo ========================================
echo OptiMon - Instalacion de Dependencias
echo ========================================
echo.
echo Este script instalara las dependencias Python necesarias para el generador IaC
echo.

:: Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.7+ desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Mostrar version de Python
for /f "delims=" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
echo [OK] Detectado: %PYTHON_VERSION%
echo.

:: Verificar pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pip no esta disponible
    echo Instala pip o actualiza Python
    pause
    exit /b 1
)

:: Instalar dependencias
echo [INFO] Instalando dependencias Python...
echo.

pip install boto3>=1.26.0
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando boto3
    pause
    exit /b 1
)
echo [OK] boto3 instalado (AWS SDK)

pip install azure-identity>=1.12.0
if %errorlevel% neq 0 (
    echo [WARNING] Error instalando azure-identity (opcional para Azure)
)
echo [OK] azure-identity instalado

pip install azure-mgmt-compute>=29.0.0
if %errorlevel% neq 0 (
    echo [WARNING] Error instalando azure-mgmt-compute (opcional para Azure)
)

pip install azure-mgmt-resource>=22.0.0
if %errorlevel% neq 0 (
    echo [WARNING] Error instalando azure-mgmt-resource (opcional para Azure)
)

pip install jinja2>=3.1.0
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando jinja2
    pause
    exit /b 1
)
echo [OK] jinja2 instalado (templates)

pip install psutil>=5.9.0
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando psutil
    pause
    exit /b 1
)
echo [OK] psutil instalado (metricas sistema)

pip install requests>=2.28.0
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando requests
    pause
    exit /b 1
)
echo [OK] requests instalado

echo.
echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Las siguientes dependencias estan listas:
echo - boto3 (AWS)
echo - azure-* (Azure, opcional)
echo - jinja2 (templates)
echo - psutil (metricas)
echo - requests (HTTP)
echo.
echo Ya puedes ejecutar setup.bat para usar OptiMon con generacion IaC
echo.
pause