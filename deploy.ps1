# OptiMon Deployment Script para Windows
# Automated deployment for infrastructure monitoring

param(
    [switch]$SkipCredentials,
    [switch]$Verbose
)

# Configurar colores para salida
$Host.UI.RawUI.BackgroundColor = "Black"
$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Emoji = ""
    )
    
    if ($Emoji) {
        Write-Host "$Emoji $Message" -ForegroundColor $Color
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Write-Header {
    Write-ColorOutput "🚀 OptiMon - Sistema de Monitoreo de Infraestructura" "Cyan"
    Write-ColorOutput "==================================================" "Cyan"
    Write-Host ""
}

function Test-Prerequisites {
    Write-ColorOutput "📋 Verificando prerrequisitos..." "Yellow"
    
    # Verificar Docker
    try {
        $dockerVersion = docker --version 2>$null
        if (-not $dockerVersion) {
            throw "Docker no encontrado"
        }
        Write-ColorOutput "✅ Docker está instalado: $dockerVersion" "Green"
    }
    catch {
        Write-ColorOutput "❌ Docker no está instalado" "Red"
        Write-ColorOutput "Por favor instala Docker Desktop antes de continuar" "Red"
        exit 1
    }
    
    # Verificar Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if (-not $composeVersion) {
            throw "Docker Compose no encontrado"
        }
        Write-ColorOutput "✅ Docker Compose está instalado: $composeVersion" "Green"
    }
    catch {
        Write-ColorOutput "❌ Docker Compose no está instalado" "Red"
        Write-ColorOutput "Por favor instala Docker Compose antes de continuar" "Red"
        exit 1
    }
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            $pythonVersion = python3 --version 2>$null
        }
        if (-not $pythonVersion) {
            throw "Python no encontrado"
        }
        Write-ColorOutput "✅ Python está instalado: $pythonVersion" "Green"
    }
    catch {
        Write-ColorOutput "❌ Python no está instalado" "Red"
        Write-ColorOutput "Por favor instala Python 3.8+ antes de continuar" "Red"
        exit 1
    }
    
    Write-ColorOutput "✅ Todos los prerrequisitos están instalados" "Green"
    Write-Host ""
}

function Install-PythonDependencies {
    Write-ColorOutput "📦 Instalando dependencias Python..." "Yellow"
    
    if (Test-Path "requirements.txt") {
        try {
            & python -m pip install -r requirements.txt
            Write-ColorOutput "✅ Dependencias Python instaladas" "Green"
        }
        catch {
            Write-ColorOutput "⚠️  Error instalando dependencias Python" "Yellow"
        }
    } else {
        Write-ColorOutput "⚠️  Archivo requirements.txt no encontrado" "Yellow"
    }
    Write-Host ""
}

function Setup-Credentials {
    if ($SkipCredentials) {
        Write-ColorOutput "⏭️  Saltando configuración de credenciales" "Yellow"
        return
    }
    
    Write-ColorOutput "🔐 Configurando credenciales..." "Yellow"
    
    $simpleCredentials = Test-Path "config/credentials.simple.yml"
    
    if (-not $simpleCredentials) {
        Write-ColorOutput "⚠️  No se encontró archivo de credenciales simplificado" "Yellow"
        Write-Host "Por favor configura tus credenciales de nube en:"
        Write-Host "  - config/credentials.simple.yml"
        Write-Host ""
        Write-Host "Usa el archivo config/credentials.simple.yml como base"
        Write-Host "Solo necesitas completar las credenciales de AWS o Azure"
        
        $continue = Read-Host "¿Quieres continuar sin credenciales de nube? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    } else {
        Write-ColorOutput "✅ Archivo de credenciales simplificado encontrado" "Green"
        Write-ColorOutput "El sistema detectará automáticamente toda la infraestructura" "Cyan"
    }
    Write-Host ""
}

function Setup-Prometheus {
    Write-ColorOutput "⚙️  Configurando Prometheus..." "Yellow"
    
    # Crear configuración básica si no existe
    if (-not (Test-Path "config/prometheus/prometheus.yml")) {
        Write-ColorOutput "📝 Creando configuración básica de Prometheus" "Cyan"
        
        # Crear directorio
        New-Item -Path "config/prometheus" -ItemType Directory -Force | Out-Null
        
        # Configuración básica inicial
        $basicConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"@
        
        $basicConfig | Out-File -FilePath "config/prometheus/prometheus.yml" -Encoding UTF8
        
        # Crear reglas de alertas básicas
        $alertRules = @"
groups:
  - name: basic-alerts
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Instancia no disponible"
          description: "La instancia {{ `$labels.instance }} no responde"
"@
        
        $alertRules | Out-File -FilePath "config/prometheus/alert.rules.yml" -Encoding UTF8
    }
    
    Write-ColorOutput "✅ Prometheus configurado" "Green"
    Write-Host ""
}

function Start-Services {
    Write-ColorOutput "🐳 Iniciando servicios Docker..." "Yellow"
    
    # Detener servicios existentes si están corriendo
    try {
        & docker-compose down 2>$null
    }
    catch {
        # Ignorar errores si no hay servicios corriendo
    }
    
    # Construir e iniciar servicios
    & docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Servicios iniciados exitosamente" "Green"
    } else {
        Write-ColorOutput "❌ Error iniciando servicios Docker" "Red"
        exit 1
    }
    Write-Host ""
}

function Test-Services {
    Write-ColorOutput "🔍 Verificando servicios..." "Yellow"
    
    # Esperar unos segundos para que los servicios inicien
    Start-Sleep -Seconds 10
    
    $services = @(
        @{Name = "Prometheus"; Port = 9090},
        @{Name = "Grafana"; Port = 3000},
        @{Name = "AlertManager"; Port = 9093}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)" -TimeoutSec 5 -ErrorAction Stop
            Write-ColorOutput "✅ $($service.Name) está funcionando en puerto $($service.Port)" "Green"
        }
        catch {
            Write-ColorOutput "❌ $($service.Name) no responde en puerto $($service.Port)" "Red"
        }
    }
    Write-Host ""
}

function Start-AutoDiscovery {
    Write-ColorOutput "🤖 Iniciando descubrimiento automático..." "Yellow"
    
    if (Test-Path "config/credentials.simple.yml") {
        Write-ColorOutput "🔄 Ejecutando configuración 100% automática..." "Cyan"
        Write-ColorOutput "Esto detectará e instalará Node Exporter automáticamente" "White"
        & python scripts/auto_setup.py
    } else {
        Write-ColorOutput "⚠️  Configuración manual disponible:" "Yellow"
        
        if (Test-Path "config/aws-credentials.yml") {
            Write-ColorOutput "🔄 Configurando monitoreo AWS..." "Cyan"
            & python scripts/setup_aws_monitoring.py
        }
        
        if (Test-Path "config/azure-credentials.yml") {
            Write-ColorOutput "🔄 Configurando monitoreo Azure..." "Cyan"
            & python scripts/setup_azure_monitoring.py
        }
    }
    
    Write-ColorOutput "✅ Configuración automática completada" "Green"
    Write-Host ""
}

function Show-FinalInfo {
    Write-Host ""
    Write-ColorOutput "🎉 ¡Despliegue completado exitosamente!" "Green"
    Write-ColorOutput "======================================" "Green"
    Write-Host ""
    Write-ColorOutput "📊 Accede a los servicios:" "Cyan"
    Write-Host "  • Grafana:      http://localhost:3000 (admin/admin)"
    Write-Host "  • Prometheus:   http://localhost:9090"
    Write-Host "  • AlertManager: http://localhost:9093"
    Write-Host ""
    Write-ColorOutput "🛠️  Comandos útiles:" "Cyan"
    Write-Host "  • Ver logs:           docker-compose logs -f"
    Write-Host "  • Detener servicios:  docker-compose down"
    Write-Host "  • Reiniciar:          docker-compose restart"
    Write-Host "  • Añadir servidor:    .\scripts\add_server.ps1"
    Write-Host ""
    Write-ColorOutput "📖 Para más información, consulta README.md" "Yellow"
}

function Main {
    try {
        Write-Header
        Test-Prerequisites
        Install-PythonDependencies
        Setup-Credentials
        Setup-Prometheus
        Start-Services
        Test-Services
        Start-AutoDiscovery
        Show-FinalInfo
    }
    catch {
        Write-ColorOutput "❌ Error durante el despliegue: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# Ejecutar función principal
Main