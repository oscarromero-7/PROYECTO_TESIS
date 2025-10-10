#!/usr/bin/env python3
"""
OPTIMON - SUITE COMPLETA DE PRUEBAS
Verificación integral de todos los componentes antes del empaquetado
"""

import os
import sys
import json
import time
import socket
import requests
import subprocess
import psutil
from pathlib import Path
import threading
import tempfile

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestSuite:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log(self, message, color=Colors.WHITE):
        print(f"{color}{message}{Colors.END}")
        
    def test_result(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        color = Colors.GREEN if success else Colors.RED
        self.log(f"{status} {test_name}", color)
        
        if details:
            self.log(f"     {details}", Colors.CYAN)
            
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
            
    def check_port(self, host, port, timeout=3):
        """Verificar si un puerto está abierto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
            
    def test_system_requirements(self):
        """1. Verificar requisitos del sistema"""
        self.log(f"\n{Colors.BOLD}🔧 PRUEBA 1: REQUISITOS DEL SISTEMA{Colors.END}")
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        success = sys.version_info >= (3, 8)
        self.test_result("Python >= 3.8", success, f"Versión actual: {python_version}")
        
        # Required modules
        required_modules = ['flask', 'requests', 'psutil', 'pathlib']
        for module in required_modules:
            try:
                __import__(module)
                self.test_result(f"Módulo {module}", True, "Disponible")
            except ImportError:
                self.test_result(f"Módulo {module}", False, "No encontrado")
                
        # System resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        self.test_result("Memoria suficiente", memory.available > 500*1024*1024, 
                        f"Disponible: {memory.available//1024**2}MB")
        self.test_result("Espacio en disco", disk.free > 1024*1024*1024,
                        f"Disponible: {disk.free//1024**3}GB")
                        
    def test_file_structure(self):
        """2. Verificar estructura de archivos"""
        self.log(f"\n{Colors.BOLD}🗂️ PRUEBA 2: ESTRUCTURA DE ARCHIVOS{Colors.END}")
        
        required_files = [
            'optimon_dashboard.py',
            'optimon_smtp_service.py',
            'docker-compose.yml',
            'config/alertmanager/alertmanager.yml',
            'config/prometheus/prometheus.yml',
            'templates/base.html',
            'templates/dashboard.html',
            'templates/monitoring.html'
        ]
        
        for file_path in required_files:
            exists = os.path.exists(file_path)
            self.test_result(f"Archivo {file_path}", exists, 
                           "Encontrado" if exists else "No encontrado")
                           
    def test_docker_services(self):
        """3. Verificar servicios Docker"""
        self.log(f"\n{Colors.BOLD}🐳 PRUEBA 3: SERVICIOS DOCKER{Colors.END}")
        
        try:
            # Check if docker-compose is available
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            self.test_result("Docker Compose disponible", result.returncode == 0,
                           result.stdout.strip() if result.returncode == 0 else "No encontrado")
        except:
            self.test_result("Docker Compose disponible", False, "Comando no encontrado")
            
        # Check services
        docker_services = {
            'Prometheus': 9090,
            'Grafana': 3000,
            'AlertManager': 9093
        }
        
        for service, port in docker_services.items():
            is_running = self.check_port('localhost', port)
            self.test_result(f"{service} (puerto {port})", is_running,
                           "Ejecutándose" if is_running else "No disponible")
                           
    def test_smtp_service(self):
        """4. Verificar servicio SMTP"""
        self.log(f"\n{Colors.BOLD}📧 PRUEBA 4: SERVICIO SMTP{Colors.END}")
        
        # Check if SMTP service is running
        smtp_running = self.check_port('localhost', 5555)
        self.test_result("Servicio SMTP (puerto 5555)", smtp_running,
                        "Activo" if smtp_running else "No activo")
        
        if smtp_running:
            try:
                response = requests.get('http://localhost:5555/health', timeout=5)
                self.test_result("Health check SMTP", response.status_code == 200,
                               f"Status: {response.status_code}")
            except:
                self.test_result("Health check SMTP", False, "No responde")
                
        # Check email configuration
        email_config_exists = os.path.exists('emails_config.json')
        self.test_result("Configuración de emails", email_config_exists,
                        "Archivo encontrado" if email_config_exists else "No configurado")
                        
    def test_dashboard_service(self):
        """5. Verificar dashboard web"""
        self.log(f"\n{Colors.BOLD}🌐 PRUEBA 5: DASHBOARD WEB{Colors.END}")
        
        # Start dashboard in background for testing
        dashboard_running = self.check_port('localhost', 8080)
        
        if not dashboard_running:
            self.log("     Intentando iniciar dashboard para pruebas...", Colors.YELLOW)
            try:
                # Try to start dashboard in background
                subprocess.Popen(['python', 'optimon_dashboard.py'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                time.sleep(3)  # Wait for startup
                dashboard_running = self.check_port('localhost', 8080)
            except:
                pass
                
        self.test_result("Dashboard (puerto 8080)", dashboard_running,
                        "Ejecutándose" if dashboard_running else "No disponible")
        
        if dashboard_running:
            # Test main endpoints
            endpoints = [
                ('/', 'Página principal'),
                ('/monitoring', 'Panel de monitoreo'),
                ('/emails', 'Configuración de emails'),
                ('/api/system-status', 'API estado del sistema'),
                ('/api/monitoring/status', 'API estado monitoreo')
            ]
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f'http://localhost:8080{endpoint}', timeout=5)
                    success = response.status_code == 200
                    self.test_result(f"Endpoint {name}", success,
                                   f"HTTP {response.status_code}")
                except Exception as e:
                    self.test_result(f"Endpoint {name}", False, f"Error: {str(e)}")
                    
    def test_monitoring_features(self):
        """6. Verificar funcionalidades de monitoreo"""
        self.log(f"\n{Colors.BOLD}📊 PRUEBA 6: FUNCIONALIDADES DE MONITOREO{Colors.END}")
        
        # Test system metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            self.test_result("Lectura CPU", True, f"{cpu_percent}%")
            self.test_result("Lectura Memoria", True, f"{memory.percent}%")
            self.test_result("Lectura Disco", True, f"{disk.percent}%")
            
            # Test if metrics are reasonable
            self.test_result("Métricas válidas", 
                           0 <= cpu_percent <= 100 and 0 <= memory.percent <= 100,
                           "Valores en rango esperado")
                           
        except Exception as e:
            self.test_result("Lectura de métricas", False, f"Error: {str(e)}")
            
        # Test alerting configuration
        alert_config_exists = os.path.exists('config/alertmanager/alertmanager.yml')
        self.test_result("Configuración de alertas", alert_config_exists,
                        "Archivo encontrado" if alert_config_exists else "No encontrado")
                        
    def test_api_functionality(self):
        """7. Verificar APIs específicas"""
        self.log(f"\n{Colors.BOLD}🔗 PRUEBA 7: FUNCIONALIDAD DE APIs{Colors.END}")
        
        if not self.check_port('localhost', 8080):
            self.test_result("APIs del dashboard", False, "Dashboard no disponible")
            return
            
        # Test specific API endpoints
        api_tests = [
            ('/api/system-status', 'Estado del sistema'),
            ('/api/monitoring/config', 'Configuración monitoreo'),
            ('/api/monitoring/status', 'Estado monitoreo'),
            ('/api/monitoring/metrics/current', 'Métricas actuales'),
            ('/api/emails', 'Configuración emails')
        ]
        
        for endpoint, name in api_tests:
            try:
                response = requests.get(f'http://localhost:8080{endpoint}', timeout=5)
                success = response.status_code == 200
                
                if success:
                    # Try to parse JSON
                    try:
                        data = response.json()
                        detail = f"JSON válido con {len(data)} campos"
                    except:
                        detail = "Respuesta válida"
                else:
                    detail = f"HTTP {response.status_code}"
                    
                self.test_result(f"API {name}", success, detail)
                
            except Exception as e:
                self.test_result(f"API {name}", False, f"Error: {str(e)}")
                
    def test_installation_logic(self):
        """8. Verificar lógica de instalación"""
        self.log(f"\n{Colors.BOLD}⚙️ PRUEBA 8: LÓGICA DE INSTALACIÓN{Colors.END}")
        
        # Test Node Exporter installation logic (without actually downloading)
        try:
            # Check if the installation function exists in dashboard
            with open('optimon_dashboard.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            has_install_function = 'def install_node_exporter' in content
            self.test_result("Función instalación Node Exporter", has_install_function,
                           "Implementada" if has_install_function else "No encontrada")
            
            has_download_logic = 'urllib.request.urlretrieve' in content
            self.test_result("Lógica de descarga", has_download_logic,
                           "Implementada" if has_download_logic else "No encontrada")
                           
            has_extraction_logic = 'zipfile' in content
            self.test_result("Lógica de extracción", has_extraction_logic,
                           "Implementada" if has_extraction_logic else "No encontrada")
                           
        except Exception as e:
            self.test_result("Verificación código instalación", False, f"Error: {str(e)}")
            
        # Test directory creation
        try:
            test_dir = tempfile.mkdtemp(prefix='optimon_test_')
            os.rmdir(test_dir)
            self.test_result("Creación de directorios", True, "Permisos correctos")
        except Exception as e:
            self.test_result("Creación de directorios", False, f"Error: {str(e)}")
            
    def test_configuration_files(self):
        """9. Verificar archivos de configuración"""
        self.log(f"\n{Colors.BOLD}⚙️ PRUEBA 9: ARCHIVOS DE CONFIGURACIÓN{Colors.END}")
        
        configs = [
            ('config/prometheus/prometheus.yml', 'Prometheus'),
            ('config/alertmanager/alertmanager.yml', 'AlertManager'),
            ('config/grafana/datasources.yml', 'Grafana Datasources'),
            ('docker-compose.yml', 'Docker Compose')
        ]
        
        for config_path, name in configs:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Basic validation
                    is_valid = len(content) > 0 and not content.isspace()
                    
                    if config_path.endswith('.yml') or config_path.endswith('.yaml'):
                        # Try to validate YAML structure
                        try:
                            import yaml
                            yaml.safe_load(content)
                            detail = "YAML válido"
                        except:
                            is_valid = False
                            detail = "YAML inválido"
                    else:
                        detail = f"{len(content)} caracteres"
                        
                    self.test_result(f"Configuración {name}", is_valid, detail)
                    
                except Exception as e:
                    self.test_result(f"Configuración {name}", False, f"Error: {str(e)}")
            else:
                self.test_result(f"Configuración {name}", False, "Archivo no encontrado")
                
    def test_batch_scripts(self):
        """10. Verificar scripts de automatización"""
        self.log(f"\n{Colors.BOLD}📜 PRUEBA 10: SCRIPTS DE AUTOMATIZACIÓN{Colors.END}")
        
        scripts = [
            'start_optimon_complete.bat',
            'start_smtp_simple.bat',
            'setup.bat'
        ]
        
        for script in scripts:
            exists = os.path.exists(script)
            if exists:
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if script has basic commands
                    has_commands = any(cmd in content.lower() for cmd in ['python', 'docker', 'start'])
                    detail = "Contiene comandos válidos" if has_commands else "Sin comandos reconocidos"
                    
                except:
                    has_commands = False
                    detail = "Error leyendo archivo"
                    
                self.test_result(f"Script {script}", has_commands, detail)
            else:
                self.test_result(f"Script {script}", False, "No encontrado")
                
    def generate_report(self):
        """Generar reporte final"""
        self.log(f"\n{Colors.BOLD}📋 REPORTE FINAL DE PRUEBAS{Colors.END}")
        self.log("=" * 60)
        
        total_tests = len(self.results)
        passed = len(self.passed_tests)
        failed = len(self.failed_tests)
        
        self.log(f"Total de pruebas: {total_tests}")
        self.log(f"Exitosas: {Colors.GREEN}{passed}{Colors.END}")
        self.log(f"Fallidas: {Colors.RED}{failed}{Colors.END}")
        self.log(f"Porcentaje de éxito: {Colors.CYAN}{(passed/total_tests*100):.1f}%{Colors.END}")
        
        if failed > 0:
            self.log(f"\n{Colors.RED}❌ PRUEBAS FALLIDAS:{Colors.END}")
            for test in self.failed_tests:
                self.log(f"  • {test}", Colors.RED)
                
        # Package readiness assessment
        readiness_score = passed / total_tests
        
        if readiness_score >= 0.9:
            self.log(f"\n{Colors.GREEN}🎉 SISTEMA LISTO PARA EMPAQUETADO{Colors.END}")
            self.log(f"{Colors.GREEN}✅ Excelente nivel de completitud ({readiness_score*100:.1f}%){Colors.END}")
        elif readiness_score >= 0.8:
            self.log(f"\n{Colors.YELLOW}⚠️ SISTEMA CASI LISTO{Colors.END}")
            self.log(f"{Colors.YELLOW}⚠️ Nivel aceptable pero revisar fallos ({readiness_score*100:.1f}%){Colors.END}")
        else:
            self.log(f"\n{Colors.RED}❌ SISTEMA NO LISTO{Colors.END}")
            self.log(f"{Colors.RED}❌ Muchos problemas pendientes ({readiness_score*100:.1f}%){Colors.END}")
            
        # Save detailed report
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'success_rate': readiness_score,
            'results': self.results,
            'package_ready': readiness_score >= 0.8
        }
        
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.log(f"\n📄 Reporte detallado guardado en: test_report.json")
        
        return readiness_score >= 0.8
        
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        self.log(f"{Colors.BOLD}{Colors.PURPLE}🚀 OPTIMON - SUITE COMPLETA DE PRUEBAS{Colors.END}")
        self.log(f"{Colors.BOLD}Verificación integral antes del empaquetado{Colors.END}")
        self.log("=" * 60)
        
        test_functions = [
            self.test_system_requirements,
            self.test_file_structure,
            self.test_docker_services,
            self.test_smtp_service,
            self.test_dashboard_service,
            self.test_monitoring_features,
            self.test_api_functionality,
            self.test_installation_logic,
            self.test_configuration_files,
            self.test_batch_scripts
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ Error en {test_func.__name__}: {str(e)}", Colors.RED)
                
        return self.generate_report()

def main():
    """Función principal"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    suite = TestSuite()
    success = suite.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())