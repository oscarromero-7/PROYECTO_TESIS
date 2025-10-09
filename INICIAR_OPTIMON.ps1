# OptiMon - Sistema de Monitoreo 100% Automatico
# Inicia todo el sistema con una sola ejecucion

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "🚀 OptiMon - Iniciando Sistema Automatico Completo" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está ejecutándose
try {
    docker version | Out-Null
    Write-Host "✅ Docker está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está ejecutándose. Por favor inicia Docker Desktop." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Cambiar al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host ""
Write-Host "📦 Paso 1: Iniciando contenedores de monitoreo..." -ForegroundColor Yellow
Set-Location "2-INICIAR-MONITOREO"

try {
    docker-compose up -d
    Write-Host "✅ Contenedores iniciados exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error iniciando contenedores" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Esperar a que los servicios estén listos
Write-Host ""
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "🔍 Paso 2: Ejecutando descubrimiento y configuración automática..." -ForegroundColor Yellow
Set-Location ".."

try {
    python scripts\auto_setup.py
    Write-Host "✅ Configuración automática completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en configuración automática" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "✅ SISTEMA OPTIMON INICIADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Servicios disponibles:" -ForegroundColor White
Write-Host "   - Grafana:      http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "   - Prometheus:   http://localhost:9090" -ForegroundColor Cyan
Write-Host "   - AlertManager: http://localhost:9093" -ForegroundColor Cyan
Write-Host "   - Diagnóstico:  http://localhost:9101/metrics" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Dashboard principal: Diagnóstico de Infraestructura" -ForegroundColor Yellow
Write-Host "   -> http://localhost:3000/d/diagnostic-dashboard" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Para detener el sistema:" -ForegroundColor White
Write-Host "   cd 2-INICIAR-MONITOREO" -ForegroundColor Gray
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host ""

# Abrir automáticamente el dashboard principal
Write-Host "🌐 Abriendo dashboard principal..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/d/diagnostic-dashboard"

Write-Host ""
Write-Host "✅ Sistema OptiMon ejecutándose. ¡Disfruta del monitoreo automático!" -ForegroundColor Green
Write-Host ""
Read-Host "Presiona Enter para continuar"