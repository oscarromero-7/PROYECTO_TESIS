# Script de instalación de Node Exporter para Windows
# Ejecutar en PowerShell como Administrador

param(
    [string]$InstallPath = "C:\Program Files\node_exporter",
    [string]$Version = "1.6.1"
)

Write-Host "🚀 Instalando Node Exporter en Windows..." -ForegroundColor Green

# Verificar permisos de administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Error: Este script requiere permisos de administrador" -ForegroundColor Red
    Write-Host "   Ejecuta PowerShell como Administrador e intenta nuevamente" -ForegroundColor Yellow
    exit 1
}

# Variables
$DownloadUrl = "https://github.com/prometheus/node_exporter/releases/download/v$Version/node_exporter-$Version.windows-amd64.tar.gz"
$TempPath = "$env:TEMP\node_exporter"
$ServiceName = "NodeExporter"

Write-Host "📋 Configuración:" -ForegroundColor Cyan
Write-Host "   Versión: $Version" -ForegroundColor White
Write-Host "   Ruta de instalación: $InstallPath" -ForegroundColor White
Write-Host "   Servicio: $ServiceName" -ForegroundColor White

# Crear directorio de instalación
Write-Host "📁 Creando directorio de instalación..." -ForegroundColor Yellow
if (!(Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

# Crear directorio temporal
if (!(Test-Path $TempPath)) {
    New-Item -ItemType Directory -Path $TempPath -Force | Out-Null
}

try {
    # Descargar Node Exporter
    Write-Host "⬇️  Descargando Node Exporter $Version..." -ForegroundColor Yellow
    $ZipPath = "$TempPath\node_exporter.tar.gz"
    
    # Usar Invoke-WebRequest para descargar
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing
    
    # Extraer usando tar (disponible en Windows 10+)
    Write-Host "📦 Extrayendo archivos..." -ForegroundColor Yellow
    Push-Location $TempPath
    tar -xzf "node_exporter.tar.gz"
    
    # Encontrar el directorio extraído
    $ExtractedDir = Get-ChildItem -Directory | Where-Object { $_.Name -like "node_exporter-*" } | Select-Object -First 1
    
    if (!$ExtractedDir) {
        throw "No se pudo encontrar el directorio extraído"
    }
    
    # Copiar el ejecutable
    Write-Host "📋 Instalando binario..." -ForegroundColor Yellow
    Copy-Item "$($ExtractedDir.FullName)\node_exporter.exe" $InstallPath -Force
    Pop-Location
    
    # Verificar que el archivo existe
    $ExePath = "$InstallPath\node_exporter.exe"
    if (!(Test-Path $ExePath)) {
        throw "Error: No se pudo instalar el ejecutable"
    }
    
    # Configurar firewall
    Write-Host "🔥 Configurando Windows Firewall..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port 9100 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        Write-Host "   ✅ Regla de firewall creada para puerto 9100" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Advertencia: No se pudo configurar el firewall automáticamente" -ForegroundColor Yellow
        Write-Host "   💡 Configura manualmente: Windows Defender Firewall > Puerto 9100 TCP" -ForegroundColor Cyan
    }
    
    # Detener servicio existente si existe
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host "🛑 Deteniendo servicio existente..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName -Force
        sc.exe delete $ServiceName | Out-Null
    }
    
    # Crear servicio de Windows
    Write-Host "⚙️  Configurando servicio de Windows..." -ForegroundColor Yellow
    $ServiceArgs = "--web.listen-address=:9100"
    sc.exe create $ServiceName binPath= "`"$ExePath`" $ServiceArgs" start= auto | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "Error creando el servicio de Windows"
    }
    
    # Configurar descripción del servicio
    sc.exe description $ServiceName "Prometheus Node Exporter - Sistema de métricas" | Out-Null
    
    # Iniciar servicio
    Write-Host "🚀 Iniciando servicio Node Exporter..." -ForegroundColor Yellow
    Start-Service -Name $ServiceName
    
    # Verificar estado
    Start-Sleep -Seconds 3
    $Service = Get-Service -Name $ServiceName
    
    if ($Service.Status -eq "Running") {
        Write-Host "✅ Node Exporter instalado y ejecutándose correctamente!" -ForegroundColor Green
        
        # Obtener IP local
        $LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
        
        Write-Host ""
        Write-Host "🎉 ¡Instalación completada!" -ForegroundColor Green
        Write-Host "📋 Información del servidor:" -ForegroundColor Cyan
        Write-Host "   IP: $LocalIP" -ForegroundColor White
        Write-Host "   Puerto: 9100" -ForegroundColor White
        Write-Host "   Métricas: http://${LocalIP}:9100/metrics" -ForegroundColor White
        Write-Host "   Servicio: $ServiceName" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Próximos pasos:" -ForegroundColor Cyan
        Write-Host "   1. Verifica que las métricas están disponibles: http://${LocalIP}:9100/metrics" -ForegroundColor White
        Write-Host "   2. Agrega este servidor a tu configuración OptiMon" -ForegroundColor White
        Write-Host "   3. Ejecuta el setup automático de OptiMon" -ForegroundColor White
        Write-Host "   4. Verifica las métricas en Grafana" -ForegroundColor White
        
        # Intentar verificar métricas
        Write-Host ""
        Write-Host "🔍 Verificando métricas..." -ForegroundColor Yellow
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:9100/metrics" -TimeoutSec 5 -UseBasicParsing
            if ($Response.StatusCode -eq 200) {
                Write-Host "✅ Métricas disponibles y funcionando!" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  Las métricas aún no están disponibles. Espera unos segundos e intenta acceder a http://${LocalIP}:9100/metrics" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "❌ Error: El servicio no está ejecutándose" -ForegroundColor Red
        Write-Host "🔍 Estado del servicio: $($Service.Status)" -ForegroundColor Yellow
        
        # Mostrar logs del evento
        Write-Host "🔍 Verificando logs del sistema..." -ForegroundColor Yellow
        Get-EventLog -LogName System -Source "Service Control Manager" -Newest 5 | Where-Object { $_.Message -like "*$ServiceName*" }
    }
    
} catch {
    Write-Host "❌ Error durante la instalación: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Limpiar archivos temporales
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
    Remove-Item $TempPath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "📚 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver estado: Get-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Reiniciar: Restart-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Detener: Stop-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Desinstalar: sc.exe delete $ServiceName" -ForegroundColor White