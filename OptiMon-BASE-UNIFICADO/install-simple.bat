@echo off
title OptiMon - Instalación Simplificada
color 0E

echo.
echo ==========================================
echo   OptiMon - Instalación Simplificada
echo   Solo dependencias básicas
echo ==========================================
echo.

REM Verificar app.py
if not exist "app.py" (
    echo ❌ Ejecute desde el directorio OptiMon-BASE-UNIFICADO
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias mínimas...
python -m pip install --user Flask requests psutil PyYAML python-dotenv

echo.
echo [2/3] Creando configuración básica...
if not exist ".env" (
    echo FLASK_ENV=production > .env
    echo FLASK_DEBUG=False >> .env
)

echo.
echo [3/3] Iniciando aplicación...
echo.
echo ✅ Instalación simplificada completada
echo.
echo 📱 Portal: http://localhost:5000
echo.
echo Nota: Para funcionalidad completa, use Docker Desktop
echo.

start "" http://localhost:5000
timeout /t 2 /nobreak >nul

echo 🚀 Iniciando OptiMon (modo básico)...
python app.py

pause