@echo off
title OptiMon Multi-Cloud Setup
chcp 65001 >nul

cls
echo ---
echo --- BIENVENIDO A LA CONFIGURACION DEL PRODUCTO OPTIMON ---
echo ---
echo Este script te guiara para desplegar y monitorear tu infraestructura.
echo Soporta: Servidores Fisicos, Azure y AWS
echo.

:: --- FASE 0: Verificar prerrequisitos ---
where jq >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] El comando 'jq' no se encuentra.
    echo Por favor, instala jq para Windows y asegurese de que este en el PATH.
    echo Puedes descargarlo desde: https://jqlang.github.io/jq/download/
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] docker-compose no se encuentra en el PATH.
    echo Instala Docker Desktop y asegurate de que docker-compose este disponible.
    pause
    exit /b 1
)

:: --- FASE 1: Seleccionar tipo de infraestructura ---
echo Selecciona el tipo de infraestructura a escanear:
echo [1] Servidor fisico (este equipo)
echo [2] Servidores en la nube (Azure)
echo [3] Servidores en la nube (AWS)
set /p OPTION="Opcion: "
echo.

if "%OPTION%"=="1" goto FISICO
if "%OPTION%"=="2" goto AZURE
if "%OPTION%"=="3" goto AWS
echo Opcion invalida.
pause
exit /b 1

:: --- FASE 2A: Configuracion para servidor fisico ---
:FISICO
echo.
echo Configurando monitoreo del servidor local...
set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=local"

:: Verificar que el directorio existe
if not exist "%MONITORING_DIR%\config\prometheus" (
    echo [ERROR] Directorio %MONITORING_DIR%\config\prometheus no existe.
    echo Verifica la estructura de carpetas del proyecto.
    pause
    exit /b 1
)

:: Crear prometheus.yml para localhost
call :CREATE_PROMETHEUS_CONFIG "%MONITORING_DIR%" "local" "" ""

echo [OK] Configuracion de Prometheus creada para servidor local
echo [OK] Dashboard OptiMon ya esta configurado
echo [OK] Alertas personalizables disponibles en: %MONITORING_DIR%\config\prometheus\alert.rules.yml
echo.
echo Iniciando Prometheus y Grafana...
cd "%MONITORING_DIR%"
docker-compose up -d

echo.
echo ---------------------------------------------------------
echo Monitoreo del servidor local iniciado!
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo Prometheus: http://localhost:9090
echo ---------------------------------------------------------
echo.
goto FIN

:: --- FASE 2B: Configuracion para servidores Azure ---
:AZURE
echo Por favor, introduce tus credenciales de Azure (Service Principal):
set /p AZURE_CLIENT_ID="Azure Client ID: "
set /p AZURE_CLIENT_SECRET="Azure Client Secret: "
set /p AZURE_TENANT_ID="Azure Tenant ID: "
set /p AZURE_SUBSCRIPTION_ID="Azure Subscription ID: "
echo.
echo NOTA: La contrasena de la VM sera visible mientras la escribes.
set /p VM_PASSWORD="Crea una contrasena para la nueva Maquina Virtual: "
echo.

:: Configurar variables de entorno para Azure
set AZURE_CLIENT_ID=%AZURE_CLIENT_ID%
set AZURE_CLIENT_SECRET=%AZURE_CLIENT_SECRET%
set AZURE_TENANT_ID=%AZURE_TENANT_ID%
set AZURE_SUBSCRIPTION_ID=%AZURE_SUBSCRIPTION_ID%

cd 1-CREAR-INFRAESTRUCTURA

:: Asegurar que usamos el provider de Azure
copy /y provider-azure.tf provider.tf

echo vm_password = "%VM_PASSWORD%" > terraform.tfvars
terraform init -upgrade
terraform apply -auto-approve

for /f "delims=" %%i in ('terraform output -json') do set "OUTPUTS=%%i"
for /f "delims=" %%j in ('echo %OUTPUTS% ^| jq -r ".vm_private_ip.value"') do set "VM_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('echo %OUTPUTS% ^| jq -r ".vm_public_ip.value"') do set "VM_PUBLIC_IP=%%k"

cd ..

set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=azure"

:: Crear prometheus.yml para Azure VM
call :CREATE_PROMETHEUS_CONFIG "%MONITORING_DIR%" "azure" "%VM_PUBLIC_IP%" "%VM_PRIVATE_IP%"

cd "%MONITORING_DIR%"
docker-compose up -d

echo.
echo ---------------------------------------------------------
echo Infraestructura Azure desplegada!
echo IP Publica VM: %VM_PUBLIC_IP%
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo ---------------------------------------------------------
echo.
goto FIN

: --- FASE 2C: Configuracion para servidores AWS ---
:AWS
echo Por favor, introduce tus credenciales de AWS:
set /p AWS_ACCESS_KEY_ID="AWS Access Key ID: "
set /p AWS_SECRET_ACCESS_KEY="AWS Secret Access Key: "
set /p AWS_REGION="AWS Region (ej: us-east-1): "
echo.
echo NOTA: Se creara un Key Pair para acceso SSH.
set /p KEY_NAME="Nombre para el Key Pair (ej: optimon-key): "
echo.

:: NO establecer variables de entorno - usar AWS CLI configurado
:: set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
:: set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
:: set AWS_DEFAULT_REGION=%AWS_REGION%

cd 1-CREAR-INFRAESTRUCTURA

:: No copiar provider - usar el existente
:: copy /y provider-aws.tf provider.tf

:: Crear terraform.tfvars para AWS con t3.micro
echo aws_region = "%AWS_REGION%" > terraform.tfvars
echo key_name = "%KEY_NAME%" >> terraform.tfvars
echo instance_type = "t3.micro" >> terraform.tfvars

terraform init -upgrade
terraform apply -auto-approve

for /f "delims=" %%i in ('terraform output -json') do set "OUTPUTS=%%i"
for /f "delims=" %%j in ('terraform output -raw instance_private_ip') do set "INSTANCE_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('terraform output -raw instance_public_ip') do set "INSTANCE_PUBLIC_IP=%%k"

cd ..

set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=aws"

:: Crear prometheus.yml para AWS EC2
call :CREATE_PROMETHEUS_CONFIG "%MONITORING_DIR%" "aws" "%INSTANCE_PUBLIC_IP%" "%INSTANCE_PRIVATE_IP%"

cd "%MONITORING_DIR%"
docker-compose up -d

echo.
echo ---------------------------------------------------------
echo Infraestructura AWS desplegada!
echo IP Publica EC2: %INSTANCE_PUBLIC_IP%
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo IMPORTANTE: Descarga la clave privada desde la consola AWS
echo ---------------------------------------------------------
echo.
goto FIN

:: --- FUNCION: Crear configuracion de Prometheus ---
:CREATE_PROMETHEUS_CONFIG
set "DIR=%~1"
set "PROV=%~2"
set "PUBLIC_IP=%~3"
set "PRIVATE_IP=%~4"

echo global: > "%DIR%\config\prometheus\prometheus.yml"
echo   scrape_interval: 15s >> "%DIR%\config\prometheus\prometheus.yml"
echo   evaluation_interval: 15s >> "%DIR%\config\prometheus\prometheus.yml"
echo. >> "%DIR%\config\prometheus\prometheus.yml"
echo rule_files: >> "%DIR%\config\prometheus\prometheus.yml"
echo   - "alert.rules.yml" >> "%DIR%\config\prometheus\prometheus.yml"
echo. >> "%DIR%\config\prometheus\prometheus.yml"
echo alerting: >> "%DIR%\config\prometheus\prometheus.yml"
echo   alertmanagers: >> "%DIR%\config\prometheus\prometheus.yml"
echo     - static_configs: >> "%DIR%\config\prometheus\prometheus.yml"
echo         - targets: [] >> "%DIR%\config\prometheus\prometheus.yml"
echo. >> "%DIR%\config\prometheus\prometheus.yml"
echo scrape_configs: >> "%DIR%\config\prometheus\prometheus.yml"
echo   - job_name: "prometheus" >> "%DIR%\config\prometheus\prometheus.yml"
echo     static_configs: >> "%DIR%\config\prometheus\prometheus.yml"
echo       - targets: ["localhost:9090"] >> "%DIR%\config\prometheus\prometheus.yml"
echo. >> "%DIR%\config\prometheus\prometheus.yml"

if "%PROV%"=="local" (
    echo   - job_name: "windows_exporter" >> "%DIR%\config\prometheus\prometheus.yml"
    echo     static_configs: >> "%DIR%\config\prometheus\prometheus.yml"
    echo       - targets: ["host.docker.internal:9182"] >> "%DIR%\config\prometheus\prometheus.yml"
) else if "%PROV%"=="azure" (
    echo   - job_name: "azure_vm" >> "%DIR%\config\prometheus\prometheus.yml"
    echo     static_configs: >> "%DIR%\config\prometheus\prometheus.yml"
    echo       - targets: ["%PUBLIC_IP%:9100"] >> "%DIR%\config\prometheus\prometheus.yml"
    echo     scrape_interval: 30s >> "%DIR%\config\prometheus\prometheus.yml"
    echo     scrape_timeout: 10s >> "%DIR%\config\prometheus\prometheus.yml"
) else if "%PROV%"=="aws" (
    echo   - job_name: "aws_ec2" >> "%DIR%\config\prometheus\prometheus.yml"
    echo     static_configs: >> "%DIR%\config\prometheus\prometheus.yml"
    echo       - targets: ["%PUBLIC_IP%:9100"] >> "%DIR%\config\prometheus\prometheus.yml"
    echo     scrape_interval: 30s >> "%DIR%\config\prometheus\prometheus.yml"
    echo     scrape_timeout: 10s >> "%DIR%\config\prometheus\prometheus.yml"
    echo. >> "%DIR%\config\prometheus\prometheus.yml"
    echo   - job_name: "aws_cloudwatch" >> "%DIR%\config\prometheus\prometheus.yml"
    echo     ec2_sd_configs: >> "%DIR%\config\prometheus\prometheus.yml"
    echo       - region: %AWS_REGION% >> "%DIR%\config\prometheus\prometheus.yml"
    echo         port: 9100 >> "%DIR%\config\prometheus\prometheus.yml"
)

goto :eof

:FIN
echo.
echo Proceso completado!
echo.
echo Accede a tu dashboard OptiMon en:
echo    http://localhost:3000
echo    Usuario: admin / Contrasena: admin
echo.
echo Para editar alertas:
echo    Archivo: %MONITORING_DIR%\config\prometheus\alert.rules.yml
echo    Reinicia con: docker-compose restart prometheus
echo.
if "%PROVIDER%"=="aws" (
    echo RECORDATORIO AWS:
    echo - Instancia: t2.micro ^(Free Tier^)
    echo - Descargar clave privada desde AWS Console
    echo - Acceso SSH: ssh -i %KEY_NAME%.pem ec2-user@%INSTANCE_PUBLIC_IP%
    echo.
)
if "%PROVIDER%"=="azure" (
    echo RECORDATORIO AZURE:
    echo - VM: Standard_B1s ^(Free Tier^)
    echo - Acceso SSH: ssh %vm_username%@%VM_PUBLIC_IP%
    echo.
)
echo Tu sistema de monitoreo multi-cloud esta listo!
pause