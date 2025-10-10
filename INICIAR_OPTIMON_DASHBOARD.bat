@echo off
echo.
echo ============================================
echo           OPTIMON DASHBOARD
echo     Sistema de Monitoreo Integral
echo ============================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo    Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Cambiar al directorio de monitoreo
cd /d "%~dp0\2-INICIAR-MONITOREO"

REM Verificar si el archivo del dashboard existe
if not exist "optimon_dashboard.py" (
    echo ❌ Error: No se encuentra optimon_dashboard.py
    echo    Verifica que el archivo esté en el directorio correcto
    pause
    exit /b 1
)

echo ✅ Dashboard encontrado
echo.

REM Instalar dependencias si es necesario
if not exist "requirements_smtp.txt" (
    echo ⚠️  Advertencia: No se encuentra requirements_smtp.txt
) else (
    echo 📦 Instalando dependencias...
    pip install -r requirements_smtp.txt >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Algunas dependencias pueden no haberse instalado correctamente
    ) else (
        echo ✅ Dependencias instaladas
    )
)

echo.
echo 🚀 Iniciando OptiMon Dashboard...
echo.
echo ============================================
echo  🌐 URL del Dashboard: http://localhost:8080
echo  📧 Configuración de emails y SMTP
echo  ☁️  Gestión de proveedores cloud
echo  📊 Monitoreo en tiempo real
echo  🔔 Sistema de alertas
echo ============================================
echo.
echo 💡 INSTRUCCIONES:
echo    1. El dashboard se abrirá en tu navegador
echo    2. Configura primero el SMTP para emails
echo    3. Agrega emails de destino para alertas
echo    4. Configura proveedores cloud si es necesario
echo    5. Ajusta umbrales de monitoreo
echo.
echo ⚠️  Para detener el dashboard, presiona Ctrl+C
echo.

REM Intentar abrir en el navegador automáticamente
timeout /t 3 /nobreak >nul
start http://localhost:8080

REM Ejecutar el dashboard
python optimon_dashboard.py

echo.
echo 👋 Dashboard cerrado. ¡Gracias por usar OptiMon!
pause