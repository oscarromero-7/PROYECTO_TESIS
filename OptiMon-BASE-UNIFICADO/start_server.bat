@echo off
echo ========================================
echo    OptiMon - Iniciando Servidor
echo ========================================
cd /d "C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO"

echo Verificando dependencias...
python -c "import openpyxl" 2>nul
if %errorlevel% neq 0 (
    echo Instalando openpyxl...
    pip install openpyxl
)

echo Iniciando servidor en segundo plano...
start "OptiMon Server" /min python app.py

echo.
echo ✅ Servidor OptiMon iniciado en segundo plano
echo 🌐 Disponible en: http://localhost:5000
echo 📊 Dashboard: http://localhost:5000/dashboard
echo.
echo Para detener el servidor, busca "OptiMon Server" en el administrador de tareas
echo o ejecuta: taskkill /fi "WINDOWTITLE eq OptiMon Server"
echo.
pause