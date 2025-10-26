@echo off
title OptiMon - Instalacion Automatica v3.0.0

:: Arte ASCII simple
echo.
echo  ===============================================
echo    ____        _   _ __  __             
echo   / __ \      ^| ^| ^(_)  \/  ^|            
echo  ^| ^|  ^| ^|_ __ ^| ^|_ ^_ ^| \  / ^| ___  _ __  
echo  ^| ^|  ^| ^| '_ \^| __^| ^| ^| ^|\/^| ^|/ _ \^| '_ \ 
echo  ^| ^|__^| ^| ^|_) ^| ^|_^| ^| ^| ^|  ^| ^| (_) ^| ^| ^|^|
echo   \____/^| .__/ \__^|_^|_^|_^|  ^|_^|\___/^|_^| ^|_^|
echo         ^| ^|                              
echo         ^|_^|         v3.0.0 Sistema Unificado
echo  ===============================================
echo.
echo  [INFO] Iniciando instalacion automatica...
echo  [INFO] Se solicitaran permisos de administrador
echo.
pause

:: Verificar privilegios de administrador y solicitar elevación automáticamente
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ADMIN] Solicitando permisos de administrador...
    echo         Confirmar en ventana UAC que aparecerá
    echo.
    
    :: Re-ejecutar con privilegios de administrador
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

cls
echo.
echo  ===============================================
echo    OPTIMON - INSTALACION CON PRIVILEGIOS
echo  ===============================================
echo.
echo  [OK] Ejecutando con permisos de administrador
echo.

:: Verificar Docker
echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker no encontrado. 
    echo.
    echo Instalar Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Presiona cualquier tecla para abrir la pagina de descarga...
    pause >nul
    start https://www.docker.com/products/docker-desktop
    goto :fin
)
echo [OK] Docker encontrado

:: Verificar Python
echo [2/6] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no encontrado.
    echo.
    echo Instalar Python desde:
    echo https://www.python.org/downloads/
    echo.
    echo Presiona cualquier tecla para abrir la pagina de descarga...
    pause >nul
    start https://www.python.org/downloads/
    goto :fin
)
echo [OK] Python encontrado

:: Instalar dependencias
echo [3/6] Instalando dependencias Python...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %errorLevel% neq 0 (
    echo [ERROR] Error instalando dependencias
    echo [INFO] Intentando instalacion individual...
    python -m pip install flask requests paramiko azure-mgmt-compute azure-mgmt-network azure-mgmt-resource azure-identity
)
echo [OK] Dependencias instaladas

:: Limpiar servicios previos
echo [4/6] Limpiando servicios previos...
docker compose down --remove-orphans >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *app.py*" >nul 2>&1
echo [OK] Servicios limpiados

:: Iniciar servicios Docker
echo [5/6] Iniciando servicios Docker...
docker compose up -d
if %errorLevel% neq 0 (
    echo [ERROR] Error iniciando servicios Docker
    echo [INFO] Verificar que Docker Desktop este ejecutandose
    pause
    goto :fin
)
echo [OK] Servicios Docker iniciados

:: Esperar servicios
echo [6/6] Esperando servicios (15 segundos)...
timeout /t 15 /nobreak >nul

:: Iniciar portal web
echo [WEB] Iniciando portal web OptiMon...
start /B python app.py

:: Esperar portal
echo [WEB] Esperando portal web (5 segundos)...
timeout /t 5 /nobreak >nul

:: Abrir navegadores
echo [WEB] Abriendo interfaces...
start http://localhost:5000
timeout /t 2 /nobreak >nul
start http://localhost:3000

cls
echo.
echo  ===============================================
echo    INSTALACION COMPLETADA EXITOSAMENTE!
echo  ===============================================
echo.
echo  ACCESOS DISPONIBLES:
echo.
echo  ^> Portal OptiMon:  http://localhost:5000
echo  ^> Grafana:         http://localhost:3000
echo    Usuario: admin    Contraseña: admin
echo  ^> Prometheus:      http://localhost:9090  
echo  ^> AlertManager:    http://localhost:9093
echo.
echo  FUNCIONALIDADES:
echo  ^> Monitoreo de tu computadora en tiempo real
echo  ^> Configuracion de credenciales Azure
echo  ^> Generacion automatica de infraestructura
echo  ^> Dashboards avanzados de monitoreo
echo  ^> Sistema de alertas configurado
echo.
echo  SIGUIENTE PASO:
echo  ^> Accede al portal para configurar Azure
echo  ^> Explora los dashboards en Grafana
echo.

:fin
echo  Presiona cualquier tecla para finalizar...
pause >nul