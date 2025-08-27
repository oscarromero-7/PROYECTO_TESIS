@echo off
title OptiMon Product Setup

cls
echo ---
echo --- BIENVENIDO A LA CONFIGURACION DEL PRODUCTO OPTIMON ---
echo ---
echo Este script te guiara para desplegar y monitorear tu infraestructura.
echo.

:: --- FASE 0: Verificar prerrequisitos (jq) ---
where jq >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] El comando 'jq' no se encuentra.
    echo Por favor, instala jq para Windows y asegurese de que este en el PATH.
    echo Puedes descargarlo desde: https://jqlang.github.io/jq/download/
    pause
    exit /b 1
)

:: --- FASE 1: Recolectar todas las credenciales del usuario ---
echo Por favor, introduce tus credenciales de Azure (Service Principal):
set /p AZURE_CLIENT_ID="Azure Client ID: "
set /p AZURE_CLIENT_SECRET="Azure Client Secret: "
set /p AZURE_TENANT_ID="Azure Tenant ID: "
set /p AZURE_SUBSCRIPTION_ID="Azure Subscription ID: "
echo.
echo NOTA: La contrasena de la VM sera visible mientras la escribes.
set /p VM_PASSWORD="Crea una contrasena para la nueva Maquina Virtual: "
echo.
echo Gracias! Todas las credenciales han sido recibidas.
echo.

:: --- FASE 2: Crear infraestructura con Terraform ---
echo.
echo ??? Iniciando la creacion de la infraestructura en Azure con Terraform...
echo Esto puede tardar varios minutos.
echo.

cd 1-CREAR-INFRAESTRUCTURA

:: Crear el archivo terraform.tfvars automáticamente
(echo vm_password = "%VM_PASSWORD%") > terraform.tfvars

:: Inicializar y aplicar los cambios de Terraform
terraform init -upgrade
terraform apply -auto-approve

:: Capturar las salidas de Terraform en formato JSON y extraer las IPs
echo.
echo ? Infraestructura creada. Obteniendo IPs...
for /f "delims=" %%i in ('terraform output -json') do set "OUTPUTS=%%i"
for /f "delims=" %%j in ('echo %OUTPUTS% ^| jq -r ".vm_private_ip.value"') do set "VM_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('echo %OUTPUTS% ^| jq -r ".vm_public_ip.value"') do set "VM_PUBLIC_IP=%%k"

cd ..

:: --- FASE 3: Configurar el entorno de monitoreo automáticamente ---
echo.
echo ???  Configurando el entorno de monitoreo...
set "MONITORING_DIR=2-INICIAR-MONITOREO"

:: Crear el archivo .env automáticamente
(
    echo # Credenciales de AWS (dejar en blanco si no se usa)
    echo AWS_ACCESS_KEY_ID=
    echo AWS_SECRET_ACCESS_KEY=
    echo.
    echo # Credenciales de Azure
    echo AZURE_CLIENT_ID=%AZURE_CLIENT_ID%
    echo AZURE_CLIENT_SECRET=%AZURE_CLIENT_SECRET%
    echo AZURE_TENANT_ID=%AZURE_TENANT_ID%
    echo AZURE_SUBSCRIPTION_ID=%AZURE_SUBSCRIPTION_ID%
) > %MONITORING_DIR%\.env

:: Crear el archivo prometheus.yml automáticamente
(
    echo global:
    echo   scrape_interval: 15s
    echo.
    echo rule_files:
    echo   - "/etc/prometheus/alert.rules.yml"
    echo.
    echo scrape_configs:
    echo   - job_name: "prometheus"
    echo     static_configs:
    echo       - targets: ["localhost:9090"]
    echo.
    echo   - job_name: "azure_vm"
    echo     static_configs:
      - targets: ["%VM_PRIVATE_IP%:9100"]
) > %MONITORING_DIR%\config\prometheus\prometheus.yml

:: --- FASE 4: Iniciar la pila de monitoreo ---
echo.
echo ??? Iniciando los servicios de monitoreo con Docker...
cd %MONITORING_DIR%
docker-compose up -d

echo.
echo ---------------------------------------------------------
echo ? !PROCESO COMPLETADO!
echo ---------------------------------------------------------
echo Tu infraestructura esta corriendo en Azure.
echo   -^> IP Publica de la VM (para SSH): %VM_PUBLIC_IP%
echo.
echo Tu panel de monitoreo esta disponible en:
echo   -^> http://localhost:3000
echo       (Usuario/Contrasena: admin/admin)
echo ---------------------------------------------------------
echo.
pause