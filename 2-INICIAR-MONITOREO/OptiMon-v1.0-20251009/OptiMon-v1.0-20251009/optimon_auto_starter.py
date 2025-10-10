#!/usr/bin/env python3
"""
OPTIMON AUTO STARTER - Iniciador Automático Inteligente
Gestiona el inicio automático de todos los componentes de OptiMon
"""

import os
import sys
import time
import json
import socket
import requests
import subprocess
import threading
from pathlib import Path

class OptimomAutoStarter:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.services = {
            'docker': {'status': False, 'process': None},
            'smtp': {'status': False, 'process': None},
            'dashboard': {'status': False, 'process': None}
        }
        self.ports = {
            'prometheus': 9090,
            'grafana': 3000,
            'alertmanager': 9093,
            'smtp': 5555,
            'dashboard': 8080
        }
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_port(self, host, port, timeout=3):
        """Verificar si un puerto está disponible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
            
    def wait_for_service(self, service_name, host, port, max_wait=90):
        """Esperar a que un servicio esté disponible"""
        self.log(f"Esperando que {service_name} esté disponible en puerto {port}...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.check_port(host, port):
                self.log(f"✅ {service_name} disponible")
                return True
            time.sleep(3)
            
        self.log(f"❌ Timeout esperando {service_name}")
        return False
        
    def start_docker_services(self):
        """Iniciar servicios Docker"""
        self.log("🐳 Iniciando servicios Docker...")
        
        try:
            # Cambiar al directorio correcto
            os.chdir(self.script_dir)
            
            # Verificar que docker-compose existe
            if not Path('docker-compose.yml').exists():
                self.log("❌ No se encontró docker-compose.yml", "ERROR")
                return False
                
            # Iniciar servicios
            result = subprocess.run(['docker-compose', 'up', '-d'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log("✅ Servicios Docker iniciados")
                self.services['docker']['status'] = True
                
                # Esperar a que los servicios estén listos
                services_to_wait = [
                    ('Prometheus', 'localhost', self.ports['prometheus']),
                    ('Grafana', 'localhost', self.ports['grafana']),
                    ('AlertManager', 'localhost', self.ports['alertmanager'])
                ]
                
                for service_name, host, port in services_to_wait:
                    if not self.wait_for_service(service_name, host, port):
                        self.log(f"⚠️ {service_name} no respondió a tiempo", "WARNING")
                        
                return True
            else:
                self.log(f"❌ Error iniciando Docker: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Timeout iniciando servicios Docker", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Error iniciando Docker: {str(e)}", "ERROR")
            return False
            
    def start_smtp_service(self):
        """Iniciar servicio SMTP"""
        self.log("📧 Iniciando servicio SMTP...")
        
        try:
            # Verificar que el archivo existe
            smtp_script = self.script_dir / 'optimon_smtp_service.py'
            if not smtp_script.exists():
                self.log("❌ No se encontró optimon_smtp_service.py", "ERROR")
                return False
                
            # Iniciar servicio en segundo plano
            process = subprocess.Popen([sys.executable, str(smtp_script)],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     cwd=self.script_dir)
            
            self.services['smtp']['process'] = process
            
            # Esperar a que esté disponible
            if self.wait_for_service('SMTP Service', 'localhost', self.ports['smtp'], 45):
                self.services['smtp']['status'] = True
                return True
            else:
                if process.poll() is None:
                    process.terminate()
                return False
                
        except Exception as e:
            self.log(f"❌ Error iniciando SMTP: {str(e)}", "ERROR")
            return False
            
    def start_dashboard_service(self):
        """Iniciar dashboard web"""
        self.log("🌐 Iniciando dashboard web...")
        
        try:
            # Verificar que el archivo existe
            dashboard_script = self.script_dir / 'optimon_dashboard.py'
            if not dashboard_script.exists():
                self.log("❌ No se encontró optimon_dashboard.py", "ERROR")
                return False
                
            # Iniciar dashboard en segundo plano
            process = subprocess.Popen([sys.executable, str(dashboard_script)],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     cwd=self.script_dir)
            
            self.services['dashboard']['process'] = process
            
            # Esperar a que esté disponible
            if self.wait_for_service('Dashboard', 'localhost', self.ports['dashboard'], 45):
                self.services['dashboard']['status'] = True
                return True
            else:
                if process.poll() is None:
                    process.terminate()
                return False
                
        except Exception as e:
            self.log(f"❌ Error iniciando Dashboard: {str(e)}", "ERROR")
            return False
            
    def verify_all_services(self):
        """Verificar que todos los servicios estén funcionando"""
        self.log("🔍 Verificando todos los servicios...")
        
        all_ok = True
        for service_name, port in self.ports.items():
            if self.check_port('localhost', port):
                self.log(f"✅ {service_name.title()} (puerto {port})")
            else:
                self.log(f"❌ {service_name.title()} no disponible (puerto {port})")
                all_ok = False
                
        return all_ok
        
    def test_functionality(self):
        """Probar funcionalidades básicas"""
        self.log("🧪 Probando funcionalidades...")
        
        tests_passed = 0
        total_tests = 0
        
        # Test Dashboard API
        total_tests += 1
        try:
            response = requests.get('http://localhost:8080/api/system-status', timeout=5)
            if response.status_code == 200:
                self.log("✅ API Dashboard funcional")
                tests_passed += 1
            else:
                self.log(f"❌ API Dashboard error: {response.status_code}")
        except:
            self.log("❌ API Dashboard no accesible")
            
        # Test SMTP Health
        total_tests += 1
        try:
            response = requests.get('http://localhost:5555/health', timeout=5)
            if response.status_code == 200:
                self.log("✅ SMTP Service funcional")
                tests_passed += 1
            else:
                self.log(f"❌ SMTP Service error: {response.status_code}")
        except:
            self.log("❌ SMTP Service no accesible")
            
        # Test Prometheus
        total_tests += 1
        try:
            response = requests.get('http://localhost:9090/-/healthy', timeout=5)
            if response.status_code == 200:
                self.log("✅ Prometheus funcional")
                tests_passed += 1
            else:
                self.log(f"❌ Prometheus error: {response.status_code}")
        except:
            self.log("❌ Prometheus no accesible")
            
        success_rate = (tests_passed / total_tests) * 100
        self.log(f"📊 Pruebas: {tests_passed}/{total_tests} ({success_rate:.1f}% éxito)")
        
        return success_rate >= 80
        
    def create_status_file(self):
        """Crear archivo de estado"""
        status = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'services': {
                name: {
                    'status': info['status'],
                    'running': info['process'] is not None and info['process'].poll() is None if info['process'] else False
                }
                for name, info in self.services.items()
            },
            'ports': {
                name: self.check_port('localhost', port)
                for name, port in self.ports.items()
            }
        }
        
        with open(self.script_dir / 'optimon_status.json', 'w') as f:
            json.dump(status, f, indent=2)
            
    def start_all(self):
        """Iniciar todos los servicios"""
        self.log("🚀 INICIANDO OPTIMON AUTOMATICAMENTE")
        self.log("=" * 50)
        
        success = True
        
        # 1. Iniciar Docker
        if not self.start_docker_services():
            success = False
            
        # 2. Iniciar SMTP
        if not self.start_smtp_service():
            success = False
            
        # 3. Iniciar Dashboard
        if not self.start_dashboard_service():
            success = False
            
        # 4. Verificar servicios
        time.sleep(5)  # Dar tiempo para que todo se estabilice
        
        if not self.verify_all_services():
            success = False
            
        # 5. Probar funcionalidades
        if not self.test_functionality():
            success = False
            
        # 6. Crear archivo de estado
        self.create_status_file()
        
        # 7. Resultado final
        self.log("=" * 50)
        if success:
            self.log("🎉 OPTIMON INICIADO EXITOSAMENTE")
            self.log("")
            self.log("🌐 Panel de control: http://localhost:8080")
            self.log("📊 Grafana: http://localhost:3000")
            self.log("🔍 Prometheus: http://localhost:9090")
            self.log("")
            self.log("💡 Para detener: python optimon_auto_starter.py --stop")
        else:
            self.log("❌ ALGUNOS SERVICIOS FALLARON AL INICIAR")
            self.log("🔧 Revisar logs para más detalles")
            
        return success
        
    def stop_all(self):
        """Detener todos los servicios"""
        self.log("🛑 DETENIENDO OPTIMON...")
        
        # Detener procesos Python
        for name, info in self.services.items():
            if info['process'] and info['process'].poll() is None:
                self.log(f"Deteniendo {name}...")
                info['process'].terminate()
                try:
                    info['process'].wait(timeout=10)
                except subprocess.TimeoutExpired:
                    info['process'].kill()
                    
        # Detener Docker
        try:
            os.chdir(self.script_dir)
            subprocess.run(['docker-compose', 'down'], timeout=60)
            self.log("✅ Servicios Docker detenidos")
        except:
            self.log("❌ Error deteniendo Docker")
            
        self.log("🛑 OptiMon detenido")

def main():
    starter = OptimomAutoStarter()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stop':
        starter.stop_all()
    else:
        success = starter.start_all()
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())