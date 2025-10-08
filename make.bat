@echo off
REM OptiMon - Comandos de Automatizacion para Windows (Batch)
REM Compatible con cualquier version de Windows

setlocal enabledelayedexpansion

set command=%1
set target=%2

if "%command%"=="" goto :show_help
if "%command%"=="help" goto :show_help

REM Detectar Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python no esta instalado
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Ejecutar comando
if "%command%"=="setup" goto :invoke_setup
if "%command%"=="start" goto :invoke_start
if "%command%"=="stop" goto :invoke_stop
if "%command%"=="restart" goto :invoke_restart
if "%command%"=="status" goto :show_status
if "%command%"=="logs" goto :show_logs
if "%command%"=="test" goto :invoke_test
if "%command%"=="config" goto :invoke_config
if "%command%"=="package" goto :invoke_package
if "%command%"=="clean" goto :invoke_clean
if "%command%"=="add-server" goto :invoke_add_server
if "%command%"=="list-servers" goto :invoke_list_servers
if "%command%"=="setup-aws" goto :invoke_setup_aws
if "%command%"=="setup-azure" goto :invoke_setup_azure

echo [ERROR] Comando no reconocido: %command%
echo Usa 'make.bat help' para ver comandos disponibles
exit /b 1

:show_help
echo.
echo [OptiMon] Sistema de Monitoreo
echo =================================
echo.
echo Comandos disponibles:
echo.
echo   setup          - Despliegue completo del sistema
echo   start          - Iniciar servicios
echo   stop           - Detener servicios
echo   restart        - Reiniciar servicios
echo   status         - Ver estado de servicios
echo   logs           - Ver logs de servicios
echo   test           - Ejecutar pruebas del sistema
echo   config         - Regenerar configuraciones
echo   package        - Crear paquete ZIP para distribucion
echo   clean          - Limpiar datos y contenedores
echo.
echo Comandos especificos:
echo   add-server     - Anadir servidor fisico
echo   list-servers   - Listar servidores configurados
echo   setup-aws      - Configurar monitoreo AWS
echo   setup-azure    - Configurar monitoreo Azure
echo.
echo Ejemplos:
echo   make.bat setup
echo   make.bat logs prometheus
echo   make.bat restart grafana
echo.
goto :eof

:invoke_setup
echo [OptiMon] Iniciando despliegue completo...
call deploy.bat
goto :eof

:invoke_start
echo   Iniciando servicios...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Error iniciando servicios
) else (
    echo [OK] Servicios iniciados
)
goto :eof

:invoke_stop
echo   Deteniendo servicios...
docker-compose down
if errorlevel 1 (
    echo [ERROR] Error deteniendo servicios
) else (
    echo [OK] Servicios detenidos
)
goto :eof

:invoke_restart
if "%target%"=="" (
    echo [INFO] Reiniciando todos los servicios...
    docker-compose restart
) else (
    echo [INFO] Reiniciando servicio: %target%
    docker-compose restart %target%
)
if errorlevel 1 (
    echo [ERROR] Error reiniciando servicios
) else (
    echo [OK] Reinicio completado
)
goto :eof

:show_status
echo [INFO] Estado de servicios:
docker-compose ps
echo.
echo [INFO] URLs de acceso:
echo   - Grafana:      http://localhost:3000
echo   - Prometheus:   http://localhost:9090
echo   - AlertManager: http://localhost:9093
goto :eof

:show_logs
if "%target%"=="" (
    echo [INFO] Logs de todos los servicios
    docker-compose logs -f
) else (
    echo [INFO] Logs de %target%
    docker-compose logs -f %target%
)
goto :eof

:invoke_test
echo  Ejecutando pruebas del sistema...
%PYTHON_CMD% test_system.py
goto :eof

:invoke_config
echo [INFO]  Regenerando configuraciones...
%PYTHON_CMD% scripts\setup_prometheus.py
echo [INFO] Reiniciando Prometheus...
docker-compose restart prometheus
echo [OK] Configuracion actualizada
goto :eof

:invoke_package
echo [INFO] Creando paquete de distribucion...
%PYTHON_CMD% create_package.py
goto :eof

:invoke_clean
echo  Limpiando sistema...
set /p response="Estas seguro? Esto eliminara todos los datos (y/N): "
if /i "%response%"=="y" (
    echo   Eliminando contenedores y volumenes...
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo [OK] Limpieza completada
) else (
    echo [ERROR] Operacion cancelada
)
goto :eof

:invoke_add_server
echo   Anadir servidor fisico
call add_server.bat
goto :eof

:invoke_list_servers
echo [INFO] Servidores configurados:
%PYTHON_CMD% scripts\add_physical_server.py list
goto :eof

:invoke_setup_aws
echo   Configurando monitoreo AWS...
%PYTHON_CMD% scripts\setup_aws_monitoring.py
goto :eof

:invoke_setup_azure
echo   Configurando monitoreo Azure...
%PYTHON_CMD% scripts\setup_azure_monitoring.py
goto :eof