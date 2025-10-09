# OptiMon - Comandos de Automatización
# Para Windows PowerShell

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Target = ""
)

function Show-Help {
    Write-Host "🚀 OptiMon - Sistema de Monitoreo" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  setup" -ForegroundColor Green -NoNewline
    Write-Host "          - Despliegue completo del sistema"
    Write-Host "  start" -ForegroundColor Green -NoNewline  
    Write-Host "          - Iniciar servicios"
    Write-Host "  stop" -ForegroundColor Green -NoNewline
    Write-Host "           - Detener servicios"
    Write-Host "  restart" -ForegroundColor Green -NoNewline
    Write-Host "        - Reiniciar servicios"
    Write-Host "  status" -ForegroundColor Green -NoNewline
    Write-Host "         - Ver estado de servicios"
    Write-Host "  logs" -ForegroundColor Green -NoNewline
    Write-Host "           - Ver logs de servicios"
    Write-Host "  test" -ForegroundColor Green -NoNewline
    Write-Host "           - Ejecutar pruebas del sistema"
    Write-Host "  config" -ForegroundColor Green -NoNewline
    Write-Host "         - Regenerar configuraciones"
    Write-Host "  package" -ForegroundColor Green -NoNewline
    Write-Host "        - Crear paquete ZIP para distribución"
    Write-Host "  clean" -ForegroundColor Green -NoNewline
    Write-Host "          - Limpiar datos y contenedores"
    Write-Host ""
    Write-Host "Comandos específicos:" -ForegroundColor Yellow
    Write-Host "  add-server" -ForegroundColor Green -NoNewline
    Write-Host "     - Añadir servidor físico"
    Write-Host "  list-servers" -ForegroundColor Green -NoNewline
    Write-Host "   - Listar servidores configurados"
    Write-Host "  setup-aws" -ForegroundColor Green -NoNewline
    Write-Host "      - Configurar monitoreo AWS"
    Write-Host "  setup-azure" -ForegroundColor Green -NoNewline
    Write-Host "    - Configurar monitoreo Azure"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  .\make.ps1 setup" -ForegroundColor Gray
    Write-Host "  .\make.ps1 logs prometheus" -ForegroundColor Gray
    Write-Host "  .\make.ps1 restart grafana" -ForegroundColor Gray
}

function Invoke-Setup {
    Write-Host "🚀 Iniciando despliegue completo..." -ForegroundColor Cyan
    & .\deploy.ps1
}

function Invoke-Start {
    Write-Host "▶️  Iniciando servicios..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✅ Servicios iniciados" -ForegroundColor Green
}

function Invoke-Stop {
    Write-Host "⏹️  Deteniendo servicios..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Servicios detenidos" -ForegroundColor Green
}

function Invoke-Restart {
    param([string]$Service)
    
    if ($Service) {
        Write-Host "🔄 Reiniciando servicio: $Service" -ForegroundColor Yellow
        docker-compose restart $Service
    } else {
        Write-Host "🔄 Reiniciando todos los servicios..." -ForegroundColor Yellow
        docker-compose restart
    }
    Write-Host "✅ Reinicio completado" -ForegroundColor Green
}

function Show-Status {
    Write-Host "📊 Estado de servicios:" -ForegroundColor Cyan
    docker-compose ps
    
    Write-Host "`n🌐 URLs de acceso:" -ForegroundColor Cyan
    Write-Host "  • Grafana:      http://localhost:3000" -ForegroundColor White
    Write-Host "  • Prometheus:   http://localhost:9090" -ForegroundColor White
    Write-Host "  • AlertManager: http://localhost:9093" -ForegroundColor White
}

function Show-Logs {
    param([string]$Service)
    
    if ($Service) {
        Write-Host "📋 Logs de $Service" -ForegroundColor Cyan
        docker-compose logs -f $Service
    } else {
        Write-Host "📋 Logs de todos los servicios" -ForegroundColor Cyan
        docker-compose logs -f
    }
}

function Invoke-Test {
    Write-Host "🧪 Ejecutando pruebas del sistema..." -ForegroundColor Cyan
    python test_system.py
}

function Invoke-Config {
    Write-Host "⚙️  Regenerando configuraciones..." -ForegroundColor Cyan
    python scripts/setup_prometheus.py
    Write-Host "🔄 Reiniciando Prometheus..." -ForegroundColor Yellow
    docker-compose restart prometheus
    Write-Host "✅ Configuración actualizada" -ForegroundColor Green
}

function Invoke-Package {
    Write-Host "📦 Creando paquete de distribución..." -ForegroundColor Cyan
    python create_package.py
}

function Invoke-Clean {
    Write-Host "🧹 Limpiando sistema..." -ForegroundColor Yellow
    
    $response = Read-Host "¿Estás seguro? Esto eliminará todos los datos (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "🗑️  Eliminando contenedores y volúmenes..." -ForegroundColor Red
        docker-compose down -v --remove-orphans
        docker system prune -f
        Write-Host "✅ Limpieza completada" -ForegroundColor Green
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function Invoke-AddServer {
    Write-Host "🖥️  Añadir servidor físico" -ForegroundColor Cyan
    & .\add_server.ps1
}

function Invoke-ListServers {
    Write-Host "📋 Servidores configurados:" -ForegroundColor Cyan
    python scripts/add_physical_server.py list
}

function Invoke-SetupAWS {
    Write-Host "☁️  Configurando monitoreo AWS..." -ForegroundColor Cyan
    python scripts/setup_aws_monitoring.py
}

function Invoke-SetupAzure {
    Write-Host "☁️  Configurando monitoreo Azure..." -ForegroundColor Cyan
    python scripts/setup_azure_monitoring.py
}

# Función principal
switch ($Command.ToLower()) {
    "setup" { Invoke-Setup }
    "start" { Invoke-Start }
    "stop" { Invoke-Stop }
    "restart" { Invoke-Restart -Service $Target }
    "status" { Show-Status }
    "logs" { Show-Logs -Service $Target }
    "test" { Invoke-Test }
    "config" { Invoke-Config }
    "package" { Invoke-Package }
    "clean" { Invoke-Clean }
    "add-server" { Invoke-AddServer }
    "list-servers" { Invoke-ListServers }
    "setup-aws" { Invoke-SetupAWS }
    "setup-azure" { Invoke-SetupAzure }
    "help" { Show-Help }
    "" { Show-Help }
    default {
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Write-Host "Usa '.\make.ps1 help' para ver comandos disponibles" -ForegroundColor Yellow
    }
}