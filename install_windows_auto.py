#!/usr/bin/env python3
"""
OptiMon - Instalador Automático de Node Exporter para Windows
Instala automáticamente Node Exporter en Windows via WinRM
"""

import sys
import os
import subprocess
import requests
import time
import socket

class WindowsNodeExporterInstaller:
    def __init__(self):
        self.node_exporter_version = "1.6.1"
        self.target_port = 9100
    
    def install_on_windows(self, ip, name=None, username=None, password=None):
        """Instala Node Exporter automáticamente en Windows"""
        if not name:
            name = f"windows-{ip.replace('.', '-')}"
        
        print(f"🚀 Instalación automática en Windows")
        print(f"📋 Target: {name} ({ip})")
        print("=" * 50)
        
        # Paso 1: Verificar conectividad
        if not self._check_connectivity(ip):
            print(f"❌ Error: No se puede conectar a {ip}")
            return False
        
        # Paso 2: Verificar si ya está instalado
        if self._check_node_exporter_running(ip):
            print(f"✅ Node Exporter ya está ejecutándose en {ip}:9100")
            self._add_to_monitoring(ip, name)
            return True
        
        # Paso 3: Intentar instalación automática vía PowerShell remoto
        methods = [
            self._try_winrm_installation,
            self._try_psexec_installation,
            self._try_wmi_installation,
            self._try_guided_manual_installation
        ]
        
        for method in methods:
            print(f"🔄 Probando método: {method.__name__}")
            if method(ip, name, username, password):
                self._add_to_monitoring(ip, name)
                return True
        
        print(f"❌ No se pudo instalar automáticamente")
        return False
    
    def _check_connectivity(self, ip):
        """Verifica conectividad a Windows"""
        try:
            # Verificar puertos comunes de Windows
            windows_ports = [135, 445, 5985, 5986, 3389]  # RPC, SMB, WinRM HTTP/HTTPS, RDP
            
            for port in windows_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    print(f"✅ Puerto Windows {port} accesible")
                    return True
            
            # Si no hay puertos específicos, intentar ping
            result = subprocess.run(['ping', '-n', '1', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Host responde a ping")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error verificando conectividad: {e}")
            return False
    
    def _check_node_exporter_running(self, ip):
        """Verifica si Node Exporter ya está ejecutándose"""
        try:
            response = requests.get(f"http://{ip}:{self.target_port}/metrics", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _try_winrm_installation(self, ip, name, username=None, password=None):
        """Instalación via WinRM (Windows Remote Management)"""
        try:
            print("   📦 Intentando instalación via WinRM...")
            
            # Script PowerShell para instalación
            ps_script = f'''
# Instalación automática de Node Exporter
$ErrorActionPreference = "Stop"

Write-Host "Iniciando instalación de Node Exporter..."

# Variables
$Version = "{self.node_exporter_version}"
$InstallPath = "C:\\Program Files\\node_exporter"
$ServiceName = "NodeExporter"
$DownloadUrl = "https://github.com/prometheus/node_exporter/releases/download/v$Version/node_exporter-$Version.windows-amd64.tar.gz"

# Crear directorio de instalación
if (!(Test-Path $InstallPath)) {{
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "Directorio creado: $InstallPath"
}}

# Descargar Node Exporter
$TempPath = "$env:TEMP\\node_exporter.tar.gz"
Write-Host "Descargando Node Exporter desde $DownloadUrl..."

try {{
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempPath -UseBasicParsing
    Write-Host "Descarga completada"
}} catch {{
    Write-Host "Error descargando: $_"
    exit 1
}}

# Extraer usando tar (Windows 10+)
Push-Location $env:TEMP
tar -xzf "node_exporter.tar.gz"

# Buscar el ejecutable
$ExtractedDir = Get-ChildItem -Directory | Where-Object {{ $_.Name -like "node_exporter-*" }} | Select-Object -First 1
if (!$ExtractedDir) {{
    Write-Host "Error: No se encontró el directorio extraído"
    exit 1
}}

# Copiar ejecutable
Copy-Item "$($ExtractedDir.FullName)\\node_exporter.exe" $InstallPath -Force
Pop-Location

# Configurar firewall
try {{
    New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port {self.target_port} -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
    Write-Host "Firewall configurado para puerto {self.target_port}"
}} catch {{
    Write-Host "Advertencia: No se pudo configurar firewall"
}}

# Detener servicio existente si existe
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {{
    Stop-Service -Name $ServiceName -Force
    sc.exe delete $ServiceName | Out-Null
    Write-Host "Servicio anterior eliminado"
}}

# Crear servicio
$ExePath = "$InstallPath\\node_exporter.exe"
$ServiceArgs = "--web.listen-address=:{self.target_port}"
sc.exe create $ServiceName binPath= "`"$ExePath`" $ServiceArgs" start= auto | Out-Null

if ($LASTEXITCODE -eq 0) {{
    sc.exe description $ServiceName "Prometheus Node Exporter" | Out-Null
    Start-Service -Name $ServiceName
    Write-Host "Servicio creado e iniciado exitosamente"
    
    # Verificar que está funcionando
    Start-Sleep -Seconds 3
    $Service = Get-Service -Name $ServiceName
    if ($Service.Status -eq "Running") {{
        Write-Host "✅ Node Exporter instalado y ejecutándose correctamente"
        exit 0
    }} else {{
        Write-Host "❌ Error: Servicio no está ejecutándose"
        exit 1
    }}
}} else {{
    Write-Host "❌ Error creando servicio"
    exit 1
}}
'''
            
            # Intentar ejecutar vía WinRM
            winrm_methods = [
                self._winrm_via_powershell,
                self._winrm_via_invoke_command
            ]
            
            for method in winrm_methods:
                if method(ip, ps_script, username, password):
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Error WinRM: {e}")
            return False
    
    def _winrm_via_powershell(self, ip, script, username=None, password=None):
        """Ejecutar via PowerShell Invoke-Command"""
        try:
            # Crear archivo temporal con el script
            script_file = "temp_install_script.ps1"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Comando PowerShell para ejecutar remotamente
            if username and password:
                cmd = [
                    "powershell", "-Command",
                    f"$cred = New-Object System.Management.Automation.PSCredential('{username}', (ConvertTo-SecureString '{password}' -AsPlainText -Force)); "
                    f"Invoke-Command -ComputerName {ip} -Credential $cred -FilePath {script_file}"
                ]
            else:
                cmd = [
                    "powershell", "-Command",
                    f"Invoke-Command -ComputerName {ip} -FilePath {script_file}"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Limpiar archivo temporal
            try:
                os.remove(script_file)
            except:
                pass
            
            if result.returncode == 0:
                print("   ✅ Instalación PowerShell exitosa")
                return True
            else:
                print(f"   ❌ Error PowerShell: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error PowerShell remoto: {e}")
            return False
    
    def _winrm_via_invoke_command(self, ip, script, username=None, password=None):
        """Ejecutar via WinRM directo"""
        try:
            # Intentar con winrs (Windows Remote Shell)
            cmd = ["winrs", "-r", f"http://{ip}:5985", "powershell", "-Command", script]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("   ✅ Instalación WinRS exitosa")
                return True
            else:
                print(f"   ❌ Error WinRS: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error WinRS: {e}")
            return False
    
    def _try_psexec_installation(self, ip, name, username=None, password=None):
        """Instalación via PsExec (si está disponible)"""
        try:
            print("   📦 Intentando instalación via PsExec...")
            
            # Verificar si PsExec está disponible
            try:
                subprocess.run(["psexec"], capture_output=True, timeout=5)
            except FileNotFoundError:
                print("   ⚠️  PsExec no disponible")
                return False
            
            # Crear script local
            script_content = self._get_installation_script()
            script_file = f"install_node_exporter_{name}.ps1"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Ejecutar via PsExec
            cmd = ["psexec", f"\\\\{ip}", "-c", "-f", "powershell", "-ExecutionPolicy", "Bypass", "-File", script_file]
            
            if username and password:
                cmd.extend(["-u", username, "-p", password])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Limpiar
            try:
                os.remove(script_file)
            except:
                pass
            
            if result.returncode == 0:
                print("   ✅ Instalación PsExec exitosa")
                return True
            else:
                print(f"   ❌ Error PsExec: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error PsExec: {e}")
            return False
    
    def _try_wmi_installation(self, ip, name, username=None, password=None):
        """Instalación via WMI"""
        try:
            print("   📦 Intentando instalación via WMI...")
            
            # Crear script de instalación
            script_content = self._get_installation_script()
            script_b64 = self._encode_script_base64(script_content)
            
            # Comando WMI para ejecutar PowerShell
            wmi_cmd = f'wmic /node:"{ip}" process call create "powershell -EncodedCommand {script_b64}"'
            
            if username and password:
                wmi_cmd = f'wmic /node:"{ip}" /user:"{username}" /password:"{password}" process call create "powershell -EncodedCommand {script_b64}"'
            
            result = subprocess.run(wmi_cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if "ReturnValue = 0" in result.stdout:
                print("   ✅ Comando WMI ejecutado")
                # Esperar y verificar instalación
                time.sleep(30)
                if self._check_node_exporter_running(ip):
                    print("   ✅ Instalación WMI exitosa")
                    return True
            
            print(f"   ❌ Error WMI: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"   ❌ Error WMI: {e}")
            return False
    
    def _try_guided_manual_installation(self, ip, name, username=None, password=None):
        """Instalación manual guiada"""
        print("   📦 Instalación manual guiada...")
        print(f"")
        print(f"   💡 Para completar la instalación en {ip}:")
        print(f"   ")
        print(f"   1. Conecta a la máquina Windows {ip}")
        print(f"   2. Abre PowerShell como Administrador")
        print(f"   3. Ejecuta este comando:")
        print(f"   ")
        print(f"   Invoke-WebRequest -Uri 'https://github.com/prometheus/node_exporter/releases/download/v{self.node_exporter_version}/node_exporter-{self.node_exporter_version}.windows-amd64.tar.gz' -OutFile 'node_exporter.tar.gz'; tar -xzf 'node_exporter.tar.gz'; $dir = Get-ChildItem -Directory | Where {{ $_.Name -like 'node_exporter-*' }}; Copy-Item \"$($dir.FullName)\\node_exporter.exe\" 'C:\\Program Files\\node_exporter\\' -Force; sc.exe create NodeExporter binPath= '\"C:\\Program Files\\node_exporter\\node_exporter.exe\" --web.listen-address=:{self.target_port}' start= auto; Start-Service NodeExporter")
        print(f"   ")
        print(f"   4. O usa el script automatizado en: scripts/physical/install_node_exporter.ps1")
        print(f"   ")
        
        # Esperar a que esté disponible
        print(f"   ⏳ Esperando instalación manual...")
        print(f"   (Presiona Ctrl+C para cancelar)")
        
        try:
            for i in range(60):  # 5 minutos
                if self._check_node_exporter_running(ip):
                    print(f"   ✅ ¡Node Exporter detectado!")
                    return True
                time.sleep(5)
                if i % 6 == 0:
                    print(f"   Esperando... ({i//6 + 1}/10)")
            
            print(f"   ⏰ Tiempo agotado")
            return False
            
        except KeyboardInterrupt:
            print(f"\n   ⚠️  Cancelado por usuario")
            return False
    
    def _get_installation_script(self):
        """Obtiene el script de instalación PowerShell"""
        return f'''
# Node Exporter Installation Script
$ErrorActionPreference = "Stop"
$Version = "{self.node_exporter_version}"
$InstallPath = "C:\\Program Files\\node_exporter"
$ServiceName = "NodeExporter"

# Create directory
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

# Download and extract
$url = "https://github.com/prometheus/node_exporter/releases/download/v$Version/node_exporter-$Version.windows-amd64.tar.gz"
Invoke-WebRequest -Uri $url -OutFile "$env:TEMP\\node_exporter.tar.gz" -UseBasicParsing
Push-Location $env:TEMP
tar -xzf "node_exporter.tar.gz"
$dir = Get-ChildItem -Directory | Where-Object {{ $_.Name -like "node_exporter-*" }} | Select-Object -First 1
Copy-Item "$($dir.FullName)\\node_exporter.exe" $InstallPath -Force
Pop-Location

# Configure firewall
New-NetFirewallRule -DisplayName "Node Exporter" -Direction Inbound -Port {self.target_port} -Protocol TCP -Action Allow -ErrorAction SilentlyContinue

# Create and start service
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {{
    Stop-Service -Name $ServiceName -Force
    sc.exe delete $ServiceName | Out-Null
}}
sc.exe create $ServiceName binPath= "`"$InstallPath\\node_exporter.exe`" --web.listen-address=:{self.target_port}" start= auto | Out-Null
Start-Service -Name $ServiceName
'''
    
    def _encode_script_base64(self, script):
        """Codifica script en Base64 para PowerShell"""
        import base64
        encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
        return encoded
    
    def _add_to_monitoring(self, ip, name):
        """Agrega el servidor a Prometheus"""
        try:
            import yaml
            
            prometheus_config = "2-INICIAR-MONITOREO/config/prometheus/prometheus.yml"
            
            with open(prometheus_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Buscar job de physical servers
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
            target = f"{ip}:{self.target_port}"
            if not physical_job['static_configs']:
                physical_job['static_configs'] = [{'targets': [], 'labels': {'provider': 'physical'}}]
            
            if target not in physical_job['static_configs'][0]['targets']:
                physical_job['static_configs'][0]['targets'].append(target)
                physical_job['static_configs'][0]['labels'].update({
                    'provider': 'physical',
                    'instance': name,
                    'os': 'windows'
                })
            
            with open(prometheus_config, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ Agregado a configuración de Prometheus")
            
            # Reiniciar Prometheus
            subprocess.run([
                "docker-compose", "-f", "2-INICIAR-MONITOREO/docker-compose.yml", 
                "restart", "prometheus"
            ], cwd=".")
            
            print(f"✅ Prometheus reiniciado")
            
        except Exception as e:
            print(f"⚠️  Error configurando monitoreo: {e}")

def main():
    if len(sys.argv) < 2:
        print("🚀 OptiMon - Instalador Automático Node Exporter Windows")
        print("")
        print("Uso:")
        print(f"   python {sys.argv[0]} <IP> [nombre] [usuario] [contraseña]")
        print("")
        print("Ejemplos:")
        print(f"   python {sys.argv[0]} 172.20.10.11")
        print(f"   python {sys.argv[0]} 172.20.10.11 vm-windows")
        print(f"   python {sys.argv[0]} 172.20.10.11 vm-windows admin password123")
        return
    
    ip = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    username = sys.argv[3] if len(sys.argv) > 3 else None
    password = sys.argv[4] if len(sys.argv) > 4 else None
    
    installer = WindowsNodeExporterInstaller()
    success = installer.install_on_windows(ip, name, username, password)
    
    if success:
        print(f"")
        print(f"🎉 ¡Instalación completada!")
        print(f"📊 Métricas: http://{ip}:9100/metrics")
        print(f"🔗 Grafana: http://localhost:3000")
    else:
        print(f"")
        print(f"❌ Instalación no completada automáticamente")
        print(f"💡 Sigue las instrucciones manuales mostradas arriba")

if __name__ == "__main__":
    main()