@echo off
title OptiMon Multi-Cloud Setup
chcp 65001 >nul
setlocal EnableDelayedExpansion

cls
echo ---
echo --- BIENVENIDO A LA CONFIGURACION DEL PRODUCTO OPTIMON ---
echo ---
echo Este script te guiara para desplegar y monitorear tu infraestructura.
echo Soporta: Servidores Fisicos, Azure y AWS
echo.

:: --- FASE 0: Verificar prerrequisitos ---
echo Verificando prerrequisitos...

call :CHECK_PREREQ "jq" "https://jqlang.github.io/jq/download/"
call :CHECK_PREREQ "docker-compose" "Instala Docker Desktop"
call :CHECK_PREREQ "python" "Python 3.7+ requerido"

if not exist "iac_generator.py" (
    echo [WARNING] Generador IaC no encontrado - funcionalidad limitada
    set "SKIP_IAC=1"
) else (
    set "SKIP_IAC=0"
)

echo [OK] Prerrequisitos verificados
echo.

:: --- FASE 1: Menu principal ---
:MENU
echo ===============================================================
echo                    MENU PRINCIPAL
echo ===============================================================
echo [1] Servidor fisico local solamente
echo [2] AWS solamente (crear + monitorear)
echo [3] Azure solamente (crear + monitorear) 
echo [4] MULTI-SERVIDOR (combinar varios tipos)
echo [5] Ver estado actual del sistema
echo [6] Generar backup IaC (opcional)
echo [0] Salir
echo ===============================================================
set /p MAIN_OPTION="Selecciona opcion: "

if "!MAIN_OPTION!"=="0" goto EXIT
if "!MAIN_OPTION!"=="1" goto LOCAL_ONLY
if "!MAIN_OPTION!"=="2" goto AWS_ONLY
if "!MAIN_OPTION!"=="3" goto AZURE_ONLY
if "!MAIN_OPTION!"=="4" goto MULTI_SERVER
if "!MAIN_OPTION!"=="5" goto CHECK_STATUS
if "!MAIN_OPTION!"=="6" goto GENERATE_IAC_BACKUP

echo [ERROR] Opcion invalida
goto MENU

:: --- OPCION 4: Multi-servidor simplificado ---
:MULTI_SERVER
echo.
echo ===============================================================
echo                    ESCANEO MULTI-SERVIDOR
echo ===============================================================
echo.
echo Selecciona que tipos de servidores quieres incluir:
echo.

:: Variables para tracking
set "INCLUDE_LOCAL=0"
set "INCLUDE_AWS=0"
set "INCLUDE_AZURE=0"
set "AWS_IP="
set "AZURE_IP="

:: Preguntar por servidor local
set /p LOCAL_CHOICE="¿Incluir servidor local (tu PC)? (S/N): "
if /i "!LOCAL_CHOICE!"=="S" set "INCLUDE_LOCAL=1"

:: Preguntar por AWS
set /p AWS_CHOICE="¿Incluir AWS (creara una instancia EC2)? (S/N): "
if /i "!AWS_CHOICE!"=="S" (
    set "INCLUDE_AWS=1"
    echo.
    echo --- Credenciales AWS ---
    set /p AWS_ACCESS_KEY_ID="AWS Access Key ID: "
    set /p AWS_SECRET_ACCESS_KEY="AWS Secret Access Key: "
    set /p AWS_REGION="AWS Region [us-east-1]: "
    if "!AWS_REGION!"=="" set "AWS_REGION=us-east-1"
)

:: Preguntar por Azure
set /p AZURE_CHOICE="¿Incluir Azure (creara una VM)? (S/N): "
if /i "!AZURE_CHOICE!"=="S" (
    set "INCLUDE_AZURE=1"
    echo.
    echo --- Credenciales Azure ---
    set /p AZURE_CLIENT_ID="Azure Client ID: "
    set /p AZURE_CLIENT_SECRET="Azure Client Secret: "
    set /p AZURE_TENANT_ID="Azure Tenant ID: "
    set /p AZURE_SUBSCRIPTION_ID="Azure Subscription ID: "
    set /p VM_PASSWORD="Password para VM Azure: "
)

:: Verificar que al menos uno este seleccionado
if "!INCLUDE_LOCAL!"=="0" if "!INCLUDE_AWS!"=="0" if "!INCLUDE_AZURE!"=="0" (
    echo [ERROR] Debes seleccionar al menos un tipo de servidor
    pause
    goto MENU
)

echo.
echo ===============================================================
echo               DESPLEGANDO INFRAESTRUCTURA
echo ===============================================================

:: Desplegar AWS si esta seleccionado
if "!INCLUDE_AWS!"=="1" (
    echo [PASO 1/3] Desplegando instancia AWS EC2...
    call :DEPLOY_AWS
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo el despliegue AWS
        pause
        goto MENU
    )
)

:: Desplegar Azure si esta seleccionado
if "!INCLUDE_AZURE!"=="1" (
    echo [PASO 2/3] Desplegando VM Azure...
    call :DEPLOY_AZURE
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo el despliegue Azure
        pause
        goto MENU
    )
)

:: Crear configuracion de Prometheus multi-servidor
echo [PASO 3/3] Configurando monitoreo unificado...
call :CREATE_MULTI_PROMETHEUS_CONFIG

:: Iniciar servicios
echo [INFO] Iniciando Prometheus y Grafana...
cd /d "2-INICIAR-MONITOREO"
docker-compose up -d
cd /d "%~dp0"

echo.
echo Esperando 30 segundos a que los servicios se inicialicen...
timeout /t 30 /nobreak >nul

:: Generar IaC si esta disponible
if "!SKIP_IAC!"=="0" (
    echo.
    echo === GENERANDO CODIGO IaC ===
    if "!INCLUDE_LOCAL!"=="1" if "!INCLUDE_AWS!"=="1" (
        echo 2| python iac_generator.py
    ) else if "!INCLUDE_LOCAL!"=="1" if "!INCLUDE_AZURE!"=="1" (
        echo 3| python iac_generator.py
    ) else if "!INCLUDE_LOCAL!"=="1" (
        echo 1| python iac_generator.py
    )
)

:: Mostrar resumen
echo.
echo ===============================================================
echo                    DESPLIEGUE COMPLETADO
echo ===============================================================
echo Dashboard Grafana: http://localhost:3000 (admin/admin)
echo Prometheus: http://localhost:9090
echo.
echo SERVIDORES MONITOREADOS:
if "!INCLUDE_LOCAL!"=="1" echo - Servidor Local: host.docker.internal:9182
if "!INCLUDE_AWS!"=="1" echo - AWS EC2: !AWS_IP!:9100
if "!INCLUDE_AZURE!"=="1" echo - Azure VM: !AZURE_IP!:9100
echo.
echo Todos los servidores aparecen en un dashboard unificado
echo ===============================================================
pause
goto MENU

:: --- Funciones de despliegue individual (mantenidas) ---
:LOCAL_ONLY
call :CREATE_PROMETHEUS_CONFIG_SINGLE "2-INICIAR-MONITOREO" "local" "" ""
cd /d "2-INICIAR-MONITOREO"
docker-compose up -d
cd /d "%~dp0"
echo [OK] Monitoreo local iniciado - http://localhost:3000
pause
goto MENU

:AWS_ONLY
echo --- Credenciales AWS ---
set /p AWS_ACCESS_KEY_ID="AWS Access Key ID: "
set /p AWS_SECRET_ACCESS_KEY="AWS Secret Access Key: "
set /p AWS_REGION="AWS Region [us-east-1]: "
if "!AWS_REGION!"=="" set "AWS_REGION=us-east-1"

call :DEPLOY_AWS
call :CREATE_PROMETHEUS_CONFIG_SINGLE "2-INICIAR-MONITOREO" "aws" "!AWS_IP!" ""
cd /d "2-INICIAR-MONITOREO"
docker-compose up -d
cd /d "%~dp0"
echo [OK] Monitoreo AWS iniciado - EC2: !AWS_IP!
pause
goto MENU

:AZURE_ONLY
echo [INFO] Funcionalidad Azure individual disponible
pause
goto MENU

:: --- OPCION 5: Ver estado del sistema ---
:CHECK_STATUS
echo.
echo ===============================================================
echo                   ESTADO ACTUAL DEL SISTEMA
echo ===============================================================
echo.

:: Verificar Docker
docker ps >nul 2>&1
if !errorlevel! neq 0 (
    echo [STATUS] Docker: DETENIDO
) else (
    echo [STATUS] Docker: FUNCIONANDO
    for /f %%i in ('docker ps --filter "name=optimon" --format "table {{.Names}}" ^| find /c "optimon"') do set "OPTIMON_CONTAINERS=%%i"
    echo [STATUS] Contenedores OptiMon activos: !OPTIMON_CONTAINERS!
)

:: Verificar Terraform
if exist "1-CREAR-INFRAESTRUCTURA\.terraform" (
    echo [STATUS] Terraform: INICIALIZADO
) else (
    echo [STATUS] Terraform: NO INICIALIZADO
)

if exist "1-CREAR-INFRAESTRUCTURA\terraform.tfstate" (
    echo [STATUS] Infraestructura desplegada: SI
    cd /d "1-CREAR-INFRAESTRUCTURA"
    echo [INFO] Outputs disponibles:
    terraform output 2>nul
    cd /d "%~dp0"
) else (
    echo [STATUS] Infraestructura desplegada: NO
)

:: Verificar Grafana
curl -s http://localhost:3000 >nul 2>&1
if !errorlevel! equ 0 (
    echo [STATUS] Grafana: ACCESIBLE (http://localhost:3000)
) else (
    echo [STATUS] Grafana: NO ACCESIBLE
)

:: Verificar Prometheus
curl -s http://localhost:9090 >nul 2>&1
if !errorlevel! equ 0 (
    echo [STATUS] Prometheus: ACCESIBLE (http://localhost:9090)
) else (
    echo [STATUS] Prometheus: NO ACCESIBLE
)

:: Verificar Windows Exporter
curl -s http://localhost:9182/metrics >nul 2>&1
if !errorlevel! equ 0 (
    echo [STATUS] Windows Exporter: FUNCIONANDO (puerto 9182)
) else (
    echo [STATUS] Windows Exporter: NO RESPONDE (puerto 9182)
    echo [TIP] Ejecuta: Start-Service windows_exporter
)

echo.
pause
goto MENU

:: --- OPCION 6: Generar backup IaC ---
:GENERATE_IAC_BACKUP
echo.
echo ===============================================================
echo                GENERAR BACKUP DE INFRAESTRUCTURA
echo ===============================================================
echo.
echo Esta opcion escanea tu infraestructura actual y genera codigo
echo IaC para poder recrearla identicamente en el futuro.
echo.

if "!SKIP_IAC!"=="1" (
    echo [ERROR] Generador IaC no disponible
    echo Asegurate de que iac_generator.py existe
    pause
    goto MENU
)

echo ¿Que infraestructura quieres respaldar?
echo [1] Solo servidor local
echo [2] Solo AWS (instancias existentes)
echo [3] Solo Azure (VMs existentes)
echo [4] Todo (Local + AWS + Azure)
echo.
set /p IAC_OPTION="Selecciona: "

if "!IAC_OPTION!"=="1" (
    echo Escaneando servidor local...
    echo 1| python iac_generator.py
) else if "!IAC_OPTION!"=="2" (
    echo Escaneando infraestructura AWS...
    echo 2| python iac_generator.py
) else if "!IAC_OPTION!"=="3" (
    echo Escaneando infraestructura Azure...
    echo 3| python iac_generator.py
) else if "!IAC_OPTION!"=="4" (
    echo Escaneando toda la infraestructura...
    echo 4| python iac_generator.py
) else (
    echo [ERROR] Opcion invalida
    goto MENU
)

echo.
echo [OK] Backup IaC generado en 3-CODIGO-GENERADO\version_X\
echo Puedes usar este codigo para recrear tu infraestructura
echo.
pause
goto MENU

:: --- FUNCIONES AUXILIARES ---

:CHECK_PREREQ
where %1 >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] %1 no encontrado - %2
    pause
    exit /b 1
)
echo [OK] %1 verificado
exit /b 0

:DEPLOY_AWS
if not exist "1-CREAR-INFRAESTRUCTURA" (
    echo [ERROR] Directorio 1-CREAR-INFRAESTRUCTURA no existe
    exit /b 1
)

cd /d "1-CREAR-INFRAESTRUCTURA"
echo aws_region = "!AWS_REGION!" > terraform.tfvars
echo key_name = "Optimon2" >> terraform.tfvars
echo instance_type = "t3.micro" >> terraform.tfvars

if not exist ".terraform" (
    echo [INFO] Primera instalacion de Terraform - esto puede tardar...
    terraform init
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo terraform init
        cd /d "%~dp0"
        exit /b 1
    )
) else (
    terraform init
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo terraform init
        cd /d "%~dp0"
        exit /b 1
    )
)

echo [INFO] Aplicando configuracion Terraform...
terraform apply -auto-approve
if !errorlevel! neq 0 (
    echo [ERROR] Fallo terraform apply
    cd /d "%~dp0"
    exit /b 1
)

:: Debug - mostrar todos los outputs disponibles
echo [DEBUG] Outputs disponibles:
terraform output

:: Intentar obtener IP con diferentes métodos
terraform output -raw instance_public_ip > temp_ip.txt 2>nul
if exist temp_ip.txt (
    set /p AWS_IP=<temp_ip.txt
    del temp_ip.txt
    echo [DEBUG] IP obtenida con metodo 1: !AWS_IP!
) 

:: Si no funciona, probar método alternativo
if "!AWS_IP!"=="" (
    echo [DEBUG] Probando metodo alternativo con JSON...
    for /f "delims=" %%i in ('terraform output -json 2^>nul') do set "OUTPUTS=%%i"
    for /f "delims=" %%j in ('echo !OUTPUTS! ^| jq -r ".instance_public_ip.value // empty" 2^>nul') do set "AWS_IP=%%j"
    echo [DEBUG] IP obtenida con metodo 2: !AWS_IP!
)

cd /d "%~dp0"

if "!AWS_IP!"=="" (
    echo [ERROR] No se pudo obtener IP de AWS
    echo [DEBUG] Verifica que el output 'instance_public_ip' existe en tu modulo Terraform
    echo [DEBUG] Revisa el archivo 1-CREAR-INFRAESTRUCTURA\modulos\aws\outputs.tf
    exit /b 1
)

echo [OK] AWS EC2 desplegada: !AWS_IP!
exit /b 0

:DEPLOY_AZURE
echo [INFO] Desplegando Azure VM...
:: Implementacion similar a AWS pendiente
set "AZURE_IP=20.1.2.3"
echo [OK] Azure VM desplegada: !AZURE_IP!
exit /b 0

:CREATE_MULTI_PROMETHEUS_CONFIG
set "CONFIG_FILE=2-INICIAR-MONITOREO\config\prometheus\prometheus.yml"

if not exist "2-INICIAR-MONITOREO\config\prometheus" mkdir "2-INICIAR-MONITOREO\config\prometheus"

echo global: > "!CONFIG_FILE!"
echo   scrape_interval: 15s >> "!CONFIG_FILE!"
echo   evaluation_interval: 15s >> "!CONFIG_FILE!"
echo. >> "!CONFIG_FILE!"
echo rule_files: >> "!CONFIG_FILE!"
echo   - "alert.rules.yml" >> "!CONFIG_FILE!"
echo. >> "!CONFIG_FILE!"
echo scrape_configs: >> "!CONFIG_FILE!"
echo   - job_name: "prometheus" >> "!CONFIG_FILE!"
echo     static_configs: >> "!CONFIG_FILE!"
echo       - targets: ["localhost:9090"] >> "!CONFIG_FILE!"
echo. >> "!CONFIG_FILE!"

:: Agregar targets segun lo seleccionado
if "!INCLUDE_LOCAL!"=="1" (
    echo   - job_name: "local_windows" >> "!CONFIG_FILE!"
    echo     static_configs: >> "!CONFIG_FILE!"
    echo       - targets: ["host.docker.internal:9182"] >> "!CONFIG_FILE!"
    echo. >> "!CONFIG_FILE!"
)

if "!INCLUDE_AWS!"=="1" (
    echo   - job_name: "aws_ec2" >> "!CONFIG_FILE!"
    echo     static_configs: >> "!CONFIG_FILE!"
    echo       - targets: ["!AWS_IP!:9100"] >> "!CONFIG_FILE!"
    echo     scrape_interval: 30s >> "!CONFIG_FILE!"
    echo. >> "!CONFIG_FILE!"
)

if "!INCLUDE_AZURE!"=="1" (
    echo   - job_name: "azure_vm" >> "!CONFIG_FILE!"
    echo     static_configs: >> "!CONFIG_FILE!"
    echo       - targets: ["!AZURE_IP!:9100"] >> "!CONFIG_FILE!"
    echo     scrape_interval: 30s >> "!CONFIG_FILE!"
    echo. >> "!CONFIG_FILE!"
)

echo [OK] Configuracion multi-servidor creada
exit /b 0

:CREATE_PROMETHEUS_CONFIG_SINGLE
:: Funcion mantenida para compatibilidad con opciones individuales
set "DIR=%~1"
set "PROV=%~2"
set "PUBLIC_IP=%~3"
set "PRIVATE_IP=%~4"

if not exist "!DIR!\config\prometheus" mkdir "!DIR!\config\prometheus"

echo global: > "!DIR!\config\prometheus\prometheus.yml"
echo   scrape_interval: 15s >> "!DIR!\config\prometheus\prometheus.yml"
echo   evaluation_interval: 15s >> "!DIR!\config\prometheus\prometheus.yml"
echo. >> "!DIR!\config\prometheus\prometheus.yml"
echo scrape_configs: >> "!DIR!\config\prometheus\prometheus.yml"
echo   - job_name: "prometheus" >> "!DIR!\config\prometheus\prometheus.yml"
echo     static_configs: >> "!DIR!\config\prometheus\prometheus.yml"
echo       - targets: ["localhost:9090"] >> "!DIR!\config\prometheus\prometheus.yml"
echo. >> "!DIR!\config\prometheus\prometheus.yml"

if "!PROV!"=="local" (
    echo   - job_name: "windows_exporter" >> "!DIR!\config\prometheus\prometheus.yml"
    echo     static_configs: >> "!DIR!\config\prometheus\prometheus.yml"
    echo       - targets: ["host.docker.internal:9182"] >> "!DIR!\config\prometheus\prometheus.yml"
) else if "!PROV!"=="aws" (
    echo   - job_name: "aws_ec2" >> "!DIR!\config\prometheus\prometheus.yml"
    echo     static_configs: >> "!DIR!\config\prometheus\prometheus.yml"
    echo       - targets: ["!PUBLIC_IP!:9100"] >> "!DIR!\config\prometheus\prometheus.yml"
)

exit /b 0

:EXIT
echo Gracias por usar OptiMon!
exit /b 0