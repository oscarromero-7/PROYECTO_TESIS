@echo off
:: OptiMon - Instalador Automático de Node Exporter para Windows
:: Ejecutar como Administrador

echo.
echo ========================================
echo   OptiMon - Node Exporter Installer
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador
    echo         Click derecho en el archivo y selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo [INFO] Permisos de administrador confirmados
echo.

:: Variables
set VERSION=1.6.1
set INSTALL_DIR=C:\Program Files\node_exporter
set SERVICE_NAME=NodeExporter
set PORT=9100
set TEMP_DIR=%TEMP%\node_exporter_install

echo [INFO] Configuracion:
echo        Version: %VERSION%
echo        Directorio: %INSTALL_DIR%
echo        Puerto: %PORT%
echo        Servicio: %SERVICE_NAME%
echo.

:: Verificar si ya esta instalado
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Verificando estado del servicio existente...
    sc query %SERVICE_NAME% | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] Node Exporter ya esta instalado y ejecutandose
        echo [INFO] Verificando metricas...
        powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:%PORT%/metrics' -TimeoutSec 5 -UseBasicParsing; if ($r.StatusCode -eq 200) { Write-Host '[OK] Metricas disponibles en http://localhost:%PORT%/metrics' } } catch { Write-Host '[WARN] Servicio ejecutandose pero metricas no disponibles aun' }"
        echo.
        pause
        exit /b 0
    )
)

:: Crear directorio temporal
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

echo [INFO] Descargando Node Exporter %VERSION%...
:: Usar PowerShell para descargar
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/prometheus/node_exporter/releases/download/v%VERSION%/node_exporter-%VERSION%.windows-amd64.tar.gz' -OutFile 'node_exporter.tar.gz' -UseBasicParsing}"

if %errorLevel% neq 0 (
    echo [ERROR] Error descargando Node Exporter
    goto cleanup
)

echo [OK] Descarga completada

echo [INFO] Extrayendo archivos...
:: Usar tar nativo de Windows 10+
tar -xzf node_exporter.tar.gz
if %errorLevel% neq 0 (
    echo [ERROR] Error extrayendo archivos
    goto cleanup
)

:: Buscar directorio extraido
for /d %%i in (node_exporter-*) do set EXTRACTED_DIR=%%i

if not defined EXTRACTED_DIR (
    echo [ERROR] No se encontro el directorio extraido
    goto cleanup
)

echo [OK] Archivos extraidos

echo [INFO] Instalando Node Exporter...
:: Crear directorio de instalacion
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copiar ejecutable
copy "%EXTRACTED_DIR%\node_exporter.exe" "%INSTALL_DIR%\"
if %errorLevel% neq 0 (
    echo [ERROR] Error copiando ejecutable
    goto cleanup
)

echo [OK] Ejecutable instalado

echo [INFO] Configurando Windows Firewall...
:: Configurar firewall
netsh advfirewall firewall delete rule name="Node Exporter" >nul 2>&1
netsh advfirewall firewall add rule name="Node Exporter" dir=in action=allow protocol=TCP localport=%PORT%
if %errorLevel% equ 0 (
    echo [OK] Firewall configurado para puerto %PORT%
) else (
    echo [WARN] No se pudo configurar el firewall automaticamente
)

echo [INFO] Configurando servicio de Windows...
:: Detener y eliminar servicio existente si existe
sc stop %SERVICE_NAME% >nul 2>&1
sc delete %SERVICE_NAME% >nul 2>&1

:: Crear nuevo servicio
sc create %SERVICE_NAME% binPath= "\"%INSTALL_DIR%\node_exporter.exe\" --web.listen-address=:%PORT%" start= auto
if %errorLevel% neq 0 (
    echo [ERROR] Error creando servicio
    goto cleanup
)

:: Configurar descripcion del servicio
sc description %SERVICE_NAME% "Prometheus Node Exporter - Metricas del sistema"

echo [OK] Servicio creado

echo [INFO] Iniciando servicio...
sc start %SERVICE_NAME%
if %errorLevel% neq 0 (
    echo [ERROR] Error iniciando servicio
    goto cleanup
)

echo [OK] Servicio iniciado

echo [INFO] Verificando instalacion...
:: Esperar un poco para que el servicio inicie
timeout /t 5 /nobreak >nul

:: Verificar que el servicio esta ejecutandose
sc query %SERVICE_NAME% | find "RUNNING" >nul
if %errorLevel% neq 0 (
    echo [ERROR] El servicio no esta ejecutandose
    echo [INFO] Verificando logs...
    sc query %SERVICE_NAME%
    goto cleanup
)

echo [OK] Servicio ejecutandose correctamente

echo [INFO] Probando metricas...
:: Probar metricas con PowerShell
powershell -Command "& {for($i=0; $i -lt 10; $i++) { try { $response = Invoke-WebRequest -Uri 'http://localhost:%PORT%/metrics' -TimeoutSec 3 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[OK] Metricas funcionando correctamente!'; $content = $response.Content; $lines = ($content -split \"`n\" | Where-Object {$_ -like \"# HELP*\"} | Select-Object -First 3); Write-Host '[INFO] Ejemplos de metricas:'; foreach($line in $lines) { Write-Host \"        $line\" }; exit 0 } } catch { Start-Sleep -Seconds 2 } } Write-Host '[WARN] Metricas aun no disponibles, pero el servicio esta ejecutandose' }"

echo.
echo ========================================
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.

:: Obtener IP local
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        set LOCAL_IP=%%j
        goto :ip_found
    )
)
:ip_found

echo [INFO] Informacion del servidor:
echo        IP local: %LOCAL_IP%
echo        Puerto: %PORT%
echo        Metricas: http://%LOCAL_IP%:%PORT%/metrics
echo        Servicio: %SERVICE_NAME%
echo.
echo [INFO] Proximos pasos:
echo        1. Las metricas estan disponibles en: http://%LOCAL_IP%:%PORT%/metrics
echo        2. OptiMon detectara automaticamente este servidor
echo        3. Verifica en Grafana: http://localhost:3000
echo.
echo [INFO] Comandos utiles:
echo        Ver estado: sc query %SERVICE_NAME%
echo        Reiniciar: sc stop %SERVICE_NAME% ^&^& sc start %SERVICE_NAME%
echo        Detener: sc stop %SERVICE_NAME%
echo        Desinstalar: sc delete %SERVICE_NAME%
echo.

goto cleanup_success

:cleanup
echo.
echo [ERROR] La instalacion no se completo correctamente
echo [INFO] Limpiando archivos temporales...

:cleanup_success
:: Limpiar archivos temporales
cd /d %TEMP%
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" >nul 2>&1

echo.
pause
exit /b %errorLevel%