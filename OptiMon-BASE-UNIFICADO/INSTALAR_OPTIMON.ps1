# OptiMon - Sistema Unificado v3.0.0
# Instalación Automática para Usuario Final

# Verificar y solicitar elevación automáticamente
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "🔐 Solicitando permisos de administrador..." -ForegroundColor Yellow
    Write-Host "   Se abrirá ventana UAC para confirmar permisos" -ForegroundColor Gray
    
    # Re-ejecutar el script con privilegios de administrador
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Definition)`""
    Start-Process PowerShell -Verb RunAs -ArgumentList $arguments
    exit 0
}

Write-Host "🚀================================================================🚀" -ForegroundColor Cyan
Write-Host "🖥️             OPTIMON - INSTALACION AUTOMATICA COMPLETA" -ForegroundColor Cyan
Write-Host "📊                    Sistema Unificado v3.0.0" -ForegroundColor Cyan
Write-Host "🚀================================================================🚀" -ForegroundColor Cyan
Write-Host ""

function Test-Command {
    param($Command)
    try {
        & $Command --version 2>$null | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Wait-ForService {
    param($Url, $Name, $MaxAttempts = 30)
    
    Write-Host "🔄 Esperando que $Name esté listo..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $Name está listo" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "   Intento $i/$MaxAttempts..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "⚠️ $Name no responde, pero continuando..." -ForegroundColor Yellow
    return $false
}

# Paso 1: Verificar Docker
Write-Host "🐳 [1/7] Verificando Docker..." -ForegroundColor Blue
if (-not (Test-Command "docker")) {
    Write-Host "❌ Docker no encontrado" -ForegroundColor Red
    Write-Host "   Instalar Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "✅ Docker encontrado" -ForegroundColor Green

# Paso 2: Verificar Python
Write-Host "🐍 [2/7] Verificando Python..." -ForegroundColor Blue
if (-not (Test-Command "python")) {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "   Instalar Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "✅ Python encontrado" -ForegroundColor Green

# Paso 3: Instalar dependencias
Write-Host "📦 [3/7] Instalando dependencias Python..." -ForegroundColor Blue
try {
    & python -m pip install --upgrade pip --quiet
    & python -m pip install -r requirements.txt --quiet
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
} catch {
    Write-Host "❌ Error instalando dependencias: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Paso 4: Detener servicios previos
Write-Host "🛑 [4/7] Limpiando servicios previos..." -ForegroundColor Blue
try {
    & docker compose down --remove-orphans 2>$null
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servicios previos detenidos" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Algunos servicios no se pudieron detener" -ForegroundColor Yellow
}

# Paso 5: Iniciar servicios Docker
Write-Host "🐳 [5/7] Iniciando servicios Docker..." -ForegroundColor Blue
try {
    & docker compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Error en docker compose"
    }
    Write-Host "✅ Servicios Docker iniciados" -ForegroundColor Green
} catch {
    Write-Host "❌ Error iniciando servicios Docker: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Paso 6: Esperar servicios
Write-Host "⏳ [6/7] Esperando que los servicios estén listos..." -ForegroundColor Blue
Start-Sleep -Seconds 10
Wait-ForService "http://localhost:9090/-/healthy" "Prometheus"
Wait-ForService "http://localhost:3000/api/health" "Grafana"

# Paso 7: Iniciar portal web
Write-Host "🌐 [7/7] Iniciando portal web OptiMon..." -ForegroundColor Blue
try {
    Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Hidden -WorkingDirectory (Get-Location)
    Start-Sleep -Seconds 5
    
    # Verificar portal
    Wait-ForService "http://localhost:5000/api/health" "Portal OptiMon"
    Write-Host "✅ Portal web iniciado" -ForegroundColor Green
} catch {
    Write-Host "❌ Error iniciando portal web: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Abrir navegadores
Write-Host "🌐 Abriendo interfaces de usuario..." -ForegroundColor Blue
Start-Process "http://localhost:5000"
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "🎉================================================================🎉" -ForegroundColor Green
Write-Host "🎯                    INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "🎉================================================================🎉" -ForegroundColor Green
Write-Host ""
Write-Host "📋 ACCESOS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "   🌐 Portal OptiMon:  http://localhost:5000" -ForegroundColor White
Write-Host "   📊 Grafana:         http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "   🔍 Prometheus:      http://localhost:9090" -ForegroundColor White
Write-Host "   🚨 AlertManager:    http://localhost:9093" -ForegroundColor White
Write-Host ""
Write-Host "🚀 FUNCIONALIDADES:" -ForegroundColor Cyan
Write-Host "   ✅ Monitoreo local de tu computadora" -ForegroundColor White
Write-Host "   ✅ Configuración de credenciales Azure" -ForegroundColor White
Write-Host "   ✅ Generación automática de infraestructura" -ForegroundColor White
Write-Host "   ✅ Dashboards de monitoreo avanzados" -ForegroundColor White
Write-Host "   ✅ Sistema de alertas configurado" -ForegroundColor White
Write-Host ""
Write-Host "💡 SIGUIENTE PASO: Accede al portal para configurar Azure" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona Enter para finalizar"