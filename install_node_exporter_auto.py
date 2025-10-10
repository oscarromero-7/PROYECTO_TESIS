#!/usr/bin/env python3
"""
OptiMon - Instalador Automático de Node Exporter
Instala automáticamente Node Exporter en cualquier IP
"""

import sys
import os
sys.path.append('scripts')

from auto_setup import IntelligentAutoSetup
import socket
import requests

class AutoNodeExporterInstaller:
    def __init__(self):
        self.setup = IntelligentAutoSetup()
        self.setup.load_config()
    
    def install_on_ip(self, ip, name=None):
        """Instala Node Exporter automáticamente en una IP específica"""
        if not name:
            name = f"server-{ip.replace('.', '-')}"
        
        print(f"🚀 Iniciando instalación automática de Node Exporter")
        print(f"📋 Target: {name} ({ip})")
        print("=" * 50)
        
        # Paso 1: Verificar conectividad
        if not self._check_connectivity(ip):
            print(f"❌ Error: No se puede conectar a {ip}")
            return False
        
        # Paso 2: Verificar si ya está instalado
        if self._check_node_exporter_running(ip):
            print(f"✅ Node Exporter ya está ejecutándose en {ip}:9100")
            self._add_to_prometheus_config(ip, name)
            print(f"🎉 ¡Listo! El servidor ya está siendo monitoreado.")
            return True
        
        # Paso 3: Detectar SO automáticamente
        print(f"🔍 Detectando sistema operativo...")
        os_info = self._detect_os_and_arch(ip)
        if not os_info:
            print(f"❌ No se pudo detectar el SO de {ip}")
            self._show_manual_instructions(ip, name)
            return False
        
        print(f"✅ SO detectado: {os_info['os']} {os_info['arch']}")
        
        # Paso 4: Instalar según el SO
        success = False
        if os_info['os'] == 'linux':
            success = self._install_linux_auto(ip, name, os_info)
        elif os_info['os'] == 'windows':
            success = self._install_windows_auto(ip, name, os_info)
        
        # Paso 5: Configurar Prometheus
        if success:
            self._add_to_prometheus_config(ip, name)
            self._restart_prometheus()
            print(f"🎉 ¡Instalación completada exitosamente!")
            print(f"📊 Métricas disponibles en: http://{ip}:9100/metrics")
            print(f"🔗 Verifica en Grafana: http://localhost:3000")
        
        return success
    
    def _check_connectivity(self, ip):
        """Verifica conectividad básica a la IP"""
        try:
            # Verificar si responde a ping (puerto 22 o 3389)
            common_ports = [22, 3389, 80, 443]
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    print(f"✅ Conectividad confirmada (puerto {port})")
                    return True
            
            print(f"⚠️  No se detectaron puertos comunes abiertos")
            return True  # Continuar de todos modos
            
        except Exception as e:
            print(f"❌ Error verificando conectividad: {e}")
            return False
    
    def _check_node_exporter_running(self, ip):
        """Verifica si Node Exporter ya está ejecutándose"""
        try:
            response = requests.get(f"http://{ip}:9100/metrics", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _detect_os_and_arch(self, ip):
        """Detecta SO y arquitectura automáticamente"""
        return self.setup._detect_os_and_arch(ip)
    
    def _install_linux_auto(self, ip, name, os_info):
        """Instalación automática en Linux"""
        print(f"📦 Instalando Node Exporter en Linux...")
        
        try:
            # Crear instancia temporal para usar las funciones existentes
            temp_instance = {
                'provider': 'physical',
                'name': name,
                'ip': ip,
                'ssh_user': os_info.get('ssh_user', 'admin')
            }
            
            return self.setup._install_node_exporter_linux(ip, temp_instance, os_info)
            
        except Exception as e:
            print(f"❌ Error en instalación Linux: {e}")
            return False
    
    def _install_windows_auto(self, ip, name, os_info):
        """Instalación automática en Windows"""
        print(f"📦 Preparando instalación en Windows...")
        print(f"💡 Para completar la instalación en Windows ({ip}):")
        print(f"   1. Copia y ejecuta este comando en PowerShell como Administrador:")
        print(f"   ")
        print(f"   Invoke-WebRequest -Uri 'https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.windows-amd64.tar.gz' -OutFile 'node_exporter.tar.gz'")
        print(f"   ")
        print(f"   2. O usa nuestro script automatizado:")
        print(f"      - Descarga: scripts/physical/install_node_exporter.ps1")
        print(f"      - Ejecuta en PowerShell como Admin")
        print(f"   ")
        print(f"   3. El sistema detectará automáticamente cuando esté disponible")
        
        # Esperar a que el usuario instale manualmente
        print(f"⏳ Esperando a que Node Exporter esté disponible...")
        print(f"   (Presiona Ctrl+C para cancelar)")
        
        try:
            import time
            for i in range(60):  # Esperar hasta 5 minutos
                if self._check_node_exporter_running(ip):
                    print(f"✅ ¡Node Exporter detectado en {ip}!")
                    return True
                time.sleep(5)
                if i % 6 == 0:  # Cada 30 segundos
                    print(f"   Esperando... ({i//6 + 1}/10)")
            
            print(f"⏰ Tiempo de espera agotado. Instala manualmente y vuelve a ejecutar.")
            return False
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Instalación cancelada por el usuario")
            return False
    
    def _add_to_prometheus_config(self, ip, name):
        """Agrega el servidor a la configuración de Prometheus"""
        try:
            import yaml
            
            prometheus_config_path = "2-INICIAR-MONITOREO/config/prometheus/prometheus.yml"
            
            # Leer configuración actual
            with open(prometheus_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Buscar job de physical servers o crearlo
            physical_job = None
            for job in config['scrape_configs']:
                if job['job_name'] == 'physical-servers':
                    physical_job = job
                    break
            
            if not physical_job:
                # Crear nuevo job para servidores físicos
                physical_job = {
                    'job_name': 'physical-servers',
                    'static_configs': [],
                    'scrape_interval': '15s',
                    'metrics_path': '/metrics'
                }
                config['scrape_configs'].append(physical_job)
            
            # Agregar target si no existe
            target = f"{ip}:9100"
            target_exists = False
            
            for static_config in physical_job['static_configs']:
                if target in static_config.get('targets', []):
                    target_exists = True
                    break
            
            if not target_exists:
                if not physical_job['static_configs']:
                    physical_job['static_configs'].append({
                        'targets': [],
                        'labels': {}
                    })
                
                physical_job['static_configs'][0]['targets'].append(target)
                physical_job['static_configs'][0]['labels'].update({
                    'provider': 'physical',
                    'instance': name
                })
                
                # Guardar configuración
                with open(prometheus_config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"✅ Servidor agregado a configuración de Prometheus")
            else:
                print(f"ℹ️  Servidor ya está en configuración de Prometheus")
            
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo actualizar configuración de Prometheus: {e}")
    
    def _restart_prometheus(self):
        """Reinicia Prometheus para aplicar nueva configuración"""
        try:
            import subprocess
            print(f"🔄 Reiniciando Prometheus...")
            
            # Usar docker-compose para reiniciar
            result = subprocess.run([
                "docker-compose", "-f", "2-INICIAR-MONITOREO/docker-compose.yml", 
                "restart", "prometheus"
            ], capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print(f"✅ Prometheus reiniciado exitosamente")
            else:
                print(f"⚠️  Advertencia: Error reiniciando Prometheus: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo reiniciar Prometheus: {e}")
    
    def _show_manual_instructions(self, ip, name):
        """Muestra instrucciones para instalación manual"""
        print(f"📋 Instrucciones de instalación manual para {ip}:")
        print(f"")
        print(f"🐧 Para Linux:")
        print(f"   curl -sSL https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz | tar xz")
        print(f"   sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/")
        print(f"   sudo useradd --no-create-home --shell /bin/false node_exporter")
        print(f"   sudo systemctl enable --now node_exporter")
        print(f"")
        print(f"🪟 Para Windows:")
        print(f"   Usa el script: scripts/physical/install_node_exporter.ps1")
        print(f"")
        print(f"🔄 Después de instalar, ejecuta nuevamente este comando")

def main():
    if len(sys.argv) < 2:
        print("🚀 OptiMon - Instalador Automático de Node Exporter")
        print("")
        print("Uso:")
        print(f"   python {sys.argv[0]} <IP> [nombre]")
        print("")
        print("Ejemplos:")
        print(f"   python {sys.argv[0]} 192.168.1.100")
        print(f"   python {sys.argv[0]} 192.168.1.100 servidor-web")
        print(f"   python {sys.argv[0]} 10.0.0.50 servidor-bd")
        return
    
    ip = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    installer = AutoNodeExporterInstaller()
    success = installer.install_on_ip(ip, name)
    
    if success:
        print(f"")
        print(f"🎉 ¡Instalación completada!")
        print(f"📊 Próximos pasos:")
        print(f"   1. Ve a Grafana: http://localhost:3000")
        print(f"   2. Busca el dashboard 'Physical Servers'")
        print(f"   3. Verifica que {name or ip} aparezca en las métricas")
    else:
        print(f"")
        print(f"❌ Instalación no completada")
        print(f"💡 Revisa las instrucciones manuales arriba")

if __name__ == "__main__":
    main()