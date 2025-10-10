@echo off
REM OptiMon Complete System Startup
REM Inicia todo el sistema OptiMon (Docker + SMTP Service)

echo =========================================
echo     OptiMon Complete System Startup
echo =========================================

cd /d "%~dp0"

REM 1. Verificar Docker
echo 🐳 Verificando Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está ejecutándose
    echo 💡 Inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)

REM 2. Iniciar servicios Docker
echo 🚀 Iniciando servicios Docker (Prometheus, Grafana, AlertManager)...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Error iniciando servicios Docker
    pause
    exit /b 1
)

REM 3. Esperar que los servicios inicien
echo ⏰ Esperando que los servicios Docker inicien...
timeout /t 10 /nobreak >nul

REM 4. Iniciar servicio SMTP
echo 📧 Iniciando OptiMon SMTP Service...
call start_optimon_smtp.bat

REM 5. Verificar estado de todos los servicios
echo.
echo 📊 ESTADO FINAL DEL SISTEMA:
echo =====================================

echo.
echo 🐳 Servicios Docker:
docker-compose ps

echo.
echo 📧 Servicio SMTP:
python optimon_smtp_daemon.py status

echo.
echo 🌐 URLs del sistema:
echo    Prometheus: http://localhost:9090
echo    Grafana:    http://localhost:3000
echo    SMTP API:   http://localhost:5555

echo.
echo 🧪 Probar sistema:
echo    python test_simple_email.py

echo.
echo ✅ Sistema OptiMon completamente iniciado
pause