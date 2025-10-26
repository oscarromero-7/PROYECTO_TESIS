@echo off
setlocal enabledelayedexpansion

cls
title OptiMon - Creador de Paquete Final

echo.
echo ============================================================
echo          OPTIMON - CREADOR DE PAQUETE FINAL LIMPIO
echo ============================================================
echo.

:: Cambiar al directorio base del proyecto
cd /d "C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO"

:: Crear directorio de distribución final
set "DIST_DIR=OptiMon-Final-v3.0.0"
set "DIST_PATH=C:\Users\oagr2\Documents\GitHub\%DIST_DIR%"

if exist "%DIST_PATH%" (
    echo Eliminando paquete anterior...
    rmdir /s /q "%DIST_PATH%"
)

echo Creando paquete de distribucion final en: %DIST_PATH%
mkdir "%DIST_PATH%"

:: Copiar archivos esenciales
echo Copiando archivos del sistema...

:: Archivos principales
copy "app.py" "%DIST_PATH%\"
copy "docker-compose.yml" "%DIST_PATH%\"
copy "requirements.txt" "%DIST_PATH%\"

:: Scripts de automatización mejorados (copiar de prueba)
copy "C:\Users\oagr2\Documents\GitHub\PRUEBA_OPTIMON\OptiMon-Distribucion-v3.0.0\INSTALAR_COMPLETO.bat" "%DIST_PATH%\"
copy "C:\Users\oagr2\Documents\GitHub\PRUEBA_OPTIMON\OptiMon-Distribucion-v3.0.0\start_server.py" "%DIST_PATH%\"
copy "C:\Users\oagr2\Documents\GitHub\PRUEBA_OPTIMON\OptiMon-Distribucion-v3.0.0\setup_ultra_simple.py" "%DIST_PATH%\"

:: Documentación final
echo # OptiMon - Sistema de Monitoreo Automatico v3.0.0> "%DIST_PATH%\README.md"
echo.>> "%DIST_PATH%\README.md"
echo ## Instalacion Ultra Simple>> "%DIST_PATH%\README.md"
echo.>> "%DIST_PATH%\README.md"
echo **SOLO EJECUTAR:** INSTALAR_COMPLETO.bat>> "%DIST_PATH%\README.md"
echo.>> "%DIST_PATH%\README.md"
echo ### Requisitos:>> "%DIST_PATH%\README.md"
echo - Docker Desktop instalado y ejecutandose>> "%DIST_PATH%\README.md"
echo - Python 3.8+ instalado>> "%DIST_PATH%\README.md"
echo.>> "%DIST_PATH%\README.md"
echo ### Que hace automaticamente:>> "%DIST_PATH%\README.md"
echo - Instala dependencias Python>> "%DIST_PATH%\README.md"
echo - Inicia servicios Docker (Prometheus, Grafana, AlertManager)>> "%DIST_PATH%\README.md"
echo - Lanza servidor OptiMon en segundo plano>> "%DIST_PATH%\README.md"
echo - Descarga e instala Windows Exporter automaticamente>> "%DIST_PATH%\README.md"
echo - Configura monitoreo completo sin intervencion manual>> "%DIST_PATH%\README.md"
echo - Abre navegador con el portal funcionando>> "%DIST_PATH%\README.md"
echo.>> "%DIST_PATH%\README.md"
echo ### Accesos tras instalacion:>> "%DIST_PATH%\README.md"
echo - Portal OptiMon: http://localhost:5000>> "%DIST_PATH%\README.md"
echo - Grafana: http://localhost:3000 (admin/admin)>> "%DIST_PATH%\README.md"
echo - Prometheus: http://localhost:9090>> "%DIST_PATH%\README.md"
echo - Windows Exporter: http://localhost:9182/metrics>> "%DIST_PATH%\README.md"

:: Directorios completos
echo Copiando directorios...
xcopy /e /i "templates" "%DIST_PATH%\templates" >nul
xcopy /e /i "docker" "%DIST_PATH%\docker" >nul
xcopy /e /i "core" "%DIST_PATH%\core" >nul

:: Crear archivo de instalación mejorado
(
echo @echo off
echo title OptiMon - Verificacion de Requisitos
echo.
echo Verificando requisitos del sistema...
echo.
echo :: Verificar Docker
echo docker --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Docker no esta instalado
echo     echo.
echo     echo Descargue e instale Docker Desktop desde:
echo     echo https://www.docker.com/products/docker-desktop
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Verificar Python
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ERROR: Python no esta instalado
echo     echo.
echo     echo Descargue e instale Python desde:
echo     echo https://www.python.org/downloads/
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Requisitos verificados. Iniciando instalacion automatica...
echo timeout /t 3 /nobreak ^>nul
echo.
echo :: Ejecutar instalacion completa
echo INSTALAR_COMPLETO.bat
) > "%DIST_PATH%\VERIFICAR_E_INSTALAR.bat"

:: Crear archivo de información del paquete
(
echo OptiMon - Sistema de Monitoreo Unificado v3.0.0
echo ===============================================
echo.
echo Paquete de distribucion final creado el: %date% %time%
echo.
echo ARCHIVOS INCLUIDOS:
echo -------------------
echo - VERIFICAR_E_INSTALAR.bat: Verifica requisitos e instala automaticamente
echo - INSTALAR_COMPLETO.bat: Instalacion directa (requiere Docker y Python)
echo - app.py: Aplicacion principal OptiMon
echo - start_server.py: Launcher del servidor
echo - setup_ultra_simple.py: Script Python alternativo
echo - docker-compose.yml: Configuracion de servicios
echo - requirements.txt: Dependencias Python
echo - templates/: Plantillas web
echo - docker/: Configuraciones Prometheus, Grafana, AlertManager
echo - core/: Servicios del sistema
echo.
echo INSTRUCCIONES DE USO:
echo ---------------------
echo 1. Extraer este archivo ZIP en cualquier ubicacion
echo 2. Ejecutar VERIFICAR_E_INSTALAR.bat
echo 3. El sistema se configurara automaticamente
echo 4. Acceder al portal en http://localhost:5000
echo.
echo FUNCIONALIDADES:
echo ----------------
echo - Monitoreo automatico de Windows
echo - Dashboards prediseñados en Grafana
echo - Alertas configuradas automaticamente
echo - Metricas de sistema, servicios y aplicaciones
echo - Portal web unificado de administracion
echo.
echo SOPORTE:
echo --------
echo Si algun servicio no funciona, ejecute nuevamente
echo INSTALAR_COMPLETO.bat para reiniciar la configuracion.
) > "%DIST_PATH%\INFORMACION.txt"

:: Crear archivo ZIP final
echo Creando archivo ZIP de distribucion final...
cd /d "C:\Users\oagr2\Documents\GitHub"
powershell -command "Compress-Archive -Path '%DIST_DIR%' -DestinationPath '%DIST_DIR%.zip' -Force"

:: Mostrar resultado
echo.
echo ============================================================
echo               PAQUETE FINAL CREADO EXITOSAMENTE
echo ============================================================
echo.
echo Ubicacion: C:\Users\oagr2\Documents\GitHub\%DIST_DIR%.zip
echo.
dir "%DIST_DIR%.zip" | findstr /C:"%DIST_DIR%.zip"
echo.
echo Contenido del paquete:
dir /b "%DIST_DIR%"
echo.
echo ============================================================
echo.
echo PAQUETE LISTO PARA DISTRIBUCION
echo.
echo Para probar:
echo 1. Extraer %DIST_DIR%.zip en otra ubicacion
echo 2. Ejecutar VERIFICAR_E_INSTALAR.bat
echo 3. Sistema se configurara automaticamente
echo.
echo El paquete es completamente autonomo e incluye
echo toda la funcionalidad de OptiMon.
echo.
pause