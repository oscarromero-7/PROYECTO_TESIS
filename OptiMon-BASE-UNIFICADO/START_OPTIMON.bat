@echo off
echo ====================================
echo     OptiMon Sistema Unificado
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado o no esta en PATH
    pause
    exit /b 1
)

echo [2/3] Iniciando servicios Docker...
docker compose up -d
if errorlevel 1 (
    echo ERROR: No se pudieron iniciar los servicios Docker
    pause
    exit /b 1
)

echo [3/3] Iniciando servidor OptiMon...
echo.
echo ========================================
echo   Servidor OptiMon iniciado en:
echo   http://localhost:5000
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py

echo.
echo Servidor detenido.
pause