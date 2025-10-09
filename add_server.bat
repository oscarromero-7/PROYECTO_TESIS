@echo off
REM Script para anadir servidores fisicos al monitoreo

setlocal enabledelayedexpansion

echo.
echo   OptiMon - Anadir Servidor Fisico
echo ===================================
echo.

REM Detectar Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python no esta instalado
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Solicitar informacion del servidor
set /p server_name="Nombre del servidor: "
set /p server_ip="Direccion IP: "
set /p ssh_user="Usuario SSH: "
set /p ssh_port="Puerto SSH (22): "

if "%ssh_port%"=="" set ssh_port=22

echo.
echo Selecciona metodo de autenticacion:
echo 1) Clave SSH
echo 2) Contrasena
set /p auth_method="Opcion (1-2): "

if "%auth_method%"=="1" (
    set /p key_file="Ruta a la clave privada: "
    %PYTHON_CMD% scripts\add_physical_server.py add --name "%server_name%" --ip "%server_ip%" --user "%ssh_user%" --port %ssh_port% --key "%key_file%" --install
) else (
    set /p ssh_pass="Contrasena SSH: "
    %PYTHON_CMD% scripts\add_physical_server.py add --name "%server_name%" --ip "%server_ip%" --user "%ssh_user%" --port %ssh_port% --password "%ssh_pass%" --install
)

echo.
pause