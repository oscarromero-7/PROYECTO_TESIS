#!/usr/bin/env pwsh
<#
.SYNOPSIS
    OptiMon - Configuración Automática Completa
.DESCRIPTION
    Script PowerShell que configura automáticamente todo el sistema de monitoreo OptiMon
.EXAMPLE
    .\setup_automatico.ps1
#>

param(
    [switch]$Force = $false
)

# Configuración de colores
$Host.UI.RawUI.ForegroundColor = "White"

function Write-Step {
    param(
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR", "HEADER")]
        [string]$Type = "INFO"
    )
    
    $colors = @{
        "INFO"    = "Cyan"
        "SUCCESS" = "Green" 
        "WARNING" = "Yellow"
        "ERROR"   = "Red"
        "HEADER"  = "Magenta"
    }
    
    $icons = @{
        "INFO"    = "ℹ️"
        "SUCCESS" = "✅"
        "WARNING" = "⚠️"
        "ERROR"   = "❌"
        "HEADER"  = "🚀"
    }
    
    Write-Host "$($icons[$Type]) $Message" -ForegroundColor $colors[$Type]
}

function Test-ServiceAvailable {
    param(
        [string]$Url,
        [int]$MaxAttempts = 20,
        [int]$DelaySeconds = 3
    )
    
    Write-Step "Esperando servicio en $Url..." -Type "INFO"
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Step "Servicio disponible en $Url" -Type "SUCCESS"
                return $true
            }
        }
        catch {
            # Continuar intentando
        }
        
        if ($i -lt $MaxAttempts) {
            Start-Sleep -Seconds $DelaySeconds
        }
    }
    
    Write-Step "Servicio no disponible en $Url después de $MaxAttempts intentos" -Type "WARNING"
    return $false
}

function Stop-ExistingServices {
    Write-Step "Deteniendo servicios existentes..." -Type "HEADER"
    
    # Detener procesos Python
    try {
        Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Step "Procesos Python detenidos" -Type "SUCCESS"
    }
    catch {
        Write-Step "No hay procesos Python ejecutándose" -Type "INFO"
    }
    
    # Detener Windows Exporter
    try {
        Get-Process -Name "windows_exporter" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Step "Windows Exporter detenido" -Type "SUCCESS"
    }
    catch {
        Write-Step "Windows Exporter no estaba ejecutándose" -Type "INFO"
    }
    
    # Detener contenedores Docker
    try {
        docker compose down 2>$null
        Write-Step "Contenedores Docker detenidos" -Type "SUCCESS"
    }
    catch {
        Write-Step "Error deteniendo contenedores Docker" -Type "WARNING"
    }
    
    Start-Sleep -Seconds 3
}

function Start-DockerServices {
    Write-Step "Iniciando servicios Docker..." -Type "HEADER"
    
    # Verificar Docker
    try {
        $dockerVersion = docker --version 2>$null
        Write-Step "Docker disponible: $dockerVersion" -Type "SUCCESS"
    }
    catch {
        Write-Step "Docker no está disponible" -Type "ERROR"
        return $false
    }
    
    # Iniciar servicios
    try {
        docker compose up -d
        Write-Step "Servicios Docker iniciados" -Type "SUCCESS"
    }
    catch {
        Write-Step "Error iniciando servicios Docker" -Type "ERROR"
        return $false
    }
    
    Start-Sleep -Seconds 15
    
    # Verificar servicios
    $services = @(
        @{ Url = "http://localhost:9090"; Name = "Prometheus" },
        @{ Url = "http://localhost:3000"; Name = "Grafana" },
        @{ Url = "http://localhost:9093"; Name = "AlertManager" }
    )
    
    foreach ($service in $services) {
        if (Test-ServiceAvailable -Url $service.Url -MaxAttempts 10) {
            Write-Step "$($service.Name) iniciado correctamente" -Type "SUCCESS"
        }
        else {
            Write-Step "Error iniciando $($service.Name)" -Type "ERROR"
            return $false
        }
    }
    
    return $true
}

function Start-OptiMonPortal {
    Write-Step "Iniciando portal OptiMon..." -Type "HEADER"
    
    # Iniciar servidor en segundo plano
    try {
        $job = Start-Job -ScriptBlock {
            Set-Location "C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO"
            python app.py
        } -Name "OptiMonServer"
        
        Write-Step "Servidor OptiMon iniciado en segundo plano (Job ID: $($job.Id))" -Type "SUCCESS"
    }
    catch {
        Write-Step "Error iniciando servidor OptiMon" -Type "ERROR"
        return $false
    }
    
    # Esperar a que el servidor inicie
    if (Test-ServiceAvailable -Url "http://localhost:5000/api/health" -MaxAttempts 20) {
        Write-Step "Portal OptiMon iniciado correctamente" -Type "SUCCESS"
        return $true
    }
    else {
        Write-Step "Error: Portal OptiMon no responde" -Type "ERROR"
        return $false
    }
}

function Setup-WindowsExporter {
    Write-Step "Configurando Windows Exporter automáticamente..." -Type "HEADER"
    
    try {
        Write-Step "Ejecutando configuración automática..." -Type "INFO"
        
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/local/setup" -Method POST -TimeoutSec 120
        
        if ($response.success) {
            Write-Step "Configuración automática completada" -Type "SUCCESS"
            
            # Mostrar resultados
            foreach ($step in $response.steps) {
                $stepType = if ($step.success) { "SUCCESS" } else { "ERROR" }
                Write-Step "  $($step.step): $($step.message)" -Type $stepType
            }
            
            return $response.success
        }
        else {
            Write-Step "Error en configuración automática" -Type "ERROR"
            return $false
        }
    }
    catch {
        Write-Step "Error ejecutando configuración automática: $($_.Exception.Message)" -Type "ERROR"
        return $false
    }
}

function Test-CompleteSystem {
    Write-Step "Verificando sistema completo..." -Type "HEADER"
    
    $services = @(
        @{ Url = "http://localhost:5000/api/health"; Name = "OptiMon Portal" },
        @{ Url = "http://localhost:9090/api/v1/targets"; Name = "Prometheus" },
        @{ Url = "http://localhost:3000"; Name = "Grafana" },
        @{ Url = "http://localhost:9182/metrics"; Name = "Windows Exporter" }
    )
    
    $allOk = $true
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Step "$($service.Name): ✓ Funcionando" -Type "SUCCESS"
            }
            else {
                Write-Step "$($service.Name): ✗ Error $($response.StatusCode)" -Type "ERROR"
                $allOk = $false
            }
        }
        catch {
            Write-Step "$($service.Name): ✗ No disponible" -Type "ERROR"
            $allOk = $false
        }
    }
    
    # Verificar targets de Prometheus
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets" -TimeoutSec 10
        $windowsTarget = $response.data.activeTargets | Where-Object { $_.labels.job -eq "windows_local" }
        
        if ($windowsTarget -and $windowsTarget.health -eq "up") {
            Write-Step "Target Windows Exporter: ✓ UP y recolectando métricas" -Type "SUCCESS"
        }
        else {
            Write-Step "Target Windows Exporter: ✗ No disponible o DOWN" -Type "ERROR"
            $allOk = $false
        }
    }
    catch {
        Write-Step "No se pudo verificar targets de Prometheus" -Type "ERROR"
        $allOk = $false
    }
    
    return $allOk
}

# Función principal
function Main {
    Write-Step "OPTIMON - CONFIGURACIÓN AUTOMÁTICA COMPLETA" -Type "HEADER"
    Write-Step "Iniciando configuración automática del sistema de monitoreo..." -Type "INFO"
    
    # Cambiar al directorio correcto
    $scriptPath = $PSScriptRoot
    if (-not $scriptPath) {
        $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
    }
    Set-Location $scriptPath
    
    $steps = @(
        @{ Name = "Detener Servicios Existentes"; Function = { Stop-ExistingServices; return $true } },
        @{ Name = "Servicios Docker"; Function = { Start-DockerServices } },
        @{ Name = "Portal OptiMon"; Function = { Start-OptiMonPortal } },
        @{ Name = "Windows Exporter"; Function = { Setup-WindowsExporter } },
        @{ Name = "Verificación del Sistema"; Function = { Test-CompleteSystem } }
    )
    
    foreach ($step in $steps) {
        Write-Step "`n$('='*50)" -Type "INFO"
        Write-Step "PASO: $($step.Name)" -Type "HEADER"
        Write-Step "$('='*50)" -Type "INFO"
        
        $result = & $step.Function
        
        if (-not $result) {
            Write-Step "✗ Error en paso: $($step.Name)" -Type "ERROR"
            Write-Step "Configuración automática fallida" -Type "ERROR"
            return $false
        }
        
        Write-Step "✓ Paso completado: $($step.Name)" -Type "SUCCESS"
    }
    
    # Resumen final
    Write-Step "`n$('='*60)" -Type "INFO"
    Write-Step "🎉 CONFIGURACIÓN AUTOMÁTICA COMPLETADA EXITOSAMENTE" -Type "SUCCESS"
    Write-Step "$('='*60)" -Type "INFO"
    
    Write-Step "`n📊 ACCESOS AL SISTEMA:" -Type "INFO"
    Write-Step "  • Portal OptiMon:     http://localhost:5000" -Type "INFO"
    Write-Step "  • Grafana:           http://localhost:3000 (admin/admin)" -Type "INFO"
    Write-Step "  • Prometheus:        http://localhost:9090" -Type "INFO"
    Write-Step "  • Windows Exporter:  http://localhost:9182/metrics" -Type "INFO"
    
    Write-Step "`n✅ Sistema de monitoreo completamente operativo" -Type "SUCCESS"
    
    # Abrir el portal automáticamente
    Write-Step "Abriendo portal OptiMon..." -Type "INFO"
    Start-Process "http://localhost:5000"
    
    return $true
}

# Ejecutar configuración
try {
    $success = Main
    if ($success) {
        exit 0
    }
    else {
        exit 1
    }
}
catch {
    Write-Step "Error inesperado: $($_.Exception.Message)" -Type "ERROR"
    exit 1
}