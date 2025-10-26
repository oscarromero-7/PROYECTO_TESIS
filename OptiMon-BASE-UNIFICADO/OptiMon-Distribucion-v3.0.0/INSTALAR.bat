@echo off
cls
title OptiMon - Instalacion Automatica

========================================================
         OPTIMON - INSTALACION AUTOMATICA
========================================================

Instalando sistema de monitoreo OptiMon...

Verificando requisitos...

:: Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado o no esta en el PATH
    echo Por favor instale Docker Desktop antes de continuar
    pause
    exit /b 1
)

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python 3.8+ antes de continuar
    pause
    exit /b 1
)

echo Instalando dependencias Python...
pip install -r requirements.txt

echo Iniciando configuracion automatica...
SETUP_AUTOMATICO_COMPLETO.bat
