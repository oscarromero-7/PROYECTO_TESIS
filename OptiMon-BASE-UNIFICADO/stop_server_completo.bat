@echo off
echo ========================================
echo    OptiMon - Deteniendo Sistema Completo
echo ========================================

echo Deteniendo OptiMon Flask Server...
taskkill /fi "WINDOWTITLE eq OptiMon Server v3.1.0" /f >nul 2>&1

echo Deteniendo servicios Docker (si existen)...
cd /d "C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO\2-INICIAR-MONITOREO" 2>nul
docker-compose down >nul 2>&1
cd ..

echo Deteniendo cualquier proceso Python relacionado...
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq python.exe" ^| findstr app.py 2^>nul') do (
    taskkill /pid %%i /f >nul 2>&1
)

echo ✅ Todos los servicios OptiMon detenidos
pause