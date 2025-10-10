#!/usr/bin/env python3
"""
OptiMon - Comando Rápido para Windows
Automatiza completamente la instalación en Windows
"""

import sys
import subprocess
import requests
import time
import socket

def quick_install_windows(ip, name=None):
    """Instalación rápida en Windows con instrucciones paso a paso"""
    if not name:
        name = f"windows-{ip.replace('.', '-')}"
    
    print(f"🚀 OptiMon - Instalación Rápida en Windows")
    print(f"📍 Target: {name} ({ip})")
    print("=" * 60)
    
    # Verificar conectividad
    print(f"🔍 Verificando conectividad a {ip}...")
    if not check_connectivity(ip):
        print(f"❌ No se puede conectar a {ip}")
        print(f"💡 Verifica que la máquina esté encendida y en la red")
        return False
    
    print(f"✅ Conectividad confirmada")
    
    # Verificar si ya está instalado
    print(f"🔍 Verificando si Node Exporter ya está instalado...")
    if check_node_exporter_running(ip):
        print(f"✅ Node Exporter ya está ejecutándose en {ip}:9100")
        add_to_prometheus(ip, name)
        print(f"🎉 ¡Servidor ya está siendo monitoreado!")
        return True
    
    print(f"❌ Node Exporter no detectado, proceder con instalación")
    
    # Mostrar instrucciones claras
    print(f"")
    print(f"📋 INSTRUCCIONES DE INSTALACIÓN")
    print(f"=" * 60)
    print(f"")
    print(f"🪟 En la máquina Windows {ip}:")
    print(f"")
    print(f"1️⃣  Abre PowerShell como ADMINISTRADOR")
    print(f"    (Click derecho en el botón Inicio → Windows PowerShell (Administrador))")
    print(f"")
    print(f"2️⃣  Copia y pega este comando COMPLETO:")
    print(f"")
    print(f"    irm https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.windows-amd64.tar.gz -OutFile node_exporter.tar.gz; tar -xzf node_exporter.tar.gz; $dir = gci -Directory | ? {{$_.Name -like 'node_exporter-*'}}; mkdir 'C:\\Program Files\\node_exporter' -Force; cp \"$($dir.FullName)\\node_exporter.exe\" 'C:\\Program Files\\node_exporter\\'; New-NetFirewallRule -DisplayName 'Node Exporter' -Direction Inbound -Port 9100 -Protocol TCP -Action Allow; sc.exe create NodeExporter binPath= '\"C:\\Program Files\\node_exporter\\node_exporter.exe\" --web.listen-address=:9100' start= auto; Start-Service NodeExporter; echo '✅ Instalación completada'")
    print(f"")
    print(f"3️⃣  Presiona Enter y espera a que complete")
    print(f"")
    print(f"4️⃣  Verifica que veas: '✅ Instalación completada'")
    print(f"")
    
    # Crear archivo de script para facilitar
    script_path = f"install_on_{ip.replace('.', '_')}.ps1"
    create_installation_script(script_path, ip)
    print(f"💾 Script guardado en: {script_path}")
    print(f"   (Puedes copiarlo a la máquina Windows si prefieres)")
    print(f"")
    
    # Esperar instalación
    print(f"⏳ Esperando instalación en {ip}...")
    print(f"   Monitoreando puerto 9100 cada 10 segundos...")
    print(f"   (Presiona Ctrl+C para cancelar)")
    print(f"")
    
    try:
        max_attempts = 36  # 6 minutos
        for attempt in range(max_attempts):
            if check_node_exporter_running(ip):
                print(f"")
                print(f"🎉 ¡INSTALACIÓN DETECTADA!")
                print(f"✅ Node Exporter está funcionando en {ip}:9100")
                
                # Configurar automáticamente
                add_to_prometheus(ip, name)
                restart_prometheus()
                
                print(f"")
                print(f"🎯 CONFIGURACIÓN COMPLETADA:")
                print(f"   📊 Métricas: http://{ip}:9100/metrics")
                print(f"   🔗 Grafana: http://localhost:3000")
                print(f"   📈 Dashboard: 'Physical Servers'")
                print(f"")
                return True
            
            # Mostrar progreso cada minuto
            if attempt % 6 == 0 and attempt > 0:
                print(f"   ⏱️  Esperando... ({attempt//6}/6 minutos)")
            
            time.sleep(10)
        
        print(f"")
        print(f"⏰ Tiempo de espera agotado (6 minutos)")
        print(f"💡 Verifica que el comando se ejecutó correctamente en {ip}")
        return False
        
    except KeyboardInterrupt:
        print(f"\n")
        print(f"⚠️  Monitoreo cancelado por el usuario")
        print(f"💡 Puedes ejecutar este comando nuevamente cuando la instalación esté lista")
        return False

def check_connectivity(ip):
    """Verifica conectividad básica"""
    try:
        # Ping test
        result = subprocess.run(['ping', '-n', '1', ip], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_node_exporter_running(ip):
    """Verifica si Node Exporter está funcionando"""
    try:
        response = requests.get(f"http://{ip}:9100/metrics", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_installation_script(filename, ip):
    """Crea script de instalación"""
    script_content = f'''# Instalación automática de Node Exporter
# Para Windows {ip}

# Verificar permisos de administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Host "❌ Ejecuta PowerShell como Administrador" -ForegroundColor Red
    exit 1
}}

Write-Host "🚀 Instalando Node Exporter..." -ForegroundColor Green

try {{
    # Descargar y extraer
    Invoke-RestMethod -Uri "https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.windows-amd64.tar.gz" -OutFile "node_exporter.tar.gz"
    tar -xzf "node_exporter.tar.gz"
    
    # Instalar
    $dir = Get-ChildItem -Directory | Where-Object {{$_.Name -like "node_exporter-*"}}
    New-Item -ItemType Directory -Path "C:\\Program Files\\node_exporter" -Force | Out-Null
    Copy-Item "$($dir.FullName)\\node_exporter.exe" "C:\\Program Files\\node_exporter\\" -Force
    
    # Configurar firewall
    New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port 9100 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
    
    # Crear y iniciar servicio
    sc.exe create NodeExporter binPath= '"C:\\Program Files\\node_exporter\\node_exporter.exe" --web.listen-address=:9100' start= auto
    Start-Service NodeExporter
    
    Write-Host "✅ Instalación completada exitosamente!" -ForegroundColor Green
    Write-Host "📊 Métricas en: http://localhost:9100/metrics" -ForegroundColor Cyan
    
}} catch {{
    Write-Host "❌ Error: $_" -ForegroundColor Red
}}

Read-Host "Presiona Enter para continuar"'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(script_content)

def add_to_prometheus(ip, name):
    """Agrega servidor a Prometheus"""
    try:
        import yaml
        
        config_file = "2-INICIAR-MONITOREO/config/prometheus/prometheus.yml"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Buscar job physical-servers
        physical_job = None
        for job in config['scrape_configs']:
            if job['job_name'] == 'physical-servers':
                physical_job = job
                break
        
        if not physical_job:
            physical_job = {
                'job_name': 'physical-servers',
                'static_configs': [{'targets': [], 'labels': {'provider': 'physical'}}],
                'scrape_interval': '15s'
            }
            config['scrape_configs'].append(physical_job)
        
        # Agregar target
        target = f"{ip}:9100"
        if not physical_job['static_configs']:
            physical_job['static_configs'] = [{'targets': [], 'labels': {}}]
        
        targets = physical_job['static_configs'][0].get('targets', [])
        if target not in targets:
            targets.append(target)
            physical_job['static_configs'][0]['targets'] = targets
            physical_job['static_configs'][0]['labels'] = {
                'provider': 'physical',
                'instance': name,
                'os': 'windows'
            }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Agregado a configuración de Prometheus")
        
    except Exception as e:
        print(f"⚠️  Error configurando Prometheus: {e}")

def restart_prometheus():
    """Reinicia Prometheus"""
    try:
        print(f"🔄 Reiniciando Prometheus...")
        subprocess.run([
            "docker-compose", "-f", "2-INICIAR-MONITOREO/docker-compose.yml", 
            "restart", "prometheus"
        ], cwd=".", check=True)
        print(f"✅ Prometheus reiniciado")
    except Exception as e:
        print(f"⚠️  Error reiniciando Prometheus: {e}")

def main():
    if len(sys.argv) < 2:
        print("🚀 OptiMon - Instalación Rápida Windows")
        print("")
        print("Uso:")
        print(f"   python {sys.argv[0]} <IP> [nombre]")
        print("")
        print("Ejemplo:")
        print(f"   python {sys.argv[0]} 172.20.10.11")
        print(f"   python {sys.argv[0]} 172.20.10.11 mi-servidor-windows")
        return
    
    ip = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = quick_install_windows(ip, name)
    
    if success:
        print(f"🎉 ¡Proceso completado exitosamente!")
    else:
        print(f"❌ Proceso no completado")
        print(f"💡 Ejecuta nuevamente cuando la instalación esté lista")

if __name__ == "__main__":
    main()