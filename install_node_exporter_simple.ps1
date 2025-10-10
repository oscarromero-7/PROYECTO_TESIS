# Script de instalación rápida de Node Exporter para Windows
# Ejecutar en PowerShell como Administrador en la máquina 172.20.10.11

param(
    [string]$PrometheusServer = "172.20.10.1"  # IP del servidor OptiMon
)

Write-Host "🚀 Instalación automática de Node Exporter" -ForegroundColor Green
Write-Host "📍 Configurando para servidor Prometheus: $PrometheusServer" -ForegroundColor Cyan

# Verificar permisos de administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Este script requiere permisos de administrador" -ForegroundColor Red
    Write-Host "   Ejecuta PowerShell como Administrador e intenta nuevamente" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar..."
    exit 1
}

try {
    # Variables
    $Version = "1.6.1"
    $InstallPath = "C:\Program Files\node_exporter"
    $ServiceName = "NodeExporter"
    $Port = 9100
    
    Write-Host "📋 Configuración:" -ForegroundColor Cyan
    Write-Host "   Versión: $Version" -ForegroundColor White
    Write-Host "   Directorio: $InstallPath" -ForegroundColor White
    Write-Host "   Puerto: $Port" -ForegroundColor White
    Write-Host "   Servicio: $ServiceName" -ForegroundColor White
    
    # Verificar si ya está instalado
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        $Service = Get-Service -Name $ServiceName
        if ($Service.Status -eq "Running") {
            Write-Host "✅ Node Exporter ya está instalado y ejecutándose" -ForegroundColor Green
            Write-Host "📊 Métricas disponibles en: http://localhost:$Port/metrics" -ForegroundColor Cyan
            Read-Host "Presiona Enter para continuar..."
            exit 0
        }
    }
    
    # Crear directorio de instalación
    Write-Host "📁 Creando directorio de instalación..." -ForegroundColor Yellow
    if (!(Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    
    # Descargar Node Exporter
    Write-Host "⬇️  Descargando Node Exporter $Version..." -ForegroundColor Yellow
    $DownloadUrl = "https://github.com/prometheus/node_exporter/releases/download/v$Version/node_exporter-$Version.windows-amd64.tar.gz"
    $TempPath = "$env:TEMP\node_exporter.tar.gz"
    
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempPath -UseBasicParsing
    Write-Host "✅ Descarga completada" -ForegroundColor Green
    
    # Extraer archivos
    Write-Host "📦 Extrayendo archivos..." -ForegroundColor Yellow
    Push-Location $env:TEMP
    tar -xzf "node_exporter.tar.gz"
    
    $ExtractedDir = Get-ChildItem -Directory | Where-Object { $_.Name -like "node_exporter-*" } | Select-Object -First 1
    if (!$ExtractedDir) {
        throw "No se pudo encontrar el directorio extraído"
    }
    
    # Copiar ejecutable
    Copy-Item "$($ExtractedDir.FullName)\node_exporter.exe" $InstallPath -Force
    Pop-Location
    Write-Host "✅ Archivos extraídos" -ForegroundColor Green
    
    # Configurar firewall
    Write-Host "🔥 Configurando Windows Firewall..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port $Port -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        Write-Host "✅ Firewall configurado para puerto $Port" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  No se pudo configurar el firewall automáticamente" -ForegroundColor Yellow
    }
    
    # Detener servicio existente
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Write-Host "🛑 Deteniendo servicio existente..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName -Force
        sc.exe delete $ServiceName | Out-Null
    }
    
    # Crear servicio
    Write-Host "⚙️  Creando servicio de Windows..." -ForegroundColor Yellow
    $ExePath = "$InstallPath\node_exporter.exe"
    $ServiceArgs = "--web.listen-address=:$Port"
    sc.exe create $ServiceName binPath= "`"$ExePath`" $ServiceArgs" start= auto | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        sc.exe description $ServiceName "Prometheus Node Exporter - Métricas del sistema" | Out-Null
        Start-Service -Name $ServiceName
        Write-Host "✅ Servicio creado e iniciado" -ForegroundColor Green
    } else {
        throw "Error creando el servicio"
    }
    
    # Verificar instalación
    Write-Host "🔍 Verificando instalación..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    $Service = Get-Service -Name $ServiceName
    if ($Service.Status -eq "Running") {
        Write-Host "✅ Node Exporter instalado correctamente!" -ForegroundColor Green
        
        # Obtener IP local
        $LocalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
        
        Write-Host ""
        Write-Host "🎉 ¡Instalación completada exitosamente!" -ForegroundColor Green
        Write-Host "📋 Información del servidor:" -ForegroundColor Cyan
        Write-Host "   IP local: $LocalIP" -ForegroundColor White
        Write-Host "   Puerto: $Port" -ForegroundColor White
        Write-Host "   Métricas: http://$LocalIP`:$Port/metrics" -ForegroundColor White
        Write-Host "   Servicio: $ServiceName" -ForegroundColor White
        
        # Probar métricas
        Write-Host ""
        Write-Host "🔍 Probando métricas..." -ForegroundColor Yellow
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:$Port/metrics" -TimeoutSec 5 -UseBasicParsing
            if ($Response.StatusCode -eq 200) {
                Write-Host "✅ Métricas funcionando correctamente!" -ForegroundColor Green
                
                # Mostrar algunas métricas de ejemplo
                $Metrics = $Response.Content -split "`n" | Where-Object { $_ -like "# HELP*" } | Select-Object -First 5
                Write-Host ""
                Write-Host "📊 Ejemplo de métricas disponibles:" -ForegroundColor Cyan
                foreach ($Metric in $Metrics) {
                    Write-Host "   $Metric" -ForegroundColor White
                }
            }
        } catch {
            Write-Host "⚠️  Las métricas aún no están disponibles. Espera unos segundos." -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "💡 Próximos pasos:" -ForegroundColor Cyan
        Write-Host "   1. Las métricas están disponibles en: http://$LocalIP`:$Port/metrics" -ForegroundColor White
        Write-Host "   2. OptiMon detectará automáticamente este servidor" -ForegroundColor White
        Write-Host "   3. Verifica en Grafana: http://$PrometheusServer`:3000" -ForegroundColor White
        
    } else {
        Write-Host "❌ Error: El servicio no está ejecutándose" -ForegroundColor Red
        Write-Host "Estado del servicio: $($Service.Status)" -ForegroundColor Yellow
        
        # Mostrar logs
        Write-Host "🔍 Verificando logs del sistema..." -ForegroundColor Yellow
        Get-EventLog -LogName System -Source "Service Control Manager" -Newest 5 | Where-Object { $_.Message -like "*$ServiceName*" } | Format-Table -AutoSize
    }
    
} catch {
    Write-Host "❌ Error durante la instalación: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Limpiar archivos temporales
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
    Remove-Item "$env:TEMP\node_exporter*" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "📚 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver estado: Get-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Reiniciar: Restart-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Detener: Stop-Service -Name $ServiceName" -ForegroundColor White
Write-Host "   Desinstalar: sc.exe delete $ServiceName" -ForegroundColor White

Read-Host "Presiona Enter para continuar..."