@echo off
REM OptiMon - Sistema de Monitoreo 100% Automatico
REM Inicia todo el sistema con una sola ejecucion

echo.
echo =========================================================
echo 🚀 OptiMon - Iniciando Sistema Automatico Completo
echo =========================================================
echo.

REM Verificar si Docker está ejecutándose
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor inicia Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker está ejecutándose

REM Ir al directorio del proyecto
cd /d "%~dp0"

echo.
echo 📦 Paso 1: Iniciando contenedores de monitoreo...
cd 2-INICIAR-MONITOREO
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Error iniciando contenedores
    pause
    exit /b 1
)

REM Esperar a que los servicios estén listos
echo.
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 15 /nobreak >nul

echo.
echo 🔍 Paso 2: Ejecutando descubrimiento y configuración automática...
cd ..
python scripts\auto_setup.py
if %errorlevel% neq 0 (
    echo ❌ Error en configuración automática
    pause
    exit /b 1
)

echo.
echo =========================================================
echo ✅ SISTEMA OPTIMON INICIADO EXITOSAMENTE
echo =========================================================
echo.
echo 📊 Servicios disponibles:
echo   - Grafana:      http://localhost:3000 (admin/admin)
echo   - Prometheus:   http://localhost:9090
echo   - AlertManager: http://localhost:9093
echo   - Diagnóstico:  http://localhost:9101/metrics
echo.
echo 🎯 Dashboard principal: Diagnóstico de Infraestructura
echo    -> http://localhost:3000/d/diagnostic-dashboard
echo.
echo 🔧 Para detener el sistema:
echo    cd 2-INICIAR-MONITOREO
echo    docker-compose down
echo.

REM Abrir automáticamente el dashboard principal
echo 🌐 Abriendo dashboard principal...
start http://localhost:3000/d/diagnostic-dashboard

echo.
echo ✅ Sistema OptiMon ejecutándose. ¡Disfruta del monitoreo automático!
echo.
pause