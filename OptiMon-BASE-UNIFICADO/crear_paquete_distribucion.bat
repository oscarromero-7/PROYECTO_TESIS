@echo off
setlocal enabledelayedexpansion

cls
title OptiMon - Creador de Paquete de Distribucion

echo.
echo ========================================================
echo         OPTIMON - CREADOR DE PAQUETE DE DISTRIBUCION
echo ========================================================
echo.

:: Cambiar al directorio del proyecto
cd /d "%~dp0"

:: Crear directorio de distribución
set "DIST_DIR=OptiMon-Distribucion-v3.0.0"
if exist "%DIST_DIR%" (
    echo Eliminando paquete anterior...
    rmdir /s /q "%DIST_DIR%"
)

echo Creando paquete de distribucion en: %DIST_DIR%
mkdir "%DIST_DIR%"

:: Copiar archivos esenciales
echo Copiando archivos del sistema...

:: Archivos principales
copy "app.py" "%DIST_DIR%\"
copy "docker-compose.yml" "%DIST_DIR%\"
copy "requirements.txt" "%DIST_DIR%\"

:: Scripts de automatización
copy "SETUP_AUTOMATICO_COMPLETO.bat" "%DIST_DIR%\"
copy "setup_automatico.ps1" "%DIST_DIR%\"
copy "setup_automatico_completo.py" "%DIST_DIR%\"

:: Documentación
copy "README_AUTOMATICO.md" "%DIST_DIR%\README.md"

:: Directorios completos
echo Copiando directorios...
xcopy /e /i "templates" "%DIST_DIR%\templates"
xcopy /e /i "static" "%DIST_DIR%\static"
xcopy /e /i "docker" "%DIST_DIR%\docker"
xcopy /e /i "core" "%DIST_DIR%\core"

:: Crear archivo de verificación
echo Creando archivo de verificacion...
(
echo # OptiMon - Paquete de Distribucion v3.0.0
echo.
echo Contenido del paquete:
echo - app.py: Aplicacion principal
echo - docker-compose.yml: Configuracion de servicios
echo - SETUP_AUTOMATICO_COMPLETO.bat: Instalacion automatica
echo - setup_automatico.ps1: Script PowerShell avanzado
echo - setup_automatico_completo.py: Script Python robusto
echo - templates/: Plantillas web
echo - static/: Archivos estaticos
echo - docker/: Configuraciones Docker
echo - core/: Modulos del sistema
echo.
echo Fecha de creacion: %date% %time%
echo Sistema: OptiMon Unified Monitoring System
echo Version: 3.0.0-UNIFIED
) > "%DIST_DIR%\CONTENIDO.txt"

:: Crear script de instalación específico para distribución
(
echo @echo off
echo cls
echo title OptiMon - Instalacion Automatica
echo.
echo ========================================================
echo          OPTIMON - INSTALACION AUTOMATICA
echo ========================================================
echo.
echo Instalando sistema de monitoreo OptiMon...
echo.
echo Verificando requisitos...
echo.
echo :: Verificar Docker
echo docker --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Docker no esta instalado o no esta en el PATH
echo     echo Por favor instale Docker Desktop antes de continuar
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Verificar Python
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Python no esta instalado o no esta en el PATH
echo     echo Por favor instale Python 3.8+ antes de continuar
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Instalando dependencias Python...
echo pip install -r requirements.txt
echo.
echo echo Iniciando configuracion automatica...
echo SETUP_AUTOMATICO_COMPLETO.bat
) > "%DIST_DIR%\INSTALAR.bat"

:: Crear archivo ZIP
echo Creando archivo ZIP de distribucion...
powershell -command "Compress-Archive -Path '%DIST_DIR%' -DestinationPath '%DIST_DIR%.zip' -Force"

:: Mostrar resultado
echo.
echo ========================================================
echo           PAQUETE DE DISTRIBUCION CREADO
echo ========================================================
echo.
echo Ubicacion: %CD%\%DIST_DIR%.zip
echo Tamaño: 
dir "%DIST_DIR%.zip" | findstr /C:"%DIST_DIR%.zip"
echo.
echo Contenido del paquete:
dir /b "%DIST_DIR%"
echo.
echo ========================================================
echo.
echo El paquete esta listo para distribuir y probar
echo Instrucciones:
echo.
echo 1. Extraer %DIST_DIR%.zip en cualquier ubicacion
echo 2. Ejecutar INSTALAR.bat o SETUP_AUTOMATICO_COMPLETO.bat
echo 3. El sistema se configurara automaticamente
echo.
pause