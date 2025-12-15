# Script para verificar, modernizar y corregir todos los dashboards de Grafana
# Autor: OptiMon System
# Fecha: 2025-12-14

$ErrorActionPreference = "Continue"

# Configuración
$GRAFANA_URL = "http://localhost:3000"
$GRAFANA_USER = "admin"
$GRAFANA_PASS = "admin"
$DATASOURCE_UID = "af24x2bn7ezuof"

# Headers para autenticación
$headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${GRAFANA_USER}:${GRAFANA_PASS}"))
    "Content-Type" = "application/json"
}

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       🚀 OptiMon Dashboard Modernization Tool 🚀           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Obtener todos los dashboards
Write-Host "📊 Obteniendo lista de dashboards..." -ForegroundColor Yellow
$dashboards = Invoke-RestMethod -Uri "$GRAFANA_URL/api/search?type=dash-db" -Headers $headers
Write-Host "   ✅ Encontrados: $($dashboards.Count) dashboards`n" -ForegroundColor Green

# 2. Obtener información de Prometheus
Write-Host "🎯 Verificando targets activos en Prometheus..." -ForegroundColor Yellow
$prometheusTargets = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets"
$activeTargets = $prometheusTargets.data.activeTargets | Where-Object { $_.health -eq 'up' }
$activeJobs = $activeTargets | Select-Object -ExpandProperty labels | Select-Object -ExpandProperty job -Unique

Write-Host "   ✅ Jobs activos:" -ForegroundColor Green
foreach ($job in $activeJobs) {
    $targetCount = ($activeTargets | Where-Object { $_.labels.job -eq $job }).Count
    Write-Host "      - $job ($targetCount targets)" -ForegroundColor Cyan
}
Write-Host ""

# 3. Crear directorio de respaldo
$backupDir = "c:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\3-CODIGO-GENERADO\dashboards_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "📁 Directorio de respaldo creado: $backupDir`n" -ForegroundColor Green

# 4. Dashboards prioritarios a corregir
$priorityDashboards = @{
    "optimon-windows-real" = @{
        name = "🖥️ OptiMon - Tu Computadora Windows (MODERNIZADO)"
        job = "windows_local"
        description = "Dashboard modernizado para monitoreo de Windows en tiempo real"
    }
    "optimon-local" = @{
        name = "🏠 OptiMon - Sistema Local Unificado (MODERNIZADO)"
        job = "windows_local"
        description = "Dashboard unificado para monitoreo local completo"
    }
    "optimon-aws-working" = @{
        name = "☁️ OptiMon - AWS Instances (MODERNIZADO)"
        job = "aws_instances"
        description = "Dashboard modernizado para instancias AWS"
    }
    "optimon-azure-working" = @{
        name = "☁️ OptiMon - Azure Instances (MODERNIZADO)"
        job = "azure_instances"
        description = "Dashboard modernizado para instancias Azure"
    }
    "optimon-executive-real" = @{
        name = "📊 OptiMon Executive - Resumen Ejecutivo (MODERNIZADO)"
        job = "all"
        description = "Dashboard ejecutivo con resumen de toda la infraestructura"
    }
}

# 5. Función para modernizar un dashboard
function Modernize-Dashboard {
    param(
        [string]$uid,
        [string]$newTitle,
        [string]$targetJob,
        [string]$description
    )
    
    try {
        Write-Host "   🔧 Procesando: $newTitle" -ForegroundColor Yellow
        
        # Obtener dashboard actual
        $response = Invoke-RestMethod -Uri "$GRAFANA_URL/api/dashboards/uid/$uid" -Headers $headers
        $dashboard = $response.dashboard
        
        # Guardar backup
        $backupFile = Join-Path $backupDir "$uid.json"
        $dashboard | ConvertTo-Json -Depth 100 | Out-File -FilePath $backupFile -Encoding UTF8
        
        # Actualizar metadatos
        $dashboard.title = $newTitle
        if ($description) {
            $dashboard.description = $description
        }
        
        # Configurar tema moderno
        $dashboard.editable = $true
        $dashboard.graphTooltip = 1  # Shared crosshair
        $dashboard.refresh = "30s"
        
        if (-not $dashboard.time) {
            $dashboard.time = @{
                from = "now-6h"
                to = "now"
            }
        }
        
        # Contador de paneles corregidos
        $panelsFixed = 0
        
        # Corregir todos los paneles
        foreach ($panel in $dashboard.panels) {
            # Configurar datasource en el panel
            $panel.datasource = @{
                type = "prometheus"
                uid = $DATASOURCE_UID
            }
            
            # Corregir targets
            if ($panel.targets) {
                foreach ($target in $panel.targets) {
                    # Configurar datasource en el target
                    $target.datasource = @{
                        type = "prometheus"
                        uid = $DATASOURCE_UID
                    }
                    
                    # Corregir expresiones de queries
                    if ($target.expr) {
                        $originalExpr = $target.expr
                        
                        # Reemplazar jobs incorrectos
                        $target.expr = $target.expr -replace 'windows_exporter_local', 'windows_local'
                        $target.expr = $target.expr -replace 'node_exporter', 'aws_instances'
                        $target.expr = $target.expr -replace 'azure_vm', 'azure_instances'
                        
                        if ($originalExpr -ne $target.expr) {
                            $panelsFixed++
                        }
                    }
                    
                    # Configurar formato de leyenda
                    if (-not $target.legendFormat) {
                        $target.legendFormat = "{{instance}}"
                    }
                    
                    # Configurar intervalo
                    if (-not $target.interval) {
                        $target.interval = "30s"
                    }
                }
            }
            
            # Mejorar apariencia de paneles
            if ($panel.type -eq "graph" -or $panel.type -eq "timeseries") {
                if (-not $panel.fieldConfig) {
                    $panel.fieldConfig = @{
                        defaults = @{
                            custom = @{
                                lineWidth = 2
                                fillOpacity = 10
                                showPoints = "never"
                            }
                        }
                    }
                }
            }
            
            # Configurar thresholds para gauges
            if ($panel.type -eq "gauge" -or $panel.type -eq "stat") {
                if (-not $panel.fieldConfig) {
                    $panel.fieldConfig = @{
                        defaults = @{
                            thresholds = @{
                                mode = "absolute"
                                steps = @(
                                    @{ value = $null; color = "green" }
                                    @{ value = 70; color = "yellow" }
                                    @{ value = 90; color = "red" }
                                )
                            }
                            unit = "percent"
                        }
                    }
                }
            }
        }
        
        # Actualizar en Grafana
        $updatePayload = @{
            dashboard = $dashboard
            overwrite = $true
            message = "Modernización automática - Datasources y queries corregidos"
        } | ConvertTo-Json -Depth 100
        
        $updateResponse = Invoke-RestMethod -Uri "$GRAFANA_URL/api/dashboards/db" -Method Post -Headers $headers -Body $updatePayload
        
        Write-Host "      ✅ Dashboard actualizado exitosamente" -ForegroundColor Green
        Write-Host "      📊 Paneles corregidos: $panelsFixed" -ForegroundColor Cyan
        Write-Host "      🔗 URL: $GRAFANA_URL/d/$($updateResponse.uid)/`n" -ForegroundColor White
        
        return @{
            success = $true
            uid = $updateResponse.uid
            panelsFixed = $panelsFixed
        }
        
    } catch {
        Write-Host "      ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            success = $false
            error = $_.Exception.Message
        }
    }
}

# 6. Procesar dashboards prioritarios
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║           🔧 MODERNIZANDO DASHBOARDS PRIORITARIOS           ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

$results = @()

foreach ($dashUid in $priorityDashboards.Keys) {
    $config = $priorityDashboards[$dashUid]
    $result = Modernize-Dashboard -uid $dashUid -newTitle $config.name -targetJob $config.job -description $config.description
    $results += @{
        uid = $dashUid
        name = $config.name
        result = $result
    }
}

# 7. Crear dashboard maestro de monitoreo
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        📊 CREANDO DASHBOARD MAESTRO DE MONITOREO           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$masterDashboard = @{
    dashboard = @{
        uid = "optimon-master-modern"
        title = "🎯 OptiMon - Dashboard Maestro (TODOS LOS SISTEMAS)"
        tags = @("optimon", "master", "overview")
        timezone = "browser"
        editable = $true
        graphTooltip = 1
        time = @{
            from = "now-6h"
            to = "now"
        }
        refresh = "30s"
        panels = @(
            # Panel de título
            @{
                gridPos = @{ h = 3; w = 24; x = 0; y = 0 }
                id = 1
                title = "🎯 OPTIMON - CENTRO DE CONTROL MAESTRO"
                type = "text"
                options = @{
                    mode = "markdown"
                    content = @"
# 🚀 OptiMon - Sistema de Monitoreo Unificado

## ✅ Sistemas Activos
- **🖥️ Windows Local**: Monitoreando tu computadora
- **☁️ AWS Instances**: $($activeTargets | Where-Object {$_.labels.job -eq 'aws_instances'} | Measure-Object | Select-Object -ExpandProperty Count) instancias activas
- **🔧 Prometheus**: Sistema de métricas operacional

## 📊 Dashboards Disponibles
- [🖥️ Windows Local](d/optimon-windows-real/)
- [☁️ AWS Instances](d/optimon-aws-working/)
- [📊 Executive Summary](d/optimon-executive-real/)

---
**Última actualización**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@
                }
            }
            
            # CPU Windows
            @{
                datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                gridPos = @{ h = 8; w = 8; x = 0; y = 3 }
                id = 2
                title = "🖥️ CPU - Windows Local"
                type = "gauge"
                targets = @(
                    @{
                        datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                        expr = '100 - (avg(rate(windows_cpu_time_total{mode="idle",job="windows_local"}[2m])) * 100)'
                        refId = "A"
                        legendFormat = "CPU Usage"
                    }
                )
                options = @{
                    orientation = "auto"
                    showThresholdLabels = $false
                    showThresholdMarkers = $true
                }
                fieldConfig = @{
                    defaults = @{
                        unit = "percent"
                        min = 0
                        max = 100
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ value = $null; color = "green" }
                                @{ value = 70; color = "yellow" }
                                @{ value = 90; color = "red" }
                            )
                        }
                    }
                }
            }
            
            # Memoria Windows
            @{
                datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                gridPos = @{ h = 8; w = 8; x = 8; y = 3 }
                id = 3
                title = "💾 Memoria - Windows Local"
                type = "gauge"
                targets = @(
                    @{
                        datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                        expr = '100 - ((windows_memory_available_bytes{job="windows_local"} / windows_physical_memory_total_bytes{job="windows_local"}) * 100)'
                        refId = "A"
                        legendFormat = "Memory Usage"
                    }
                )
                options = @{
                    orientation = "auto"
                    showThresholdLabels = $false
                    showThresholdMarkers = $true
                }
                fieldConfig = @{
                    defaults = @{
                        unit = "percent"
                        min = 0
                        max = 100
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ value = $null; color = "green" }
                                @{ value = 70; color = "yellow" }
                                @{ value = 90; color = "red" }
                            )
                        }
                    }
                }
            }
            
            # Disco Windows
            @{
                datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                gridPos = @{ h = 8; w = 8; x = 16; y = 3 }
                id = 4
                title = "💽 Disco C: - Windows Local"
                type = "gauge"
                targets = @(
                    @{
                        datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                        expr = '100 - ((windows_logical_disk_free_bytes{job="windows_local",volume="C:"} / windows_logical_disk_size_bytes{job="windows_local",volume="C:"}) * 100)'
                        refId = "A"
                        legendFormat = "Disk Usage"
                    }
                )
                options = @{
                    orientation = "auto"
                    showThresholdLabels = $false
                    showThresholdMarkers = $true
                }
                fieldConfig = @{
                    defaults = @{
                        unit = "percent"
                        min = 0
                        max = 100
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ value = $null; color = "green" }
                                @{ value = 70; color = "yellow" }
                                @{ value = 90; color = "red" }
                            )
                        }
                    }
                }
            }
            
            # Gráfico de CPU histórico
            @{
                datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                gridPos = @{ h = 8; w = 24; x = 0; y = 11 }
                id = 5
                title = "📈 CPU Usage - Histórico (6 horas)"
                type = "timeseries"
                targets = @(
                    @{
                        datasource = @{ type = "prometheus"; uid = $DATASOURCE_UID }
                        expr = '100 - (avg(rate(windows_cpu_time_total{mode="idle",job="windows_local"}[2m])) * 100)'
                        refId = "A"
                        legendFormat = "Windows Local CPU"
                    }
                )
                fieldConfig = @{
                    defaults = @{
                        custom = @{
                            lineWidth = 2
                            fillOpacity = 10
                            showPoints = "never"
                            spanNulls = $true
                        }
                        unit = "percent"
                        min = 0
                        max = 100
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ value = $null; color = "green" }
                                @{ value = 70; color = "yellow" }
                                @{ value = 90; color = "red" }
                            )
                        }
                    }
                }
                options = @{
                    tooltip = @{
                        mode = "multi"
                        sort = "none"
                    }
                    legend = @{
                        displayMode = "list"
                        placement = "bottom"
                        calcs = @("mean", "max", "last")
                    }
                }
            }
        )
    }
    overwrite = $true
    message = "Dashboard Maestro Modernizado - Creación Automática"
}

try {
    $masterPayload = $masterDashboard | ConvertTo-Json -Depth 100
    $masterResponse = Invoke-RestMethod -Uri "$GRAFANA_URL/api/dashboards/db" -Method Post -Headers $headers -Body $masterPayload
    Write-Host "   ✅ Dashboard Maestro creado exitosamente!" -ForegroundColor Green
    Write-Host "   🔗 URL: $GRAFANA_URL/d/$($masterResponse.uid)/`n" -ForegroundColor White
} catch {
    Write-Host "   ❌ Error al crear Dashboard Maestro: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Resumen final
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   📊 RESUMEN FINAL                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "✅ Dashboards procesados: $($results.Count)" -ForegroundColor Green
$successCount = ($results | Where-Object { $_.result.success }).Count
Write-Host "✅ Exitosos: $successCount" -ForegroundColor Green
Write-Host "❌ Fallidos: $($results.Count - $successCount)" -ForegroundColor Yellow

Write-Host "`n📁 Backups guardados en: $backupDir" -ForegroundColor Cyan

Write-Host "`n🎯 DASHBOARDS PRINCIPALES MODERNIZADOS:`n" -ForegroundColor Magenta
Write-Host "   🖥️  Windows Local:    $GRAFANA_URL/d/optimon-windows-real/" -ForegroundColor White
Write-Host "   🏠  Sistema Local:    $GRAFANA_URL/d/optimon-local/" -ForegroundColor White
Write-Host "   ☁️   AWS Instances:   $GRAFANA_URL/d/optimon-aws-working/" -ForegroundColor White
Write-Host "   📊  Dashboard Maestro: $GRAFANA_URL/d/optimon-master-modern/" -ForegroundColor White

Write-Host "`n✨ ¡Modernización completada exitosamente!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
