#!/usr/bin/env python3
"""
OptiMon - Instalador Automático via BAT
Copia y ejecuta el script .bat en la máquina Windows remota
"""

import sys
import os
import subprocess
import requests
import time
import shutil
from pathlib import Path

def install_via_bat(ip, name=None):
    """Instala Node Exporter usando script .bat"""
    if not name:
        name = f"windows-{ip.replace('.', '-')}"
    
    print(f"🚀 OptiMon - Instalación via Script BAT")
    print(f"📍 Target: {name} ({ip})")
    print("=" * 50)
    
    # Verificar que el archivo .bat existe
    bat_file = "install_node_exporter.bat"
    if not Path(bat_file).exists():
        print(f"❌ Error: No se encuentra el archivo {bat_file}")
        return False
    
    # Verificar conectividad
    print(f"🔍 Verificando conectividad...")
    if not check_connectivity(ip):
        print(f"❌ No se puede conectar a {ip}")
        return False
    
    # Verificar si ya está instalado
    print(f"🔍 Verificando Node Exporter...")
    if check_node_exporter_running(ip):
        print(f"✅ Node Exporter ya está funcionando")
        add_to_prometheus(ip, name)
        return True
    
    # Intentar métodos de instalación remota
    methods = [
        try_network_copy,
        try_powershell_copy,
        show_manual_instructions
    ]
    
    for method in methods:
        print(f"🔄 Probando: {method.__name__}")
        if method(ip, name, bat_file):
            # Esperar y verificar instalación
            if wait_for_installation(ip):
                add_to_prometheus(ip, name)
                restart_prometheus()
                return True
    
    return False

def check_connectivity(ip):
    """Verifica conectividad básica"""
    try:
        result = subprocess.run(['ping', '-n', '1', ip], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ping exitoso")
            return True
        return False
    except:
        return False

def check_node_exporter_running(ip):
    """Verifica si Node Exporter está funcionando"""
    try:
        response = requests.get(f"http://{ip}:9100/metrics", timeout=5)
        return response.status_code == 200
    except:
        return False

def try_network_copy(ip, name, bat_file):
    """Intenta copiar via red compartida"""
    try:
        print(f"   📋 Intentando copia via red compartida...")
        
        # Crear directorio compartido temporal
        share_path = f"\\\\{ip}\\C$\\Temp"
        
        # Intentar copiar el archivo
        dest_path = os.path.join(share_path, "install_node_exporter.bat")
        shutil.copy2(bat_file, dest_path)
        
        print(f"   ✅ Archivo copiado a {dest_path}")
        
        # Ejecutar remotamente via PsExec o WMI
        cmd = f'wmic /node:"{ip}" process call create "cmd /c C:\\Temp\\install_node_exporter.bat"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if "ReturnValue = 0" in result.stdout:
            print(f"   ✅ Script ejecutado remotamente")
            return True
        
        print(f"   ❌ Error ejecutando: {result.stderr}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error copia de red: {e}")
        return False

def try_powershell_copy(ip, name, bat_file):
    """Intenta ejecutar via PowerShell remoto"""
    try:
        print(f"   📋 Intentando via PowerShell remoto...")
        
        # Leer el contenido del archivo .bat
        with open(bat_file, 'r', encoding='utf-8') as f:
            bat_content = f.read()
        
        # Convertir a PowerShell equivalente
        ps_script = convert_bat_to_powershell(bat_content)
        
        # Ejecutar via Invoke-Command
        cmd = [
            "powershell", "-Command",
            f"Invoke-Command -ComputerName {ip} -ScriptBlock {{ {ps_script} }}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"   ✅ PowerShell remoto exitoso")
            return True
        
        print(f"   ❌ Error PowerShell: {result.stderr}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error PowerShell: {e}")
        return False

def convert_bat_to_powershell(bat_content):
    """Convierte script .bat básico a PowerShell"""
    # Conversión básica - esto es simplificado
    ps_script = '''
    # Instalación Node Exporter via PowerShell
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        throw "Requiere permisos de administrador"
    }
    
    $Version = "1.6.1"
    $InstallDir = "C:\\Program Files\\node_exporter"
    $ServiceName = "NodeExporter"
    $Port = 9100
    
    # Descargar
    Invoke-WebRequest -Uri "https://github.com/prometheus/node_exporter/releases/download/v$Version/node_exporter-$Version.windows-amd64.tar.gz" -OutFile "$env:TEMP\\node_exporter.tar.gz" -UseBasicParsing
    
    # Extraer
    Push-Location $env:TEMP
    tar -xzf "node_exporter.tar.gz"
    $dir = Get-ChildItem -Directory | Where-Object {$_.Name -like "node_exporter-*"} | Select-Object -First 1
    
    # Instalar
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Copy-Item "$($dir.FullName)\\node_exporter.exe" $InstallDir -Force
    Pop-Location
    
    # Firewall
    New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port $Port -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
    
    # Servicio
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        Stop-Service -Name $ServiceName -Force
        sc.exe delete $ServiceName
    }
    sc.exe create $ServiceName binPath= "`"$InstallDir\\node_exporter.exe`" --web.listen-address=:$Port" start= auto
    Start-Service -Name $ServiceName
    
    Write-Host "Instalación completada"
    '''
    return ps_script

def show_manual_instructions(ip, name, bat_file):
    """Muestra instrucciones manuales"""
    print(f"   📋 Instrucciones manuales:")
    print(f"")
    print(f"   🪟 En la máquina Windows {ip}:")
    print(f"")
    print(f"   1️⃣  Copia el archivo: {os.path.abspath(bat_file)}")
    print(f"       A la máquina {ip} (por USB, red compartida, etc.)")
    print(f"")
    print(f"   2️⃣  Click derecho en el archivo → 'Ejecutar como administrador'")
    print(f"")
    print(f"   3️⃣  Espera a que complete la instalación")
    print(f"")
    print(f"   ✅ El script se encargará de todo automáticamente")
    print(f"")
    
    # Crear copia local para facilitar
    local_copy = f"install_for_{ip.replace('.', '_')}.bat"
    shutil.copy2(bat_file, local_copy)
    print(f"   💾 Copia creada: {local_copy}")
    print(f"      (Puedes transferir este archivo a la máquina {ip})")
    print(f"")
    
    return True  # Considerar como exitoso ya que se dieron instrucciones

def wait_for_installation(ip, timeout=300):
    """Espera a que la instalación se complete"""
    print(f"⏳ Esperando instalación en {ip}...")
    print(f"   Monitoreando cada 10 segundos...")
    print(f"   (Presiona Ctrl+C para cancelar)")
    
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_node_exporter_running(ip):
                print(f"")
                print(f"🎉 ¡Instalación detectada!")
                return True
            
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0 and elapsed > 0:
                print(f"   ⏱️  Esperando... ({elapsed//60}:{elapsed%60:02d})")
            
            time.sleep(10)
        
        print(f"⏰ Tiempo de espera agotado ({timeout//60} minutos)")
        return False
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Monitoreo cancelado")
        return False

def add_to_prometheus(ip, name):
    """Agrega a configuración de Prometheus"""
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
        
        print(f"✅ Agregado a Prometheus")
        
    except Exception as e:
        print(f"⚠️  Error configurando Prometheus: {e}")

def restart_prometheus():
    """Reinicia Prometheus"""
    try:
        subprocess.run([
            "docker-compose", "-f", "2-INICIAR-MONITOREO/docker-compose.yml", 
            "restart", "prometheus"
        ], cwd=".", check=True)
        print(f"✅ Prometheus reiniciado")
    except Exception as e:
        print(f"⚠️  Error reiniciando: {e}")

def main():
    if len(sys.argv) < 2:
        print("🚀 OptiMon - Instalador BAT Automático")
        print("")
        print("Uso:")
        print(f"   python {sys.argv[0]} <IP> [nombre]")
        print("")
        print("Ejemplo:")
        print(f"   python {sys.argv[0]} 172.20.10.11")
        print(f"   python {sys.argv[0]} 172.20.10.11 vm-windows")
        return
    
    ip = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = install_via_bat(ip, name)
    
    if success:
        print(f"")
        print(f"🎉 ¡Proceso completado!")
        print(f"📊 Métricas: http://{ip}:9100/metrics")
        print(f"🔗 Grafana: http://localhost:3000")
    else:
        print(f"")
        print(f"💡 Sigue las instrucciones mostradas para completar manualmente")

if __name__ == "__main__":
    main()