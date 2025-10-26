@echo off
echo ================================================================
echo            OPTIMON - INSTALACION AUTOMATICA COMPLETA
echo                    Sistema Unificado v3.0.0
echo ================================================================
echo.

:: Verificar privilegios de administrador y solicitar elevación automáticamente
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Solicitando permisos de administrador...
    echo        Se abrirá ventana UAC para confirmar permisos
    echo.
    
    :: Crear script temporal para re-ejecutar con privilegios
    echo @echo off > "%temp%\optimon_admin.bat"
    echo cd /d "%~dp0" >> "%temp%\optimon_admin.bat"
    echo call "%~f0" admin >> "%temp%\optimon_admin.bat"
    
    :: Ejecutar con privilegios de administrador
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%temp%\optimon_admin.bat\"' -Verb RunAs"
    exit /b 0
)

:: Eliminar archivo temporal si existe
if exist "%temp%\optimon_admin.bat" del "%temp%\optimon_admin.bat"

:: Verificar si es llamada con parámetro admin
if "%1"=="admin" (
    echo [OK] Ejecutando con privilegios de administrador
) else (
    echo [OK] Privilegios de administrador verificados
)

echo [INFO] Iniciando instalacion automatica...
echo.

:: Verificar Docker
echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker no encontrado. Instale Docker Desktop desde:
    echo         https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker encontrado

:: Verificar Python
echo [2/6] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no encontrado. Instale Python desde:
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado

:: Instalar dependencias
echo [3/6] Instalando dependencias Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

:: Iniciar servicios Docker
echo [4/6] Iniciando servicios Docker...
docker compose up -d
if %errorLevel% neq 0 (
    echo [ERROR] Error iniciando servicios Docker
    pause
    exit /b 1
)
echo [OK] Servicios Docker iniciados

:: Esperar a que los servicios esten listos
echo [5/6] Esperando servicios...
timeout /t 10 /nobreak >nul

:: Iniciar portal web
echo [6/6] Iniciando portal web OptiMon...
start /B python app.py

:: Esperar a que el portal inicie
timeout /t 5 /nobreak >nul

:: Abrir navegadores
start http://localhost:5000
start http://localhost:3000

echo.
echo ================================================================
echo                    INSTALACION COMPLETADA
echo ================================================================
echo.
echo   Portal OptiMon:  http://localhost:5000
echo   Grafana:         http://localhost:3000 (admin/admin)
echo   Prometheus:      http://localhost:9090
echo   AlertManager:    http://localhost:9093
echo.
echo   Presiona cualquier tecla para finalizar...
pause >nul