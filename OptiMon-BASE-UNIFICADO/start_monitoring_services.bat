@echo off
echo ========================================
echo    OptiMon - Iniciando Servicios de Monitoreo
echo ========================================
echo.

:: Verificar si Docker Desktop está corriendo
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker está disponible. Iniciando servicios con Docker...
    docker-compose up -d
    if %errorlevel% equ 0 (
        echo [OK] Servicios iniciados con Docker exitosamente
        echo.
        echo ✅ Prometheus: http://localhost:9090
        echo ✅ Grafana: http://localhost:3000 (admin/admin)
        echo ✅ Alertmanager: http://localhost:9093
        goto end
    )
)

echo [INFO] Docker no disponible. Iniciando Docker Desktop...
echo [INFO] Esperando a que Docker Desktop inicie...

:: Intentar iniciar Docker Desktop
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] No se pudo iniciar Docker Desktop automáticamente
    echo [INFO] Por favor inicia Docker Desktop manualmente y luego ejecuta:
    echo [INFO] docker-compose up -d
    goto end
)

:: Esperar a que Docker esté listo
echo [INFO] Esperando 30 segundos para que Docker se inicie...
timeout /t 30 /nobreak >nul

:: Intentar nuevamente
docker-compose up -d
if %errorlevel% equ 0 (
    echo [OK] Servicios iniciados exitosamente
    echo.
    echo ✅ Prometheus: http://localhost:9090
    echo ✅ Grafana: http://localhost:3000 (admin/admin)
    echo ✅ Alertmanager: http://localhost:9093
) else (
    echo [ERROR] No se pudieron iniciar los servicios
    echo [INFO] Por favor inicia Docker Desktop manualmente y ejecuta:
    echo [INFO] docker-compose up -d
)

:end
echo.
pause