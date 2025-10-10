@echo off
echo 🚀 OptiMon - Instalacion de Node Exporter Local
echo ================================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Se requieren permisos de administrador
    echo.
    echo 💡 Solucion:
    echo    1. Click derecho en el boton Inicio
    echo    2. Selecciona "Terminal ^(Administrador^)" o "PowerShell ^(Administrador^)"
    echo    3. Navega a: cd "%~dp0"
    echo    4. Ejecuta: %~nx0
    echo.
    pause
    exit /b 1
)

echo ✅ Permisos de administrador confirmados
echo.

:: Variables
set VERSION=1.6.1
set INSTALL_PATH=C:\Program Files\node_exporter
set SERVICE_NAME=NodeExporter
set PORT=9100

echo 📋 Configuracion:
echo    Version: %VERSION%
echo    Directorio: %INSTALL_PATH%
echo    Puerto: %PORT%
echo    Servicio: %SERVICE_NAME%
echo.

:: Verificar si ya esta instalado
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node Exporter ya esta instalado
    sc query %SERVICE_NAME% | find "RUNNING" >nul
    if %errorlevel% equ 0 (
        echo ✅ Servicio ejecutandose correctamente
        echo 📊 Metricas disponibles en: http://localhost:%PORT%/metrics
        echo.
        goto :configure_prometheus
    ) else (
        echo 🔄 Iniciando servicio...
        sc start %SERVICE_NAME%
        timeout /t 3 >nul
    )
)

:: Crear directorio de instalacion
echo 📁 Creando directorio de instalacion...
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

:: Descargar Node Exporter usando PowerShell
echo ⬇️  Descargando Node Exporter %VERSION%...
set DOWNLOAD_URL=https://github.com/prometheus/node_exporter/releases/download/v%VERSION%/node_exporter-%VERSION%.windows-amd64.tar.gz
set TEMP_FILE=%TEMP%\node_exporter.tar.gz

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_FILE%' -UseBasicParsing}"

if %errorlevel% neq 0 (
    echo ❌ Error descargando Node Exporter
    pause
    exit /b 1
)

echo ✅ Descarga completada

:: Extraer archivos
echo 📦 Extrayendo archivos...
cd /d %TEMP%
tar -xzf node_exporter.tar.gz

:: Buscar directorio extraido
for /d %%i in (node_exporter-*) do set EXTRACTED_DIR=%%i

if not defined EXTRACTED_DIR (
    echo ❌ Error: No se encontro el directorio extraido
    pause
    exit /b 1
)

:: Copiar ejecutable
echo 📋 Instalando binario...
copy "%TEMP%\%EXTRACTED_DIR%\node_exporter.exe" "%INSTALL_PATH%\" >nul

if %errorlevel% neq 0 (
    echo ❌ Error copiando ejecutable
    pause
    exit /b 1
)

:: Configurar firewall
echo 🔥 Configurando Windows Firewall...
netsh advfirewall firewall add rule name="Node Exporter" dir=in action=allow protocol=TCP localport=%PORT% >nul 2>&1

:: Detener servicio existente si existe
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo 🛑 Deteniendo servicio existente...
    sc stop %SERVICE_NAME% >nul 2>&1
    timeout /t 2 >nul
    sc delete %SERVICE_NAME% >nul 2>&1
)

:: Crear servicio
echo ⚙️  Creando servicio de Windows...
sc create %SERVICE_NAME% binPath= "\"%INSTALL_PATH%\node_exporter.exe\" --web.listen-address=:%PORT%" start= auto >nul

if %errorlevel% neq 0 (
    echo ❌ Error creando servicio
    pause
    exit /b 1
)

:: Configurar descripcion del servicio
sc description %SERVICE_NAME% "Prometheus Node Exporter - Metricas del sistema OptiMon" >nul

:: Iniciar servicio
echo 🚀 Iniciando servicio Node Exporter...
sc start %SERVICE_NAME% >nul

if %errorlevel% neq 0 (
    echo ❌ Error iniciando servicio
    pause
    exit /b 1
)

:: Verificar instalacion
echo 🔍 Verificando instalacion...
timeout /t 3 >nul

sc query %SERVICE_NAME% | find "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✅ Node Exporter instalado y ejecutandose correctamente!
    echo.
    
    :: Obtener IP local
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| find "172.20.10"') do set LOCAL_IP=%%a
    set LOCAL_IP=%LOCAL_IP: =%
    
    if not defined LOCAL_IP (
        for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| findstr /v "127.0.0.1"') do set LOCAL_IP=%%a
        set LOCAL_IP=%LOCAL_IP: =%
    )
    
    echo 🎉 ¡Instalacion completada exitosamente!
    echo 📋 Informacion del servidor:
    echo    IP local: %LOCAL_IP%
    echo    Puerto: %PORT%
    echo    Metricas: http://%LOCAL_IP%:%PORT%/metrics
    echo    Servicio: %SERVICE_NAME%
    echo.
    
    :: Probar metricas
    echo 🔍 Probando metricas...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:%PORT%/metrics' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '✅ Metricas funcionando correctamente!' -ForegroundColor Green } } catch { Write-Host '⚠️ Las metricas aun no estan disponibles. Espera unos segundos.' -ForegroundColor Yellow }"
    
) else (
    echo ❌ Error: El servicio no esta ejecutandose
    sc query %SERVICE_NAME%
    pause
    exit /b 1
)

:configure_prometheus
echo.
echo 🔧 Configurando Prometheus para monitorear esta maquina...

:: Obtener IP local para Prometheus
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| find "172.20.10"') do set PROMETHEUS_IP=%%a
set PROMETHEUS_IP=%PROMETHEUS_IP: =%

if not defined PROMETHEUS_IP (
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4" ^| findstr /v "127.0.0.1"') do set PROMETHEUS_IP=%%a
    set PROMETHEUS_IP=%PROMETHEUS_IP: =%
)

:: Llamar script Python para configurar Prometheus
python -c "
import yaml
import sys

try:
    # Leer configuracion de Prometheus
    with open('2-INICIAR-MONITOREO/config/prometheus/prometheus.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Buscar job local_windows o crearlo
    local_job = None
    for job in config['scrape_configs']:
        if job['job_name'] == 'local_windows':
            local_job = job
            break
    
    if not local_job:
        # Crear nuevo job para Windows local
        local_job = {
            'job_name': 'local_windows',
            'static_configs': [],
            'scrape_interval': '15s'
        }
        config['scrape_configs'].append(local_job)
    
    # Agregar target localhost
    target = 'localhost:9100'
    target_exists = False
    
    for static_config in local_job['static_configs']:
        if target in static_config.get('targets', []):
            target_exists = True
            break
    
    if not target_exists:
        local_job['static_configs'] = [{
            'targets': [target],
            'labels': {
                'provider': 'local',
                'instance': 'optimon-server',
                'os': 'windows'
            }
        }]
    
    # Guardar configuracion
    with open('2-INICIAR-MONITOREO/config/prometheus/prometheus.yml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print('✅ Configuracion de Prometheus actualizada')
    
except Exception as e:
    print(f'⚠️ Error configurando Prometheus: {e}')
"

if %errorlevel% equ 0 (
    echo ✅ Prometheus configurado
    
    :: Reiniciar Prometheus
    echo 🔄 Reiniciando Prometheus...
    docker-compose -f 2-INICIAR-MONITOREO/docker-compose.yml restart prometheus >nul 2>&1
    
    if %errorlevel% equ 0 (
        echo ✅ Prometheus reiniciado
    ) else (
        echo ⚠️ No se pudo reiniciar Prometheus automaticamente
        echo 💡 Reinicia manualmente: docker-compose -f 2-INICIAR-MONITOREO/docker-compose.yml restart prometheus
    )
) else (
    echo ⚠️ Error configurando Prometheus
)

:: Limpiar archivos temporales
echo 🧹 Limpiando archivos temporales...
del /q "%TEMP%\node_exporter*" >nul 2>&1
rmdir /s /q "%TEMP%\node_exporter-*" >nul 2>&1

echo.
echo 🎯 CONFIGURACION COMPLETADA:
echo    📊 Metricas locales: http://localhost:%PORT%/metrics
echo    🔗 Grafana: http://localhost:3000
echo    📈 Dashboard: 'Infrastructure Overview' o 'Physical Servers'
echo.
echo 📚 Comandos utiles:
echo    Ver estado: sc query %SERVICE_NAME%
echo    Reiniciar: sc stop %SERVICE_NAME% ^& sc start %SERVICE_NAME%
echo    Detener: sc stop %SERVICE_NAME%
echo    Desinstalar: sc delete %SERVICE_NAME%
echo.

pause