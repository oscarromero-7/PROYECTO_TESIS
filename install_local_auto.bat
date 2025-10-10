@echo off
:: OptiMon - Instalador Automático Node Exporter Local (Windows)
:: Se ejecuta automáticamente como administrador

:: Verificar si ya se está ejecutando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    goto :elevate
)

:elevate
:: Si no es administrador, solicitar elevación automáticamente
echo 🔐 Solicitando permisos de administrador...
echo.
echo ⚠️  IMPORTANTE: Click "SI" en la ventana UAC que aparecerá
echo.
timeout /t 3 >nul

:: Elevar permisos y ejecutar de nuevo
powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
exit

:admin
:: Ya tenemos permisos de administrador, proceder con instalación
title OptiMon - Instalador Node Exporter Local
color 0A

echo.
echo ================================
echo  🚀 OptiMon - Instalador Local
echo ================================
echo.
echo 📍 Instalando Node Exporter en esta computadora
echo 💻 Sistema: Windows Local
echo 🎯 Puerto: 9100
echo.

:: Verificar si ya está instalado
sc query "NodeExporter" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Node Exporter ya está instalado
    echo 🔍 Verificando estado del servicio...
    
    sc query "NodeExporter" | find "RUNNING" >nul
    if %errorLevel% == 0 (
        echo ✅ Servicio ejecutándose correctamente
        goto :configure_prometheus
    ) else (
        echo 🔄 Iniciando servicio...
        sc start "NodeExporter"
        timeout /t 3 >nul
        goto :configure_prometheus
    )
)

echo 📦 Instalando Node Exporter...
echo.

:: Crear directorio de instalación
echo 📁 Creando directorio de instalación...
if not exist "C:\Program Files\node_exporter" (
    mkdir "C:\Program Files\node_exporter"
)

:: Cambiar a directorio temporal
cd /d "%TEMP%"

:: Limpiar archivos anteriores
if exist "node_exporter*" (
    del /f /q "node_exporter*" >nul 2>&1
    rmdir /s /q "node_exporter-*" >nul 2>&1
)

echo ⬇️  Descargando Node Exporter v1.6.1...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.windows-amd64.tar.gz' -OutFile 'node_exporter.tar.gz' -UseBasicParsing; Write-Host '✅ Descarga completada' } catch { Write-Host '❌ Error descargando:' $_.Exception.Message; exit 1 }}"

if not exist "node_exporter.tar.gz" (
    echo ❌ Error: No se pudo descargar el archivo
    pause
    exit /b 1
)

echo 📦 Extrayendo archivos...
tar -xzf "node_exporter.tar.gz" 2>nul
if %errorLevel% neq 0 (
    echo ❌ Error extrayendo archivos
    echo 💡 Asegúrate de tener Windows 10 v1803 o superior ^(para soporte tar^)
    pause
    exit /b 1
)

:: Buscar directorio extraído
for /d %%i in (node_exporter-*) do set "extracted_dir=%%i"
if not defined extracted_dir (
    echo ❌ Error: No se encontró el directorio extraído
    pause
    exit /b 1
)

echo 📋 Copiando ejecutable...
copy "%extracted_dir%\node_exporter.exe" "C:\Program Files\node_exporter\" >nul
if %errorLevel% neq 0 (
    echo ❌ Error copiando ejecutable
    pause
    exit /b 1
)

echo 🔥 Configurando Windows Firewall...
powershell -Command "try { New-NetFirewallRule -DisplayName 'Node Exporter' -Direction Inbound -Port 9100 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null; Write-Host '✅ Firewall configurado' } catch { Write-Host '⚠️  Advertencia: No se pudo configurar firewall automáticamente' }"

echo ⚙️  Creando servicio de Windows...
sc create "NodeExporter" binPath= "\"C:\Program Files\node_exporter\node_exporter.exe\" --web.listen-address=:9100" start= auto DisplayName= "Prometheus Node Exporter" >nul
if %errorLevel% neq 0 (
    echo ❌ Error creando servicio
    pause
    exit /b 1
)

echo 🚀 Iniciando servicio...
sc start "NodeExporter" >nul
if %errorLevel% neq 0 (
    echo ❌ Error iniciando servicio
    pause
    exit /b 1
)

:: Esperar que el servicio inicie
echo ⏳ Esperando que el servicio inicie...
timeout /t 5 >nul

:: Verificar que está funcionando
echo 🔍 Verificando instalación...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9100/metrics' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '✅ Node Exporter funcionando correctamente!' } else { Write-Host '❌ Error: Servicio no responde' } } catch { Write-Host '⚠️  Servicio iniciando, puede tardar unos segundos...' }"

:configure_prometheus
echo.
echo 🔧 Configurando Prometheus...

:: Volver al directorio del proyecto
cd /d "c:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS"

:: Verificar que existe el archivo de configuración
if not exist "2-INICIAR-MONITOREO\config\prometheus\prometheus.yml" (
    echo ❌ Error: No se encontró la configuración de Prometheus
    echo 💡 Asegúrate de estar en el directorio correcto del proyecto OptiMon
    pause
    exit /b 1
)

:: Obtener IP local
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /R /C:"IPv4.*Address"') do (
    for /f "tokens=1" %%j in ("%%i") do set "LOCAL_IP=%%j"
    goto :ip_found
)
:ip_found
set "LOCAL_IP=%LOCAL_IP: =%"

echo 📍 IP Local detectada: %LOCAL_IP%

:: Crear script Python temporal para actualizar configuración
echo import yaml > update_prometheus.py
echo import sys >> update_prometheus.py
echo. >> update_prometheus.py
echo try: >> update_prometheus.py
echo     config_file = "2-INICIAR-MONITOREO/config/prometheus/prometheus.yml" >> update_prometheus.py
echo     with open(config_file, 'r', encoding='utf-8'^) as f: >> update_prometheus.py
echo         config = yaml.safe_load(f^) >> update_prometheus.py
echo. >> update_prometheus.py
echo     # Buscar job local_windows >> update_prometheus.py
echo     local_job = None >> update_prometheus.py
echo     for job in config['scrape_configs']: >> update_prometheus.py
echo         if job['job_name'] == 'local_windows': >> update_prometheus.py
echo             local_job = job >> update_prometheus.py
echo             break >> update_prometheus.py
echo. >> update_prometheus.py
echo     if not local_job: >> update_prometheus.py
echo         local_job = {'job_name': 'local_windows', 'static_configs': []} >> update_prometheus.py
echo         config['scrape_configs'].append(local_job^) >> update_prometheus.py
echo. >> update_prometheus.py
echo     # Actualizar target >> update_prometheus.py
echo     target = "%LOCAL_IP%:9100" >> update_prometheus.py
echo     local_job['static_configs'] = [{'targets': [target], 'labels': {'provider': 'local', 'os': 'windows', 'instance': 'local-computer'}}] >> update_prometheus.py
echo. >> update_prometheus.py
echo     with open(config_file, 'w', encoding='utf-8'^) as f: >> update_prometheus.py
echo         yaml.dump(config, f, default_flow_style=False, allow_unicode=True^) >> update_prometheus.py
echo. >> update_prometheus.py
echo     print("✅ Configuración de Prometheus actualizada"^) >> update_prometheus.py
echo except Exception as e: >> update_prometheus.py
echo     print(f"❌ Error actualizando configuración: {e}"^) >> update_prometheus.py

:: Ejecutar script Python
python update_prometheus.py
del update_prometheus.py

echo 🔄 Reiniciando Prometheus...
docker-compose -f "2-INICIAR-MONITOREO\docker-compose.yml" restart prometheus >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Prometheus reiniciado
) else (
    echo ⚠️  Advertencia: No se pudo reiniciar Prometheus automáticamente
    echo 💡 Reinicia manualmente con: docker-compose restart prometheus
)

:: Limpiar archivos temporales
cd /d "%TEMP%"
if exist "node_exporter*" (
    del /f /q "node_exporter*" >nul 2>&1
    rmdir /s /q "node_exporter-*" >nul 2>&1
)

echo.
echo ================================
echo  🎉 ¡INSTALACIÓN COMPLETADA!
echo ================================
echo.
echo ✅ Node Exporter instalado y funcionando
echo 📊 Métricas locales: http://localhost:9100/metrics
echo 📊 Métricas desde red: http://%LOCAL_IP%:9100/metrics
echo 🔗 Grafana: http://localhost:3000
echo 📈 Dashboard: "Physical Servers" ^(incluirá esta computadora^)
echo.
echo 📋 Información del servicio:
echo    Nombre: NodeExporter
echo    Estado: Ejecutándose automáticamente
echo    Puerto: 9100
echo.
echo 💡 Comandos útiles:
echo    Ver estado: sc query NodeExporter
echo    Reiniciar: sc stop NodeExporter ^&^& sc start NodeExporter
echo    Detener: sc stop NodeExporter
echo.

:: Verificar métricas una vez más
echo 🔍 Verificación final...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9100/metrics' -TimeoutSec 5 -UseBasicParsing; $lines = ($response.Content -split \"`n\" | Where-Object { $_ -like \"# HELP*\" }).Count; Write-Host \"✅ $lines métricas disponibles\" } catch { Write-Host '⚠️  Métricas aún no disponibles, espera unos segundos' }"

echo.
echo ⏱️  En unos segundos podrás ver las métricas de esta computadora en Grafana
echo 🎯 Ve a: http://localhost:3000 ^> Dashboards ^> Physical Servers
echo.

pause