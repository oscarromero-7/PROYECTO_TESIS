@echo off
REM OptiMon Deployment Script para Windows (Batch)
REM Compatible con cualquier version de Windows

setlocal enabledelayedexpansion

echo.
echo [OptiMon] Sistema de Monitoreo de Infraestructura
echo ==================================================
echo.

REM Verificar prerrequisitos
call :check_prerequisites
if errorlevel 1 goto :error_exit

REM Instalar dependencias Python
call :install_python_deps
if errorlevel 1 goto :error_exit

REM Configurar credenciales
call :setup_credentials
if errorlevel 1 goto :error_exit

REM Configurar Prometheus
call :setup_prometheus
if errorlevel 1 goto :error_exit

REM Iniciar servicios
call :start_services
if errorlevel 1 goto :error_exit

REM Verificar servicios
call :verify_services

REM Configuracion automatica
call :auto_discover

REM Mostrar informacion final
call :show_final_info

echo.
echo [OK] Despliegue completado exitosamente!
echo.
pause
goto :eof

:check_prerequisites
echo [INFO] Verificando prerrequisitos...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado
    echo Por favor instala Docker Desktop antes de continuar
    echo https://www.docker.com/products/docker-desktop
    exit /b 1
)
echo [OK] Docker esta instalado

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no esta instalado
    echo Por favor instala Docker Compose antes de continuar
    exit /b 1
)
echo [OK] Docker Compose esta instalado

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python no esta instalado
        echo Por favor instala Python 3.8+ antes de continuar
        echo https://www.python.org/downloads/
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)
echo [OK] Python esta instalado
echo.
exit /b 0

:install_python_deps
echo [INFO] Instalando dependencias Python...

if exist requirements.txt (
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARN] Error instalando dependencias Python
    ) else (
        echo [OK] Dependencias Python instaladas
    )
) else (
    echo [WARN] Archivo requirements.txt no encontrado
)
echo.
exit /b 0

:setup_credentials
echo [INFO] Configurando credenciales...

if not exist "config\credentials.simple.yml" (
    echo [WARN] No se encontro archivo de credenciales simplificado
    echo Por favor configura tus credenciales de nube en:
    echo   - config\credentials.simple.yml
    echo.
    echo Solo necesitas completar las credenciales de AWS o Azure
    echo El sistema detectara automaticamente toda la infraestructura
    echo.
    set /p continue="Quieres continuar sin credenciales de nube? (y/N): "
    if /i not "!continue!"=="y" exit /b 1
) else (
    echo [OK] Archivo de credenciales simplificado encontrado
    echo El sistema detectara automaticamente toda la infraestructura
)
echo.
exit /b 0

:setup_prometheus
echo [INFO] Configurando Prometheus...

if not exist "config\prometheus\prometheus.yml" (
    echo  Creando configuracion basica de Prometheus
    
    REM Crear directorio
    if not exist "config\prometheus" mkdir "config\prometheus"
    
    REM Crear configuracion basica
    echo global: > "config\prometheus\prometheus.yml"
    echo   scrape_interval: 15s >> "config\prometheus\prometheus.yml"
    echo   evaluation_interval: 15s >> "config\prometheus\prometheus.yml"
    echo. >> "config\prometheus\prometheus.yml"
    echo rule_files: >> "config\prometheus\prometheus.yml"
    echo   - "alert.rules.yml" >> "config\prometheus\prometheus.yml"
    echo. >> "config\prometheus\prometheus.yml"
    echo alerting: >> "config\prometheus\prometheus.yml"
    echo   alertmanagers: >> "config\prometheus\prometheus.yml"
    echo     - static_configs: >> "config\prometheus\prometheus.yml"
    echo         - targets: >> "config\prometheus\prometheus.yml"
    echo           - alertmanager:9093 >> "config\prometheus\prometheus.yml"
    echo. >> "config\prometheus\prometheus.yml"
    echo scrape_configs: >> "config\prometheus\prometheus.yml"
    echo   - job_name: 'prometheus' >> "config\prometheus\prometheus.yml"
    echo     static_configs: >> "config\prometheus\prometheus.yml"
    echo       - targets: ['localhost:9090'] >> "config\prometheus\prometheus.yml"
    
    REM Crear reglas de alertas basicas
    echo groups: > "config\prometheus\alert.rules.yml"
    echo   - name: basic-alerts >> "config\prometheus\alert.rules.yml"
    echo     rules: >> "config\prometheus\alert.rules.yml"
    echo       - alert: InstanceDown >> "config\prometheus\alert.rules.yml"
    echo         expr: up == 0 >> "config\prometheus\alert.rules.yml"
    echo         for: 1m >> "config\prometheus\alert.rules.yml"
    echo         labels: >> "config\prometheus\alert.rules.yml"
    echo           severity: critical >> "config\prometheus\alert.rules.yml"
    echo         annotations: >> "config\prometheus\alert.rules.yml"
    echo           summary: "Instancia no disponible" >> "config\prometheus\alert.rules.yml"
)

echo [OK] Prometheus configurado
echo.
exit /b 0

:start_services
echo [INFO] Iniciando servicios Docker...

REM Detener servicios existentes
docker-compose down >nul 2>&1

REM Iniciar servicios
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Error iniciando servicios Docker
    exit /b 1
)

echo [OK] Servicios iniciados exitosamente
echo.
exit /b 0

:verify_services
echo [INFO] Verificando servicios...

REM Esperar que los servicios inicien
timeout /t 10 >nul

REM Verificar servicios uno por uno
call :check_service "Prometheus" 9090
call :check_service "Grafana" 3000
call :check_service "AlertManager" 9093

echo.
exit /b 0

:check_service
set service_name=%~1
set port=%~2

REM Usar curl si esta disponible, sino usar PowerShell como respaldo
curl -s http://localhost:%port% >nul 2>&1
if errorlevel 1 (
    REM Intentar con PowerShell si curl no funciona
    powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:%port%' -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] %service_name% no responde en puerto %port%
    ) else (
        echo [OK] %service_name% esta funcionando en puerto %port%
    )
) else (
    echo [OK] %service_name% esta funcionando en puerto %port%
)
exit /b 0

:auto_discover
echo [INFO] Iniciando descubrimiento automatico...

if exist "config\credentials.simple.yml" (
    echo [INFO] Ejecutando configuracion 100%% automatica...
    echo Esto detectara e instalara Node Exporter automaticamente
    %PYTHON_CMD% scripts\auto_setup.py
) else (
    echo [WARN] Configuracion manual disponible:
    
    if exist "config\aws-credentials.yml" (
        echo [INFO] Configurando monitoreo AWS...
        %PYTHON_CMD% scripts\setup_aws_monitoring.py
    )
    
    if exist "config\azure-credentials.yml" (
        echo [INFO] Configurando monitoreo Azure...
        %PYTHON_CMD% scripts\setup_azure_monitoring.py
    )
)

echo [OK] Configuracion automatica completada
echo.
exit /b 0

:show_final_info
echo.
echo [SUCCESS] Despliegue completado exitosamente!
echo ======================================
echo.
echo [INFO] Accede a los servicios:
echo   - Grafana:      http://localhost:3000 (admin/admin)
echo   - Prometheus:   http://localhost:9090
echo   - AlertManager: http://localhost:9093
echo.
echo [INFO] Comandos utiles:
echo   - Ver logs:           docker-compose logs -f
echo   - Detener servicios:  docker-compose down
echo   - Reiniciar:          docker-compose restart
echo   - Anadir servidor:    make.bat add-server
echo.
echo [INFO] Para mas informacion, consulta README.md
echo.
exit /b 0

:error_exit
echo.
echo [ERROR] Error durante el despliegue
echo Revisa los mensajes anteriores para mas informacion
echo.
pause
exit /b 1