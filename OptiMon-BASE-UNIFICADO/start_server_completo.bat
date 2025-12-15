@echo off
echo ========================================
echo    OptiMon - Sistema Completo v3.1.0
echo ========================================

cd /d "C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO"

echo.
echo 1. Verificando dependencias...
python -c "import psutil; print('✅ psutil OK')" 2>nul || (
    echo ⚠️ Instalando psutil...
    python -m pip install psutil
)

echo.
echo 2. Verificando servicios base...
if exist "2-INICIAR-MONITOREO\docker-compose.yml" (
    echo ✅ Docker Compose encontrado
    cd "2-INICIAR-MONITOREO"
    echo Iniciando servicios de monitoreo...
    docker-compose up -d 2>nul
    cd ..
) else (
    echo ⚠️ Sin servicios Docker, usando solo Flask
)

echo.
echo 3. Iniciando OptiMon Flask Server...
start "OptiMon Server v3.1.0" /min python app.py

echo.
echo ✅ OptiMon Sistema Completo iniciado
echo 🌐 Web Interface: http://localhost:5000
echo 📊 Dashboard: http://localhost:5000/dashboard
echo 📈 Grafana (si disponible): http://localhost:3000
echo 🔍 Prometheus (si disponible): http://localhost:9090
echo.
echo Para detener: stop_server_completo.bat
echo.
pause