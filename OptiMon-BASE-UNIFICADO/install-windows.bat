@echo off
title OptiMon Sistema Unificado - Instalador
color 0A

echo.
echo ==========================================
echo   OptiMon Sistema Unificado v3.0.0
echo   Instalador Automatico Windows
echo ==========================================
echo.

REM Verificar si estamos en el directorio correcto
if not exist "app.py" (
    echo ❌ ERROR: No se encuentra app.py en el directorio actual
    echo Por favor ejecute este script desde el directorio OptiMon-BASE-UNIFICADO
    echo.
    pause
    exit /b 1
)

echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker no encontrado
    echo.
    echo Por favor instalar Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Presiona cualquier tecla para continuar cuando Docker esté instalado...
    pause
    
    REM Verificar Docker nuevamente
    docker --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker aún no está disponible. Abortando instalación.
        pause
        exit /b 1
    )
)
echo ✅ Docker encontrado

echo.
echo [2/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no encontrado
    echo.
    echo Por favor instalar Python 3.11+ desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalación, marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

echo.
echo [3/6] Actualizando pip y instalando dependencias...
echo   Esto puede tomar varios minutos...

REM Actualizar pip primero
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Advertencia: No se pudo actualizar pip, continuando...
)

REM Instalar dependencias con manejo de errores mejorado
echo   Instalando dependencias Python...
python -m pip install --user --upgrade setuptools wheel
python -m pip install -r requirements.txt --no-warn-script-location

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Fallo instalación de algunas dependencias
    echo.
    echo Intentando instalación alternativa...
    
    REM Intentar instalación paquete por paquete
    python -m pip install Flask==2.3.3
    python -m pip install requests==2.31.0
    python -m pip install psutil==5.9.5
    python -m pip install PyYAML==6.0.1
    python -m pip install python-dotenv==1.0.0
    python -m pip install paramiko
    python -m pip install boto3
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ ERROR CRÍTICO: No se pudieron instalar las dependencias básicas
        echo.
        echo Posibles soluciones:
        echo 1. Ejecutar como Administrador
        echo 2. Verificar conexión a Internet
        echo 3. Actualizar Python a la última versión
        echo 4. Ejecutar: python -m pip install --upgrade pip
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencias instaladas

echo.
echo [4/6] Iniciando servicios Docker...
echo   Iniciando Prometheus, Grafana y AlertManager...
docker compose up -d
if %errorlevel% neq 0 (
    echo ❌ ERROR: Fallo inicio Docker services
    echo.
    echo Posibles soluciones:
    echo 1. Verificar que Docker Desktop esté ejecutándose
    echo 2. Reiniciar Docker Desktop
    echo 3. Verificar puertos 3000, 9090, 9093 no estén ocupados
    echo.
    echo ¿Desea intentar nuevamente? (s/n)
    set /p retry=
    if /i "%retry%"=="s" (
        echo Reintentando...
        docker compose down
        timeout /t 5 /nobreak >nul
        docker compose up -d
        if %errorlevel% neq 0 (
            echo ❌ Error persistente con Docker
            pause
            exit /b 1
        )
    ) else (
        echo Abortando instalación
        pause
        exit /b 1
    )
)
echo ✅ Servicios Docker iniciados

echo.
echo [5/6] Configurando archivo .env...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ Archivo .env creado desde .env.example
    ) else (
        echo # OptiMon Configuration > .env
        echo FLASK_ENV=production >> .env
        echo FLASK_DEBUG=False >> .env
        echo ✅ Archivo .env básico creado
    )
) else (
    echo ✅ Archivo .env ya existe
)

echo.
echo [6/6] Verificando instalación...
echo   Verificando servicios Docker...
docker compose ps

echo.
echo   Verificando conectividad Python...
python -c "import flask, requests, psutil, yaml, paramiko; print('✅ Todas las librerías importadas correctamente')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Advertencia: Algunas librerías podrían no estar disponibles
)

echo.
echo ==========================================
echo   ✅ INSTALACION COMPLETADA
echo ==========================================
echo.
echo   Accesos del sistema:
echo   📱 Portal Principal: http://localhost:5000
echo   📊 Grafana:         http://localhost:3000
echo   📈 Prometheus:      http://localhost:9090
echo   🚨 AlertManager:    http://localhost:9093
echo.
echo   Iniciando aplicacion en 3 segundos...
echo ==========================================
echo.

timeout /t 3 /nobreak >nul

REM Abrir navegador
start "" http://localhost:5000

REM Iniciar aplicación
echo 🚀 Iniciando OptiMon Portal...
echo   Presiona Ctrl+C para detener el servidor
echo.
python app.py

echo.
echo 📛 Aplicación detenida
pause