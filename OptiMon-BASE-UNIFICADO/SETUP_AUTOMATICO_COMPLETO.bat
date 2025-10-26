@echo off
cls
title OptiMon - Configuracion Automatica Completa

echo.
echo ========================================================
echo           OPTIMON - CONFIGURACION AUTOMATICA
echo ========================================================
echo.
echo Iniciando configuracion automatica del sistema completo...
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Ejecutar script PowerShell con politicas bypass
echo Ejecutando configuracion automatica...
powershell.exe -ExecutionPolicy Bypass -File "setup_automatico.ps1"

:: Verificar resultado
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo          CONFIGURACION COMPLETADA EXITOSAMENTE
    echo ========================================================
    echo.
    echo El sistema OptiMon esta completamente operativo:
    echo.
    echo   * Portal OptiMon:     http://localhost:5000
    echo   * Grafana:           http://localhost:3000 ^(admin/admin^)
    echo   * Prometheus:        http://localhost:9090
    echo   * Windows Exporter:  http://localhost:9182/metrics
    echo.
    echo ========================================================
    echo.
    pause
) else (
    echo.
    echo ========================================================
    echo              ERROR EN LA CONFIGURACION
    echo ========================================================
    echo.
    echo Revise los mensajes anteriores para identificar el problema.
    echo.
    pause
)

exit /b %ERRORLEVEL%