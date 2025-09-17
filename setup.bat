@echo off
title OptiMon Multi-Cloud Setup with IaC Generation
chcp 65001 >nul

:: Habilitar expansion tardía de variables
setlocal EnableDelayedExpansion

cls
echo ---
echo --- BIENVENIDO A LA CONFIGURACION DEL PRODUCTO OPTIMON ---
echo ---
echo Este script te guiara para desplegar y monitorear tu infraestructura.
echo Soporta: Servidores Fisicos, Azure y AWS
echo NUEVO: Genera codigo IaC automaticamente basado en tu infraestructura
echo.

:: --- FASE 0: Verificar prerrequisitos ---
echo Verificando prerrequisitos...
echo.

where jq >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] El comando 'jq' no se encuentra.
    echo Por favor, instala jq para Windows y asegurese de que este en el PATH.
    echo Puedes descargarlo desde: https://jqlang.github.io/jq/download/
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 1
)

where docker-compose >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] docker-compose no se encuentra en el PATH.
    echo Instala Docker Desktop y asegurate de que docker-compose este disponible.
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 1
)

where python >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python no se encuentra en el PATH.
    echo El generador de IaC requiere Python 3.7+
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 1
)

:: Verificar que el generador IaC existe
if not exist "iac_generator.py" (
    echo [WARNING] No se encuentra el generador de IaC (iac_generator.py)
    echo El monitoreo continuara sin generacion automatica de IaC
    echo Directorio actual: %cd%
    echo.
    set "SKIP_IAC=1"
) else (
    set "SKIP_IAC=0"
)

echo [OK] Prerrequisitos verificados correctamente
echo.

:: --- FASE 1: Seleccionar tipo de infraestructura ---
:MENU
echo Selecciona el tipo de infraestructura a escanear:
echo [1] Servidor fisico (este equipo)
echo [2] Servidores en la nube (Azure)
echo [3] Servidores en la nube (AWS)
echo [0] Salir
echo.
set /p OPTION="Opcion (1-3, 0 para salir): "
echo.

if "!OPTION!"=="0" goto SALIR
if "!OPTION!"=="1" goto FISICO
if "!OPTION!"=="2" goto AZURE
if "!OPTION!"=="3" goto AWS

echo [ERROR] Opcion invalida. Por favor selecciona 1, 2, 3 o 0.
echo.
goto MENU

:: --- FASE 2A: Configuracion para servidor fisico ---
:FISICO
echo.
echo Configurando monitoreo del servidor local...
set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=local"

:: Verificar que el directorio existe
if not exist "!MONITORING_DIR!" (
    echo [ERROR] Directorio !MONITORING_DIR! no existe.
    echo Directorio actual: %cd%
    echo Verifica la estructura de carpetas del proyecto.
    echo.
    call :PAUSE_SAFE
    goto MENU
)

if not exist "!MONITORING_DIR!\config" (
    echo [INFO] Creando directorio config...
    mkdir "!MONITORING_DIR!\config" 2>nul
)

if not exist "!MONITORING_DIR!\config\prometheus" (
    echo [INFO] Creando directorio prometheus...
    mkdir "!MONITORING_DIR!\config\prometheus" 2>nul
)

:: Crear prometheus.yml para localhost
call :CREATE_PROMETHEUS_CONFIG "!MONITORING_DIR!" "local" "" ""
if !errorlevel! neq 0 (
    echo [ERROR] Fallo al crear configuracion de Prometheus
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo [OK] Configuracion de Prometheus creada para servidor local
echo [OK] Dashboard OptiMon ya esta configurado
echo [OK] Alertas personalizables disponibles en: !MONITORING_DIR!\config\prometheus\alert.rules.yml
echo.

echo Iniciando Prometheus y Grafana...
if exist "!MONITORING_DIR!\docker-compose.yml" (
    cd /d "!MONITORING_DIR!"
    echo Ejecutando docker-compose up -d...
    docker-compose up -d 2>&1
    set "DOCKER_RESULT=!errorlevel!"
    cd /d "%~dp0"
    
    if !DOCKER_RESULT! neq 0 (
        echo [ERROR] Fallo al iniciar docker-compose
        echo Verifica que Docker Desktop este ejecutandose
        echo.
        call :PAUSE_SAFE
        goto MENU
    )
) else (
    echo [ERROR] No se encuentra docker-compose.yml en !MONITORING_DIR!
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo.
echo Esperando 30 segundos a que los servicios se inicialicen...
timeout /t 30 /nobreak >nul

if "!SKIP_IAC!"=="0" (
    echo.
    echo === GENERANDO CODIGO IaC AUTOMATICAMENTE ===
    echo Escaneando infraestructura local y generando Terraform/Ansible...
    echo.

    :: Ejecutar el generador IaC para local con manejo de errores
    echo 1| python iac_generator.py 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] El generador IaC encontro algunos problemas, pero el monitoreo continua...
    )
)

echo.
echo ---------------------------------------------------------
echo Monitoreo del servidor local iniciado!
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo Prometheus: http://localhost:9090
echo.
if "!SKIP_IAC!"=="0" (
    echo CODIGO IaC GENERADO:
    echo - Revisa la carpeta 3-CODIGO-GENERADO\version_X\
    echo - Contiene: Terraform, Ansible y reporte de infraestructura
)
echo ---------------------------------------------------------
echo.
goto FIN

:: --- FASE 2B: Configuracion para servidores Azure ---
:AZURE
echo Por favor, introduce tus credenciales de Azure (Service Principal):
set /p AZURE_CLIENT_ID="Azure Client ID: "
if "!AZURE_CLIENT_ID!"=="" (
    echo [ERROR] Client ID no puede estar vacio
    goto MENU
)

set /p AZURE_CLIENT_SECRET="Azure Client Secret: "
if "!AZURE_CLIENT_SECRET!"=="" (
    echo [ERROR] Client Secret no puede estar vacio
    goto MENU
)

set /p AZURE_TENANT_ID="Azure Tenant ID: "
if "!AZURE_TENANT_ID!"=="" (
    echo [ERROR] Tenant ID no puede estar vacio
    goto MENU
)

set /p AZURE_SUBSCRIPTION_ID="Azure Subscription ID: "
if "!AZURE_SUBSCRIPTION_ID!"=="" (
    echo [ERROR] Subscription ID no puede estar vacio
    goto MENU
)

echo.
echo NOTA: La contrasena de la VM sera visible mientras la escribes.
set /p VM_PASSWORD="Crea una contrasena para la nueva Maquina Virtual: "
if "!VM_PASSWORD!"=="" (
    echo [ERROR] La contrasena no puede estar vacia
    goto MENU
)
echo.

:: Verificar directorio de infraestructura
if not exist "1-CREAR-INFRAESTRUCTURA" (
    echo [ERROR] Directorio 1-CREAR-INFRAESTRUCTURA no existe
    echo Directorio actual: %cd%
    echo.
    call :PAUSE_SAFE
    goto MENU
)

cd /d "1-CREAR-INFRAESTRUCTURA"

:: Asegurar que usamos el provider de Azure
if exist "provider-azure.tf" (
    copy /y "provider-azure.tf" "provider.tf" >nul
) else (
    echo [ERROR] No se encuentra provider-azure.tf
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo vm_password = "!VM_PASSWORD!" > terraform.tfvars

echo Ejecutando terraform init...
terraform init -upgrade 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Fallo terraform init
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo Ejecutando terraform apply...
terraform apply -auto-approve 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Fallo terraform apply
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

:: Obtener outputs de terraform de forma mas robusta
terraform output -json > terraform_outputs.json 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] No se pudieron obtener los outputs de terraform
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

for /f "delims=" %%j in ('jq -r ".vm_private_ip.value // empty" terraform_outputs.json 2^>nul') do set "VM_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('jq -r ".vm_public_ip.value // empty" terraform_outputs.json 2^>nul') do set "VM_PUBLIC_IP=%%k"

if "!VM_PUBLIC_IP!"=="" (
    echo [ERROR] No se pudo obtener la IP publica de la VM
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo [OK] VM Azure desplegada - IP: !VM_PUBLIC_IP!
del terraform_outputs.json 2>nul
cd /d "%~dp0"

set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=azure"

:: Crear prometheus.yml para Azure VM
call :CREATE_PROMETHEUS_CONFIG "!MONITORING_DIR!" "azure" "!VM_PUBLIC_IP!" "!VM_PRIVATE_IP!"

if exist "!MONITORING_DIR!\docker-compose.yml" (
    cd /d "!MONITORING_DIR!"
    docker-compose up -d 2>&1
    cd /d "%~dp0"
) else (
    echo [ERROR] No se encuentra docker-compose.yml en !MONITORING_DIR!
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo.
echo Esperando 45 segundos a que Azure VM y servicios se inicialicen...
timeout /t 45 /nobreak >nul

if "!SKIP_IAC!"=="0" (
    echo.
    echo === GENERANDO CODIGO IaC AUTOMATICAMENTE ===
    echo Escaneando infraestructura Azure + Local y generando Terraform/Ansible...
    echo.

    :: Ejecutar el generador IaC para Azure + Local
    echo 3| python iac_generator.py 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] El generador IaC encontro algunos problemas, pero continua...
    )
)

echo.
echo ---------------------------------------------------------
echo Infraestructura Azure desplegada!
echo IP Publica VM: !VM_PUBLIC_IP!
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo.
if "!SKIP_IAC!"=="0" (
    echo CODIGO IaC GENERADO:
    echo - Revisa la carpeta 3-CODIGO-GENERADO\version_X\
    echo - Contiene: Terraform para replicar Azure VM + Local
    echo - Playbooks Ansible para configuracion automatica
)
echo ---------------------------------------------------------
echo.
goto FIN

:: --- FASE 2C: Configuracion para servidores AWS ---
:AWS
echo Por favor, introduce tus credenciales de AWS:
set /p AWS_ACCESS_KEY_ID="AWS Access Key ID: "
if "!AWS_ACCESS_KEY_ID!"=="" (
    echo [ERROR] Access Key ID no puede estar vacio
    goto MENU
)

set /p AWS_SECRET_ACCESS_KEY="AWS Secret Access Key: "
if "!AWS_SECRET_ACCESS_KEY!"=="" (
    echo [ERROR] Secret Access Key no puede estar vacio
    goto MENU
)

set /p AWS_REGION="AWS Region (ej: us-east-1): "
if "!AWS_REGION!"=="" set "AWS_REGION=us-east-1"

echo.
echo NOTA: Se creara un Key Pair para acceso SSH.
set /p KEY_NAME="Nombre para el Key Pair (ej: optimon-key): "
if "!KEY_NAME!"=="" set "KEY_NAME=optimon-key"
echo.

if not exist "1-CREAR-INFRAESTRUCTURA" (
    echo [ERROR] Directorio 1-CREAR-INFRAESTRUCTURA no existe
    echo.
    call :PAUSE_SAFE
    goto MENU
)

cd /d "1-CREAR-INFRAESTRUCTURA"

:: Crear terraform.tfvars para AWS con t3.micro
echo aws_region = "!AWS_REGION!" > terraform.tfvars
echo key_name = "!KEY_NAME!" >> terraform.tfvars
echo instance_type = "t3.micro" >> terraform.tfvars

echo Ejecutando terraform init...
terraform init -upgrade 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Fallo terraform init
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo Ejecutando terraform apply...
terraform apply -auto-approve 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Fallo terraform apply
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

for /f "delims=" %%j in ('terraform output -raw instance_private_ip 2^>nul') do set "INSTANCE_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('terraform output -raw instance_public_ip 2^>nul') do set "INSTANCE_PUBLIC_IP=%%k"

if "!INSTANCE_PUBLIC_IP!"=="" (
    echo [ERROR] No se pudo obtener la IP publica de la instancia EC2
    cd /d "%~dp0"
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo [OK] Instancia EC2 desplegada - IP: !INSTANCE_PUBLIC_IP!
cd /d "%~dp0"

set "MONITORING_DIR=2-INICIAR-MONITOREO"
set "PROVIDER=aws"

:: Crear prometheus.yml para AWS EC2
call :CREATE_PROMETHEUS_CONFIG "!MONITORING_DIR!" "aws" "!INSTANCE_PUBLIC_IP!" "!INSTANCE_PRIVATE_IP!"

if exist "!MONITORING_DIR!\docker-compose.yml" (
    cd /d "!MONITORING_DIR!"
    docker-compose up -d 2>&1
    cd /d "%~dp0"
) else (
    echo [ERROR] No se encuentra docker-compose.yml en !MONITORING_DIR!
    echo.
    call :PAUSE_SAFE
    goto MENU
)

echo.
echo Esperando 45 segundos a que AWS EC2 y servicios se inicialicen...
timeout /t 45 /nobreak >nul

if "!SKIP_IAC!"=="0" (
    echo.
    echo === GENERANDO CODIGO IaC AUTOMATICAMENTE ===
    echo Escaneando infraestructura AWS + Local y generando Terraform/Ansible...
    echo.

    :: Ejecutar el generador IaC para AWS + Local
    echo 2| python iac_generator.py 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] El generador IaC encontro algunos problemas, pero continua...
    )
)

echo.
echo ---------------------------------------------------------
echo Infraestructura AWS desplegada!
echo IP Publica EC2: !INSTANCE_PUBLIC_IP!
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo IMPORTANTE: Descarga la clave privada desde la consola AWS
echo.
if "!SKIP_IAC!"=="0" (
    echo CODIGO IaC GENERADO:
    echo - Revisa la carpeta 3-CODIGO-GENERADO\version_X\
    echo - Contiene: Terraform para replicar EC2 + Local
    echo - Playbooks Ansible para configuracion automatica
)
echo ---------------------------------------------------------
echo.
goto FIN

:: --- FUNCION: Pausa segura ---
:PAUSE_SAFE
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
echo.
exit /b 0

:: --- FUNCION: Crear configuracion de Prometheus ---
:CREATE_PROMETHEUS_CONFIG
set "DIR=%~1"
set "PROV=%~2"
set "PUBLIC_IP=%~3"
set "PRIVATE_IP=%~4"

echo [INFO] Creando configuracion de Prometheus para !PROV!...

if not exist "!DIR!\config\prometheus" (
    mkdir "!DIR!\config\prometheus" 2>nul
)

(
echo global:
echo   scrape_interval: 15s
echo   evaluation_interval: 15s
echo.
echo rule_files:
echo   - "alert.rules.yml"
echo.
echo alerting:
echo   alertmanagers:
echo     - static_configs:
echo         - targets: []
echo.
echo scrape_configs:
echo   - job_name: "prometheus"
echo     static_configs:
echo       - targets: ["localhost:9090"]
echo.
) > "!DIR!\config\prometheus\prometheus.yml"

if "!PROV!"=="local" (
    (
    echo   - job_name: "windows_exporter"
    echo     static_configs:
    echo       - targets: ["host.docker.internal:9182"]
    ) >> "!DIR!\config\prometheus\prometheus.yml"
) else if "!PROV!"=="azure" (
    (
    echo   - job_name: "azure_vm"
    echo     static_configs:
    echo       - targets: ["!PUBLIC_IP!:9100"]
    echo     scrape_interval: 30s
    echo     scrape_timeout: 10s
    ) >> "!DIR!\config\prometheus\prometheus.yml"
) else if "!PROV!"=="aws" (
    (
    echo   - job_name: "aws_ec2"
    echo     static_configs:
    echo       - targets: ["!PUBLIC_IP!:9100"]
    echo     scrape_interval: 30s
    echo     scrape_timeout: 10s
    ) >> "!DIR!\config\prometheus\prometheus.yml"
)

:: Crear archivo de reglas de alertas basico si no existe (SIN caracteres problematicos)
if not exist "!DIR!\config\prometheus\alert.rules.yml" (
    (
    echo groups:
    echo   - name: optimon_alerts
    echo     rules:
    echo       - alert: HighCPUUsage
    echo         expr: 100 - avg^(rate^(windows_cpu_time_total{mode="idle"}[2m]^)^) * 100 ^> 80
    echo         for: 2m
    echo         labels:
    echo           severity: warning
    echo         annotations:
    echo           summary: "High CPU usage detected"
    echo           description: "CPU usage is above 80%% for more than 2 minutes"
    echo.
    echo       - alert: HighMemoryUsage  
    echo         expr: ^(windows_os_physical_memory_free_bytes / windows_cs_physical_memory_bytes^) * 100 ^< 20
    echo         for: 5m
    echo         labels:
    echo           severity: critical
    echo         annotations:
    echo           summary: "High memory usage detected"
    echo           description: "Memory usage is above 80%% for more than 5 minutes"
    ) > "!DIR!\config\prometheus\alert.rules.yml"
)

echo [OK] Configuracion de Prometheus creada exitosamente
exit /b 0

:FIN
echo.
echo Proceso completado!
echo.
echo === RESUMEN DE LO DESPLEGADO ===
echo Accede a tu dashboard OptiMon en:
echo    http://localhost:3000
echo    Usuario: admin / Contrasena: admin
echo.
echo Para editar alertas:
echo    Archivo: !MONITORING_DIR!\config\prometheus\alert.rules.yml
echo    Reinicia con: docker-compose restart prometheus
echo.
if "!SKIP_IAC!"=="0" (
    echo === CODIGO IaC GENERADO ===
    echo El sistema ha escaneado tu infraestructura y generado:
    echo 1. Codigo Terraform para replicar la infraestructura
    echo 2. Playbooks Ansible para configuracion automatica
    echo 3. Reporte detallado de recursos detectados
    echo.
    echo Ubicacion: 3-CODIGO-GENERADO\version_X\
    echo - terraform\ ^(codigo para replicar infraestructura^)
    echo - ansible\ ^(configuracion automatizada^)  
    echo - README.md ^(instrucciones de uso^)
    echo - scan_results.json ^(datos completos del escaneo^)
    echo.
)
if "!PROVIDER!"=="aws" (
    echo RECORDATORIO AWS:
    echo - Instancia: t3.micro ^(Free Tier^)
    echo - Descargar clave privada desde AWS Console
    echo - Acceso SSH: ssh -i !KEY_NAME!.pem ec2-user@!INSTANCE_PUBLIC_IP!
    echo.
)
if "!PROVIDER!"=="azure" (
    echo RECORDATORIO AZURE:
    echo - VM: Standard_B1s ^(Free Tier^)
    echo - Acceso SSH: ssh azureuser@!VM_PUBLIC_IP!
    echo.
)
echo === PROXIMOS PASOS ===
echo 1. Verifica el dashboard en http://localhost:3000
if "!SKIP_IAC!"=="0" (
    echo 2. Revisa el codigo IaC generado en 3-CODIGO-GENERADO\
    echo 3. Usa 'terraform plan' para validar antes de aplicar
    echo 4. Los playbooks Ansible configuran monitoreo automaticamente
)
echo.
echo Tu sistema de monitoreo multi-cloud esta listo!
echo.
call :PAUSE_SAFE
goto SALIR

:SALIR
echo.
echo Gracias por usar OptiMon!
echo.
exit /b 0