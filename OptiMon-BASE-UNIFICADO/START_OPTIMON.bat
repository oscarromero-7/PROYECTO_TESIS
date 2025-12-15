@echo off
echo 🚀 Iniciando OptiMon v3.1.0 - Sistema de Monitoreo Unificado
echo ================================================================
echo.

:: Verificar si Docker está instalado
echo [INFO] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [❌] Docker no está instalado. Por favor instala Docker primero.
    pause
    exit /b 1
)
echo [✅] Docker está disponible

:: Verificar si Docker Compose está instalado
echo [INFO] Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [❌] Docker Compose no está instalado. Por favor instala Docker Compose primero.
    pause
    exit /b 1
)
echo [✅] Docker Compose está disponible

:: Verificar si Python está instalado
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [❌] Python no está instalado. Por favor instala Python primero.
    pause
    exit /b 1
)
echo [✅] Python está disponible

:: Instalar dependencias de Python
echo [INFO] Instalando dependencias de Python...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] Dependencias de Python instaladas
) else (
    echo [⚠️] Error instalando dependencias. Continuando...
)

:: Crear directorios necesarios
echo [INFO] Creando directorios necesarios...
if not exist "config\prometheus" mkdir config\prometheus
if not exist "config\alertmanager" mkdir config\alertmanager
if not exist "config\grafana" mkdir config\grafana
if not exist "logs" mkdir logs
echo [✅] Directorios creados

:: Iniciar servicios de monitoreo con Docker Compose
echo [INFO] Iniciando servicios de monitoreo (Prometheus, Grafana, AlertManager)...
docker-compose -f docker-compose-unified.yml up -d
if %errorlevel% equ 0 (
    echo [✅] Servicios Docker iniciados correctamente
) else (
    echo [❌] Error iniciando servicios Docker
    pause
    exit /b 1
)

:: Esperar a que los servicios estén listos
echo [INFO] Esperando a que los servicios estén listos...
timeout /t 15 /nobreak >nul

:: Verificar estado de los servicios
echo [INFO] Verificando estado de servicios...

:: Verificar Prometheus
curl -s http://localhost:9090/api/v1/status/config >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] Prometheus está funcionando (http://localhost:9090)
) else (
    echo [⚠️] Prometheus no responde en puerto 9090
)

:: Verificar Grafana
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] Grafana está funcionando (http://localhost:3000)
) else (
    echo [⚠️] Grafana no responde en puerto 3000
)

:: Verificar AlertManager
curl -s http://localhost:9093/api/v1/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] AlertManager está funcionando (http://localhost:9093)
) else (
    echo [⚠️] AlertManager no responde en puerto 9093
)

:: Verificar Node Exporter
curl -s http://localhost:9100/metrics >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] Node Exporter está funcionando (http://localhost:9100)
) else (
    echo [⚠️] Node Exporter no responde en puerto 9100
)

:: Verificar cAdvisor
curl -s http://localhost:8080/metrics >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] cAdvisor está funcionando (http://localhost:8080)
) else (
    echo [⚠️] cAdvisor no responde en puerto 8080
)

echo.
echo [INFO] Preparándose para iniciar OptiMon Portal...
timeout /t 3 /nobreak >nul

:: Iniciar OptiMon Portal
echo [INFO] Iniciando OptiMon Portal...
echo.
echo 🎯 Accesos rápidos:
echo    • OptiMon Portal:    http://localhost:5000
echo    • Grafana Dashboard: http://localhost:3000 (admin/admin)
echo    • Prometheus:        http://localhost:9090
echo    • AlertManager:      http://localhost:9093
echo.
echo [INFO] Iniciando servidor Flask...
echo.

:: Ejecutar la aplicación principal
python app.py