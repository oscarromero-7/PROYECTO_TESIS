#!/usr/bin/env python3
"""
🚀 OPTIMON - GESTOR DE SERVICIOS EN SEGUNDO PLANO
================================================

Este script gestiona todos los servicios OptiMon en segundo plano:
- SMTP Service (puerto 5555)
- Dashboard Web (puerto 5000)
- Windows Exporter (puerto 9182)
- Servicios Docker (Prometheus, Grafana, AlertManager)

Funcionalidades:
- Inicio automático de todos los servicios
- Verificación de estado
- Reinicio automático si fallan
- Logs centralizados
- Ejecución como servicio de Windows

Autor: OptiMon Team
Versión: 2.0
Fecha: Octubre 2025
"""

import subprocess
import time
import json
import sys
import os
import signal
import threading
import requests
import psutil
from pathlib import Path
from datetime import datetime
import logging

class OptiMonServiceManager:
    def __init__(self):
        self.services = {}
        self.running = True
        self.base_dir = Path(__file__).parent
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'optimon_manager.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Definir servicios a gestionar
        self.service_configs = {
            'smtp_service': {
                'name': 'SMTP Service',
                'command': [sys.executable, 'optimon_smtp_service.py'],
                'port': 5555,
                'health_url': 'http://localhost:5555/health',
                'restart_delay': 5,
                'max_restarts': 3
            },
            'dashboard': {
                'name': 'OptiMon Dashboard',
                'command': [sys.executable, 'optimon_dashboard.py', '--no-debug'],
                'port': 5000,
                'health_url': 'http://localhost:5000/',
                'restart_delay': 5,
                'max_restarts': 3
            }
        }
    
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
        
        # Log sin emojis para evitar problemas de codificación
        clean_message = message.replace("🔴", "DETENIDO").replace("🟢", "EJECUTANDOSE").replace("📊", "").replace("🚀", "")
        if level == "ERROR":
            self.logger.error(clean_message)
        elif level == "WARNING":
            self.logger.warning(clean_message)
        else:
            self.logger.info(clean_message)
    
    def is_port_in_use(self, port):
        """Verificar si un puerto está en uso"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return True
            return False
        except:
            return False
    
    def check_service_health(self, service_name):
        """Verificar salud de un servicio"""
        config = self.service_configs.get(service_name)
        if not config:
            return False
        
        try:
            # Verificar puerto
            if not self.is_port_in_use(config['port']):
                return False
            
            # Verificar HTTP si tiene URL de salud
            if config.get('health_url'):
                response = requests.get(config['health_url'], timeout=5)
                return response.status_code == 200
            
            return True
        except:
            return False
    
    def start_service(self, service_name):
        """Iniciar un servicio en segundo plano"""
        config = self.service_configs.get(service_name)
        if not config:
            self.log(f"Configuración no encontrada para {service_name}", "ERROR")
            return False
        
        try:
            # Verificar si ya está ejecutándose
            if self.check_service_health(service_name):
                self.log(f"{config['name']} ya está ejecutándose", "SUCCESS")
                return True
            
            self.log(f"Iniciando {config['name']}...")
            
            # Crear proceso en segundo plano
            process = subprocess.Popen(
                config['command'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Guardar información del proceso
            self.services[service_name] = {
                'process': process,
                'config': config,
                'start_time': time.time(),
                'restart_count': 0
            }
            
            # Esperar un poco y verificar que se inició correctamente
            time.sleep(3)
            
            if self.check_service_health(service_name):
                self.log(f"{config['name']} iniciado exitosamente (PID: {process.pid})", "SUCCESS")
                return True
            else:
                self.log(f"Error verificando salud de {config['name']}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Error iniciando {config['name']}: {e}", "ERROR")
            return False
    
    def stop_service(self, service_name):
        """Detener un servicio"""
        if service_name not in self.services:
            return True
        
        service_info = self.services[service_name]
        config = service_info['config']
        process = service_info['process']
        
        try:
            self.log(f"Deteniendo {config['name']}...")
            
            if os.name == 'nt':
                # Windows: usar taskkill
                subprocess.run(['taskkill', '/PID', str(process.pid), '/F'], check=False)
            else:
                # Unix: usar SIGTERM
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
            
            del self.services[service_name]
            self.log(f"{config['name']} detenido", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error deteniendo {config['name']}: {e}", "ERROR")
            return False
    
    def restart_service(self, service_name):
        """Reiniciar un servicio"""
        self.log(f"Reiniciando {service_name}...")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
    
    def monitor_services(self):
        """Monitorear servicios y reiniciar si fallan"""
        while self.running:
            try:
                for service_name, service_info in list(self.services.items()):
                    config = service_info['config']
                    process = service_info['process']
                    
                    # Verificar si el proceso sigue vivo
                    if process.poll() is not None:
                        self.log(f"{config['name']} se detuvo inesperadamente", "WARNING")
                        
                        # Incrementar contador de reinicios
                        service_info['restart_count'] += 1
                        
                        if service_info['restart_count'] <= config.get('max_restarts', 3):
                            self.log(f"Reiniciando {config['name']} (intento {service_info['restart_count']})")
                            del self.services[service_name]
                            time.sleep(config.get('restart_delay', 5))
                            self.start_service(service_name)
                        else:
                            self.log(f"Máximo de reinicios alcanzado para {config['name']}", "ERROR")
                            del self.services[service_name]
                    
                    # Verificar salud del servicio
                    elif not self.check_service_health(service_name):
                        self.log(f"{config['name']} no responde correctamente", "WARNING")
                        # Opcional: reiniciar si no responde
                
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                self.log(f"Error en monitoreo: {e}", "ERROR")
                time.sleep(10)
    
    def start_docker_services(self):
        """Iniciar servicios Docker"""
        self.log("Verificando servicios Docker...")
        
        try:
            # Verificar Docker
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Docker no está disponible", "ERROR")
                return False
            
            # Iniciar docker-compose
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("Servicios Docker iniciados correctamente", "SUCCESS")
                return True
            else:
                self.log(f"Error iniciando Docker: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error con Docker: {e}", "ERROR")
            return False
    
    def show_status(self):
        """Mostrar estado de todos los servicios"""
        self.log("=" * 60)
        self.log("📊 ESTADO DE SERVICIOS OPTIMON")
        self.log("=" * 60)
        
        # Servicios Python
        for service_name, config in self.service_configs.items():
            if service_name in self.services:
                process = self.services[service_name]['process']
                uptime = time.time() - self.services[service_name]['start_time']
                status = "🟢 EJECUTÁNDOSE" if self.check_service_health(service_name) else "🟡 PROBLEMAS"
                self.log(f"{config['name']}: {status} (PID: {process.pid}, Uptime: {uptime:.0f}s)")
            else:
                self.log(f"{config['name']}: 🔴 DETENIDO")
        
        # Servicios Docker
        docker_services = [
            ("Prometheus", 9090),
            ("Grafana", 3000),
            ("AlertManager", 9093)
        ]
        
        for service_name, port in docker_services:
            status = "🟢 EJECUTÁNDOSE" if self.is_port_in_use(port) else "🔴 DETENIDO"
            self.log(f"{service_name}: {status} (Puerto: {port})")
        
        # Windows Exporter
        we_status = "🟢 EJECUTÁNDOSE" if self.is_port_in_use(9182) else "🔴 DETENIDO"
        self.log(f"Windows Exporter: {we_status} (Puerto: 9182)")
        
        self.log("=" * 60)
    
    def cleanup(self):
        """Limpiar al salir"""
        self.log("Deteniendo todos los servicios...")
        self.running = False
        
        for service_name in list(self.services.keys()):
            self.stop_service(service_name)
        
        self.log("Limpieza completada")
    
    def run(self, daemon_mode=False):
        """Ejecutar el gestor de servicios"""
        self.log("🚀 INICIANDO GESTOR DE SERVICIOS OPTIMON")
        self.log("=" * 60)
        
        # Registrar manejador de señales para limpieza
        def signal_handler(signum, frame):
            self.log("Señal recibida, deteniendo servicios...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Iniciar servicios Docker
            self.start_docker_services()
            time.sleep(10)  # Dar tiempo para que Docker se inicie
            
            # Iniciar servicios Python
            for service_name in self.service_configs.keys():
                self.start_service(service_name)
                time.sleep(2)
            
            # Mostrar estado inicial
            self.show_status()
            
            if daemon_mode:
                self.log("Ejecutando en modo daemon...")
                self.log("Para detener: Ctrl+C o kill del proceso")
                
                # Iniciar thread de monitoreo
                monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
                monitor_thread.start()
                
                # Mantener el proceso principal vivo
                try:
                    while self.running:
                        time.sleep(60)
                        self.show_status()
                except KeyboardInterrupt:
                    pass
            else:
                self.log("Servicios iniciados. Use 'Ctrl+C' para detener.")
                
                # Monitoreo básico
                try:
                    while True:
                        time.sleep(30)
                        self.show_status()
                except KeyboardInterrupt:
                    pass
        
        finally:
            self.cleanup()

def main():
    """Función principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║            🚀 OPTIMON - GESTOR DE SERVICIOS v2.0            ║
║                                                              ║
║  Gestiona todos los servicios OptiMon en segundo plano:     ║
║  • SMTP Service (puerto 5555)                               ║
║  • Dashboard Web (puerto 5000)                              ║
║  • Servicios Docker (Prometheus, Grafana, AlertManager)     ║
║  • Monitoreo y reinicio automático                          ║
║  • Logs centralizados                                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    import argparse
    parser = argparse.ArgumentParser(description="OptiMon Service Manager")
    parser.add_argument('--daemon', action='store_true', help='Ejecutar en modo daemon')
    parser.add_argument('--stop', action='store_true', help='Detener todos los servicios')
    parser.add_argument('--status', action='store_true', help='Mostrar estado de servicios')
    
    args = parser.parse_args()
    
    manager = OptiMonServiceManager()
    
    if args.stop:
        # Detener todos los procesos Python relacionados
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'optimon' in cmdline.lower():
                        print(f"Deteniendo proceso: {proc.info['pid']}")
                        proc.terminate()
            except:
                pass
        return 0
    
    elif args.status:
        manager.show_status()
        return 0
    
    else:
        try:
            manager.run(daemon_mode=args.daemon)
            return 0
        except KeyboardInterrupt:
            print("\n⏹️ Detenido por el usuario")
            return 0
        except Exception as e:
            print(f"❌ Error crítico: {e}")
            return 1

if __name__ == "__main__":
    exit(main())