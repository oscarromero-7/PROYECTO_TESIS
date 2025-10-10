@echo off
title OptiMon - Sistema de Monitoreo Automatizado

echo.
echo ===============================================
echo    OPTIMON - SISTEMA DE MONITOREO
echo ===============================================
echo.

cd /d "%~dp0"

echo [INFO] Verificando directorio de trabajo...
echo [INFO] Directorio actual: %CD%
echo.

echo [INFO] Iniciando OptiMon con control avanzado...
python start_optimon_advanced.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo     OPTIMON INICIADO EXITOSAMENTE
    echo ===============================================
    echo.
    echo  Dashboard:    http://localhost:5000
    echo  Prometheus:   http://localhost:9090
    echo  Grafana:      http://localhost:3000
    echo  AlertManager: http://localhost:9093
    echo.
    echo [INFO] Todos los servicios estan corriendo en segundo plano
    echo [INFO] Puedes cerrar esta ventana de forma segura
    echo.
    pause
) else (
    echo.
    echo ===============================================
    echo      ERROR AL INICIAR OPTIMON
    echo ===============================================
    echo.
    echo [ERROR] Algunos servicios no pudieron iniciarse
    echo [ERROR] Revisa los logs para mas detalles
    echo.
    pause
    exit /b 1
)