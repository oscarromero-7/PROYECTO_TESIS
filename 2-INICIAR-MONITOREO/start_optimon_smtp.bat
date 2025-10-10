@echo off
REM OptiMon SMTP Service - Script de inicio automático
REM Este script inicia el servicio de emails en segundo plano

echo =========================================
echo  OptiMon SMTP Service - Inicio Automatico
echo =========================================

cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado en PATH
    echo 💡 Instala Python o agregalo al PATH
    pause
    exit /b 1
)

REM Verificar si el archivo de configuración existe
if not exist ".env" (
    echo ❌ Archivo .env no encontrado
    echo 💡 Configura primero las credenciales SMTP
    echo    Copia .env.gmail a .env y edita las credenciales
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo 📦 Verificando dependencias...
python -c "import flask, requests, dotenv" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias necesarias...
    pip install -r requirements_smtp.txt
)

REM Verificar si ya está ejecutándose
echo 🔍 Verificando estado del servicio...
python optimon_smtp_daemon.py status >nul 2>&1
if not errorlevel 1 (
    echo ✅ El servicio ya está ejecutándose
    python optimon_smtp_daemon.py status
    echo.
    echo 📋 Comandos disponibles:
    echo    start_optimon_smtp.bat     - Iniciar servicio
    echo    stop_optimon_smtp.bat      - Detener servicio
    echo    restart_optimon_smtp.bat   - Reiniciar servicio
    echo    status_optimon_smtp.bat    - Ver estado
    pause
    exit /b 0
)

REM Iniciar el servicio
echo 🚀 Iniciando OptiMon SMTP Service...
python optimon_smtp_daemon.py start

if errorlevel 1 (
    echo ❌ Error iniciando el servicio
    echo 💡 Revisa la configuración y vuelve a intentar
    pause
    exit /b 1
)

echo.
echo ✅ OptiMon SMTP Service iniciado exitosamente
echo 📧 El servicio está ejecutándose en segundo plano
echo 🌐 Puerto: 5555
echo 📁 Logs: logs\optimon_smtp_daemon.log
echo.
echo 📋 Comandos de gestión:
echo    python optimon_smtp_daemon.py status    - Ver estado
echo    python optimon_smtp_daemon.py stop      - Detener
echo    python optimon_smtp_daemon.py restart   - Reiniciar
echo.
echo 🧪 Probar envío de emails:
echo    python test_simple_email.py
echo.

pause