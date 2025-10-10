@echo off
REM OptiMon SMTP Service - Versión Simple y Confiable

title OptiMon SMTP Service

echo =========================================
echo  OptiMon SMTP Service - Iniciando...
echo =========================================

cd /d "%~dp0"

REM Verificar si ya hay un servicio ejecutándose
echo Verificando si el servicio ya esta ejecutandose...
netstat -an | find "5555" | find "LISTENING" >nul
if not errorlevel 1 (
    echo El servicio ya esta ejecutandose en puerto 5555
    echo Para detenerlo, cierra esta ventana o presiona Ctrl+C
    pause
    exit /b 0
)

REM Verificar archivo .env
if not exist ".env" (
    echo Error: Archivo .env no encontrado
    echo.
    echo COMO CONFIGURAR:
    echo 1. Copia .env.gmail a .env
    echo 2. Edita .env con tu contraseña de Gmail
    echo 3. Ejecuta este script nuevamente
    echo.
    pause
    exit /b 1
)

echo Configuracion encontrada: .env
echo.

REM Instalar dependencias si es necesario
echo Verificando dependencias...
python -c "import flask, requests, dotenv" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install flask requests python-dotenv
    if errorlevel 1 (
        echo Error instalando dependencias
        pause
        exit /b 1
    )
)

echo Dependencias OK
echo.

REM Iniciar el servicio
echo =========================================
echo  Iniciando OptiMon SMTP Service...
echo =========================================
echo.
echo Servicio ejecutandose en: http://localhost:5555
echo Para detener: Cierra esta ventana o presiona Ctrl+C
echo.
echo LOGS DEL SERVICIO:
echo ------------------

REM Ejecutar el servicio directamente
python optimon_smtp_service.py

echo.
echo =========================================
echo  OptiMon SMTP Service detenido
echo =========================================
pause