@echo off
title OptiMon Product Setup
chcp 65001 >nul

cls
echo ---
echo --- BIENVENIDO A LA CONFIGURACION DEL PRODUCTO OPTIMON ---
echo ---
echo Este script te guiara para desplegar y monitorear tu infraestructura.
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
set /p OPTION="Opcion: "
echo.

if "%OPTION%"=="1" goto FISICO
if "%OPTION%"=="2" goto NUBE
echo Opcion invalida.
pause
exit /b 1

:: --- FASE 2A: Configuracion para servidor fisico ---
:FISICO
echo.
echo Configurando monitoreo del servidor local...
set "MONITORING_DIR=2-INICIAR-MONITOREO"

:: Verificar que el directorio existe
if not exist "%MONITORING_DIR%\config\prometheus" (
    echo [ERROR] Directorio %MONITORING_DIR%\config\prometheus no existe.
    echo Verifica la estructura de carpetas del proyecto.
    pause
    exit /b 1
)

:: Crear prometheus.yml para localhost
echo global: > "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   scrape_interval: 15s >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   evaluation_interval: 15s >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo rule_files: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - "alert.rules.yml" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo alerting: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   alertmanagers: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     - static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo         - targets: [] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo scrape_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - job_name: "prometheus" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo       - targets: ["localhost:9090"] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - job_name: "windows_exporter" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo       - targets: ["host.docker.internal:9182"] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"

echo [OK] Configuracion de Prometheus creada
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

:: --- FASE 2B: Configuracion para servidores en la nube ---
:NUBE
echo Por favor, introduce tus credenciales de Azure (Service Principal):
set /p AZURE_CLIENT_ID="Azure Client ID: "
set /p AZURE_CLIENT_SECRET="Azure Client Secret: "
set /p AZURE_TENANT_ID="Azure Tenant ID: "
set /p AZURE_SUBSCRIPTION_ID="Azure Subscription ID: "
echo.
echo NOTA: La contrasena de la VM sera visible mientras la escribes.
set /p VM_PASSWORD="Crea una contrasena para la nueva Maquina Virtual: "
echo.

cd 1-CREAR-INFRAESTRUCTURA
echo vm_password = "%VM_PASSWORD%" > terraform.tfvars
terraform init -upgrade
terraform apply -auto-approve

for /f "delims=" %%i in ('terraform output -json') do set "OUTPUTS=%%i"
for /f "delims=" %%j in ('echo %OUTPUTS% ^| jq -r ".vm_private_ip.value"') do set "VM_PRIVATE_IP=%%j"
for /f "delims=" %%k in ('echo %OUTPUTS% ^| jq -r ".vm_public_ip.value"') do set "VM_PUBLIC_IP=%%k"

cd ..

set "MONITORING_DIR=2-INICIAR-MONITOREO"

:: Crear prometheus.yml para Azure VM
echo global: > "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   scrape_interval: 15s >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   evaluation_interval: 15s >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo rule_files: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - "alert.rules.yml" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo alerting: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   alertmanagers: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     - static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo         - targets: [] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo scrape_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - job_name: "prometheus" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo       - targets: ["localhost:9090"] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo. >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo   - job_name: "azure_vm" >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo     static_configs: >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"
echo       - targets: ["%VM_PUBLIC_IP%:9100"] >> "%MONITORING_DIR%\config\prometheus\prometheus.yml"

cd "%MONITORING_DIR%"
docker-compose up -d

echo.
echo ---------------------------------------------------------
echo Infraestructura en la nube desplegada!
echo IP Publica VM: %VM_PUBLIC_IP%
echo Dashboard Grafana: http://localhost:3000  (admin/admin)
echo Dashboard OptiMon: Ya importado automaticamente
echo ---------------------------------------------------------
echo.
goto FIN

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
echo Tu sistema de monitoreo esta listo!
pause