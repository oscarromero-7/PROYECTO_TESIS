#!/usr/bin/env python3
"""
OPTIMON - PRUEBAS MODULARES DE FUNCIONALIDADES
Pruebas específicas de cada componente del sistema
"""

import os
import sys
import json
import time
import socket
import requests
import subprocess
import psutil
import tempfile
import threading
from pathlib import Path

class ModularTester:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.results = {}
        self.services_status = {}
        
    def log(self, message, category="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {category}: {message}")
        
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
            
    def test_docker_functionality(self):
        """Prueba 1: Funcionalidad Docker"""
        self.log("🐳 PRUEBA 1: FUNCIONALIDAD DOCKER", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 1.1 Verificar Docker disponible
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
            docker_available = result.returncode == 0
            if docker_available:
                self.log(f"✅ Docker disponible: {result.stdout.strip()}")
                results.append({"test": "Docker disponible", "status": True, "details": result.stdout.strip()})
            else:
                self.log("❌ Docker no disponible")
                results.append({"test": "Docker disponible", "status": False, "details": "No instalado"})
        except Exception as e:
            self.log(f"❌ Error verificando Docker: {str(e)}")
            results.append({"test": "Docker disponible", "status": False, "details": str(e)})
            
        # 1.2 Verificar Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True, timeout=10)
            compose_available = result.returncode == 0
            if compose_available:
                self.log(f"✅ Docker Compose disponible: {result.stdout.strip()}")
                results.append({"test": "Docker Compose disponible", "status": True, "details": result.stdout.strip()})
            else:
                self.log("❌ Docker Compose no disponible")
                results.append({"test": "Docker Compose disponible", "status": False, "details": "No instalado"})
        except Exception as e:
            self.log(f"❌ Error verificando Docker Compose: {str(e)}")
            results.append({"test": "Docker Compose disponible", "status": False, "details": str(e)})
            
        # 1.3 Verificar docker-compose.yml
        compose_file = self.script_dir / 'docker-compose.yml'
        if compose_file.exists():
            self.log("✅ Archivo docker-compose.yml encontrado")
            results.append({"test": "Archivo docker-compose.yml", "status": True, "details": "Encontrado"})
            
            # Verificar contenido
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                services = ['prometheus', 'grafana', 'alertmanager']
                missing_services = []
                for service in services:
                    if service not in content:
                        missing_services.append(service)
                        
                if not missing_services:
                    self.log("✅ Todos los servicios configurados en docker-compose.yml")
                    results.append({"test": "Servicios en docker-compose", "status": True, "details": "Todos presentes"})
                else:
                    self.log(f"❌ Servicios faltantes: {missing_services}")
                    results.append({"test": "Servicios en docker-compose", "status": False, "details": f"Faltantes: {missing_services}"})
                    
            except Exception as e:
                self.log(f"❌ Error leyendo docker-compose.yml: {str(e)}")
                results.append({"test": "Contenido docker-compose", "status": False, "details": str(e)})
        else:
            self.log("❌ Archivo docker-compose.yml no encontrado")
            results.append({"test": "Archivo docker-compose.yml", "status": False, "details": "No encontrado"})
            
        # 1.4 Iniciar servicios Docker
        if docker_available and compose_available:
            self.log("🚀 Iniciando servicios Docker...")
            try:
                os.chdir(self.script_dir)
                result = subprocess.run(['docker-compose', 'up', '-d'], 
                                      capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.log("✅ Servicios Docker iniciados correctamente")
                    results.append({"test": "Inicio servicios Docker", "status": True, "details": "Iniciados correctamente"})
                    
                    # Esperar un poco para que se estabilicen
                    time.sleep(10)
                    
                    # Verificar puertos
                    ports = {'Prometheus': 9090, 'Grafana': 3000, 'AlertManager': 9093}
                    for service, port in ports.items():
                        if self.check_port('localhost', port):
                            self.log(f"✅ {service} disponible en puerto {port}")
                            results.append({"test": f"{service} puerto {port}", "status": True, "details": "Disponible"})
                            self.services_status[service.lower()] = True
                        else:
                            self.log(f"❌ {service} no disponible en puerto {port}")
                            results.append({"test": f"{service} puerto {port}", "status": False, "details": "No disponible"})
                            self.services_status[service.lower()] = False
                else:
                    self.log(f"❌ Error iniciando servicios: {result.stderr}")
                    results.append({"test": "Inicio servicios Docker", "status": False, "details": result.stderr})
                    
            except Exception as e:
                self.log(f"❌ Error iniciando servicios Docker: {str(e)}")
                results.append({"test": "Inicio servicios Docker", "status": False, "details": str(e)})
                
        self.results['docker'] = results
        self.log("🏁 Prueba Docker completada\n")
        
    def test_smtp_functionality(self):
        """Prueba 2: Funcionalidad SMTP"""
        self.log("📧 PRUEBA 2: FUNCIONALIDAD SMTP", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 2.1 Verificar archivo SMTP existe
        smtp_file = self.script_dir / 'optimon_smtp_service.py'
        if smtp_file.exists():
            self.log("✅ Archivo optimon_smtp_service.py encontrado")
            results.append({"test": "Archivo SMTP service", "status": True, "details": "Encontrado"})
        else:
            self.log("❌ Archivo optimon_smtp_service.py no encontrado")
            results.append({"test": "Archivo SMTP service", "status": False, "details": "No encontrado"})
            return
            
        # 2.2 Verificar dependencias Python
        try:
            import smtplib
            import email
            self.log("✅ Librerías SMTP de Python disponibles")
            results.append({"test": "Librerías SMTP Python", "status": True, "details": "Disponibles"})
        except ImportError as e:
            self.log(f"❌ Error importando librerías SMTP: {str(e)}")
            results.append({"test": "Librerías SMTP Python", "status": False, "details": str(e)})
            
        # 2.3 Iniciar servicio SMTP
        self.log("🚀 Iniciando servicio SMTP...")
        try:
            # Iniciar en proceso separado
            smtp_process = subprocess.Popen([sys.executable, str(smtp_file)],
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL,
                                          cwd=self.script_dir)
            
            # Esperar que se inicie
            time.sleep(5)
            
            # Verificar que esté corriendo
            if smtp_process.poll() is None:
                self.log("✅ Proceso SMTP iniciado")
                results.append({"test": "Inicio proceso SMTP", "status": True, "details": "Proceso activo"})
                
                # Verificar puerto
                if self.check_port('localhost', 5555):
                    self.log("✅ Servicio SMTP disponible en puerto 5555")
                    results.append({"test": "SMTP puerto 5555", "status": True, "details": "Disponible"})
                    self.services_status['smtp'] = True
                    
                    # 2.4 Probar health check
                    try:
                        response = requests.get('http://localhost:5555/health', timeout=5)
                        if response.status_code == 200:
                            self.log("✅ Health check SMTP exitoso")
                            results.append({"test": "SMTP health check", "status": True, "details": f"HTTP {response.status_code}"})
                        else:
                            self.log(f"❌ Health check SMTP falló: {response.status_code}")
                            results.append({"test": "SMTP health check", "status": False, "details": f"HTTP {response.status_code}"})
                    except Exception as e:
                        self.log(f"❌ Error en health check SMTP: {str(e)}")
                        results.append({"test": "SMTP health check", "status": False, "details": str(e)})
                        
                else:
                    self.log("❌ Puerto 5555 no disponible")
                    results.append({"test": "SMTP puerto 5555", "status": False, "details": "Puerto no disponible"})
                    self.services_status['smtp'] = False
                    
            else:
                self.log("❌ Proceso SMTP se cerró inmediatamente")
                results.append({"test": "Inicio proceso SMTP", "status": False, "details": "Proceso se cerró"})
                self.services_status['smtp'] = False
                
        except Exception as e:
            self.log(f"❌ Error iniciando SMTP: {str(e)}")
            results.append({"test": "Inicio proceso SMTP", "status": False, "details": str(e)})
            self.services_status['smtp'] = False
            
        # 2.5 Verificar configuración de emails
        email_config = self.script_dir / 'emails_config.json'
        if email_config.exists():
            self.log("✅ Configuración de emails encontrada")
            results.append({"test": "Configuración emails", "status": True, "details": "Archivo encontrado"})
            
            try:
                with open(email_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                if 'recipients' in config and len(config['recipients']) > 0:
                    self.log(f"✅ {len(config['recipients'])} destinatarios configurados")
                    results.append({"test": "Destinatarios configurados", "status": True, "details": f"{len(config['recipients'])} destinatarios"})
                else:
                    self.log("⚠️ No hay destinatarios configurados")
                    results.append({"test": "Destinatarios configurados", "status": False, "details": "Sin destinatarios"})
                    
            except Exception as e:
                self.log(f"❌ Error leyendo configuración: {str(e)}")
                results.append({"test": "Lectura configuración emails", "status": False, "details": str(e)})
        else:
            self.log("⚠️ No hay configuración de emails")
            results.append({"test": "Configuración emails", "status": False, "details": "Archivo no encontrado"})
            
        self.results['smtp'] = results
        self.log("🏁 Prueba SMTP completada\n")
        
    def test_dashboard_functionality(self):
        """Prueba 3: Funcionalidad Dashboard"""
        self.log("🌐 PRUEBA 3: FUNCIONALIDAD DASHBOARD", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 3.1 Verificar archivo dashboard existe
        dashboard_file = self.script_dir / 'optimon_dashboard.py'
        if dashboard_file.exists():
            self.log("✅ Archivo optimon_dashboard.py encontrado")
            results.append({"test": "Archivo dashboard", "status": True, "details": "Encontrado"})
        else:
            self.log("❌ Archivo optimon_dashboard.py no encontrado")
            results.append({"test": "Archivo dashboard", "status": False, "details": "No encontrado"})
            return
            
        # 3.2 Verificar dependencias Flask
        try:
            import flask
            self.log(f"✅ Flask disponible: {flask.__version__}")
            results.append({"test": "Flask disponible", "status": True, "details": f"Versión {flask.__version__}"})
        except ImportError:
            self.log("❌ Flask no disponible")
            results.append({"test": "Flask disponible", "status": False, "details": "No instalado"})
            
        # 3.3 Verificar templates
        templates_dir = self.script_dir / 'templates'
        if templates_dir.exists():
            self.log("✅ Directorio templates encontrado")
            results.append({"test": "Directorio templates", "status": True, "details": "Encontrado"})
            
            # Verificar templates específicos
            required_templates = ['base.html', 'dashboard.html', 'monitoring.html', 'emails.html']
            missing_templates = []
            for template in required_templates:
                if not (templates_dir / template).exists():
                    missing_templates.append(template)
                    
            if not missing_templates:
                self.log("✅ Todos los templates requeridos encontrados")
                results.append({"test": "Templates requeridos", "status": True, "details": "Todos presentes"})
            else:
                self.log(f"❌ Templates faltantes: {missing_templates}")
                results.append({"test": "Templates requeridos", "status": False, "details": f"Faltantes: {missing_templates}"})
        else:
            self.log("❌ Directorio templates no encontrado")
            results.append({"test": "Directorio templates", "status": False, "details": "No encontrado"})
            
        # 3.4 Iniciar dashboard manualmente para prueba
        self.log("🚀 Iniciando dashboard para prueba...")
        try:
            # Iniciar en proceso separado
            dashboard_process = subprocess.Popen([sys.executable, str(dashboard_file)],
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL,
                                               cwd=self.script_dir)
            
            # Esperar que se inicie
            time.sleep(8)
            
            # Verificar que esté corriendo
            if dashboard_process.poll() is None:
                self.log("✅ Proceso dashboard iniciado")
                results.append({"test": "Inicio proceso dashboard", "status": True, "details": "Proceso activo"})
                
                # Verificar puerto (esperar más tiempo)
                max_wait = 30
                dashboard_available = False
                for i in range(max_wait):
                    if self.check_port('localhost', 8080):
                        dashboard_available = True
                        break
                    time.sleep(1)
                    
                if dashboard_available:
                    self.log("✅ Dashboard disponible en puerto 8080")
                    results.append({"test": "Dashboard puerto 8080", "status": True, "details": "Disponible"})
                    self.services_status['dashboard'] = True
                    
                    # 3.5 Probar endpoints específicos
                    endpoints = [
                        ('/', 'Página principal'),
                        ('/api/system-status', 'API estado sistema'),
                        ('/monitoring', 'Panel monitoreo'),
                        ('/emails', 'Panel emails')
                    ]
                    
                    for endpoint, name in endpoints:
                        try:
                            response = requests.get(f'http://localhost:8080{endpoint}', timeout=10)
                            if response.status_code == 200:
                                self.log(f"✅ {name}: HTTP {response.status_code}")
                                results.append({"test": f"Endpoint {name}", "status": True, "details": f"HTTP {response.status_code}"})
                            else:
                                self.log(f"❌ {name}: HTTP {response.status_code}")
                                results.append({"test": f"Endpoint {name}", "status": False, "details": f"HTTP {response.status_code}"})
                        except Exception as e:
                            self.log(f"❌ Error en {name}: {str(e)}")
                            results.append({"test": f"Endpoint {name}", "status": False, "details": str(e)})
                            
                else:
                    self.log("❌ Dashboard no disponible en puerto 8080")
                    results.append({"test": "Dashboard puerto 8080", "status": False, "details": "No disponible tras espera"})
                    self.services_status['dashboard'] = False
                    
            else:
                self.log("❌ Proceso dashboard se cerró inmediatamente")
                results.append({"test": "Inicio proceso dashboard", "status": False, "details": "Proceso se cerró"})
                self.services_status['dashboard'] = False
                
        except Exception as e:
            self.log(f"❌ Error iniciando dashboard: {str(e)}")
            results.append({"test": "Inicio proceso dashboard", "status": False, "details": str(e)})
            self.services_status['dashboard'] = False
            
        self.results['dashboard'] = results
        self.log("🏁 Prueba Dashboard completada\n")
        
    def test_monitoring_functionality(self):
        """Prueba 4: Funcionalidad de Monitoreo"""
        self.log("📊 PRUEBA 4: FUNCIONALIDAD DE MONITOREO", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 4.1 Verificar psutil para métricas de sistema
        try:
            import psutil
            self.log(f"✅ psutil disponible: {psutil.__version__}")
            results.append({"test": "psutil disponible", "status": True, "details": f"Versión {psutil.__version__}"})
            
            # Probar métricas básicas
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            self.log(f"✅ CPU: {cpu}%")
            self.log(f"✅ Memoria: {memory.percent}%")
            self.log(f"✅ Disco: {disk.percent}%")
            
            results.append({"test": "Métricas CPU", "status": True, "details": f"{cpu}%"})
            results.append({"test": "Métricas Memoria", "status": True, "details": f"{memory.percent}%"})
            results.append({"test": "Métricas Disco", "status": True, "details": f"{disk.percent}%"})
            
        except ImportError:
            self.log("❌ psutil no disponible")
            results.append({"test": "psutil disponible", "status": False, "details": "No instalado"})
        except Exception as e:
            self.log(f"❌ Error obteniendo métricas: {str(e)}")
            results.append({"test": "Obtención métricas", "status": False, "details": str(e)})
            
        # 4.2 Verificar configuración de Prometheus
        prometheus_config = self.script_dir / 'config' / 'prometheus' / 'prometheus.yml'
        if prometheus_config.exists():
            self.log("✅ Configuración Prometheus encontrada")
            results.append({"test": "Config Prometheus", "status": True, "details": "Archivo encontrado"})
            
            try:
                with open(prometheus_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar configuraciones básicas
                if 'scrape_configs' in content:
                    self.log("✅ Configuración scrape_configs presente")
                    results.append({"test": "Scrape configs", "status": True, "details": "Configurado"})
                else:
                    self.log("❌ Configuración scrape_configs faltante")
                    results.append({"test": "Scrape configs", "status": False, "details": "No configurado"})
                    
            except Exception as e:
                self.log(f"❌ Error leyendo config Prometheus: {str(e)}")
                results.append({"test": "Lectura config Prometheus", "status": False, "details": str(e)})
        else:
            self.log("❌ Configuración Prometheus no encontrada")
            results.append({"test": "Config Prometheus", "status": False, "details": "Archivo no encontrado"})
            
        # 4.3 Probar API de Prometheus (si está disponible)
        if self.services_status.get('prometheus', False):
            try:
                response = requests.get('http://localhost:9090/api/v1/targets', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    targets = data.get('data', {}).get('activeTargets', [])
                    self.log(f"✅ API Prometheus: {len(targets)} targets activos")
                    results.append({"test": "API Prometheus targets", "status": True, "details": f"{len(targets)} targets"})
                else:
                    self.log(f"❌ API Prometheus error: {response.status_code}")
                    results.append({"test": "API Prometheus targets", "status": False, "details": f"HTTP {response.status_code}"})
            except Exception as e:
                self.log(f"❌ Error API Prometheus: {str(e)}")
                results.append({"test": "API Prometheus targets", "status": False, "details": str(e)})
        else:
            self.log("⚠️ Prometheus no disponible para probar API")
            results.append({"test": "API Prometheus targets", "status": False, "details": "Prometheus no disponible"})
            
        # 4.4 Verificar configuración AlertManager
        alertmanager_config = self.script_dir / 'config' / 'alertmanager' / 'alertmanager.yml'
        if alertmanager_config.exists():
            self.log("✅ Configuración AlertManager encontrada")
            results.append({"test": "Config AlertManager", "status": True, "details": "Archivo encontrado"})
            
            try:
                with open(alertmanager_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar configuraciones básicas
                if 'webhook_configs' in content:
                    self.log("✅ Configuración webhook presente")
                    results.append({"test": "AlertManager webhooks", "status": True, "details": "Configurado"})
                else:
                    self.log("❌ Configuración webhook faltante")
                    results.append({"test": "AlertManager webhooks", "status": False, "details": "No configurado"})
                    
            except Exception as e:
                self.log(f"❌ Error leyendo config AlertManager: {str(e)}")
                results.append({"test": "Lectura config AlertManager", "status": False, "details": str(e)})
        else:
            self.log("❌ Configuración AlertManager no encontrada")
            results.append({"test": "Config AlertManager", "status": False, "details": "Archivo no encontrado"})
            
        self.results['monitoring'] = results
        self.log("🏁 Prueba Monitoreo completada\n")
        
    def test_installation_functionality(self):
        """Prueba 5: Funcionalidad de Instalación"""
        self.log("⚙️ PRUEBA 5: FUNCIONALIDAD DE INSTALACIÓN", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 5.1 Verificar funciones de instalación en dashboard
        dashboard_file = self.script_dir / 'optimon_dashboard.py'
        if dashboard_file.exists():
            try:
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar funciones de instalación
                install_functions = [
                    ('def install_node_exporter', 'Instalación Node Exporter'),
                    ('urllib.request.urlretrieve', 'Descarga de archivos'),
                    ('zipfile', 'Extracción de archivos'),
                    ('/api/local/install-node-exporter', 'API instalación')
                ]
                
                for func, name in install_functions:
                    if func in content:
                        self.log(f"✅ {name}: Implementado")
                        results.append({"test": name, "status": True, "details": "Implementado"})
                    else:
                        self.log(f"❌ {name}: No implementado")
                        results.append({"test": name, "status": False, "details": "No implementado"})
                        
            except Exception as e:
                self.log(f"❌ Error verificando funciones: {str(e)}")
                results.append({"test": "Verificación funciones instalación", "status": False, "details": str(e)})
        else:
            self.log("❌ Dashboard no disponible para verificar instalación")
            results.append({"test": "Archivo dashboard para instalación", "status": False, "details": "No encontrado"})
            
        # 5.2 Probar creación de directorios
        try:
            test_dir = tempfile.mkdtemp(prefix='optimon_test_install_')
            os.rmdir(test_dir)
            self.log("✅ Permisos para crear directorios: OK")
            results.append({"test": "Permisos creación directorios", "status": True, "details": "Permisos correctos"})
        except Exception as e:
            self.log(f"❌ Error permisos directorios: {str(e)}")
            results.append({"test": "Permisos creación directorios", "status": False, "details": str(e)})
            
        # 5.3 Verificar dependencias de descarga
        try:
            import urllib.request
            import zipfile
            self.log("✅ Librerías de descarga disponibles")
            results.append({"test": "Librerías descarga", "status": True, "details": "urllib y zipfile disponibles"})
        except ImportError as e:
            self.log(f"❌ Librerías de descarga no disponibles: {str(e)}")
            results.append({"test": "Librerías descarga", "status": False, "details": str(e)})
            
        # 5.4 Probar API de instalación (si dashboard está disponible)
        if self.services_status.get('dashboard', False):
            try:
                # Probar endpoint de instalación (sin ejecutar realmente)
                response = requests.get('http://localhost:8080/api/local/install-node-exporter', timeout=10)
                # Puede dar error porque es POST, pero verificamos que el endpoint existe
                if response.status_code in [200, 405]:  # 405 = Method Not Allowed (esperado para GET en POST endpoint)
                    self.log("✅ API instalación disponible")
                    results.append({"test": "API instalación disponible", "status": True, "details": "Endpoint existe"})
                else:
                    self.log(f"❌ API instalación no disponible: {response.status_code}")
                    results.append({"test": "API instalación disponible", "status": False, "details": f"HTTP {response.status_code}"})
            except Exception as e:
                self.log(f"❌ Error verificando API instalación: {str(e)}")
                results.append({"test": "API instalación disponible", "status": False, "details": str(e)})
        else:
            self.log("⚠️ Dashboard no disponible para probar API instalación")
            results.append({"test": "API instalación disponible", "status": False, "details": "Dashboard no disponible"})
            
        self.results['installation'] = results
        self.log("🏁 Prueba Instalación completada\n")
        
    def test_automation_functionality(self):
        """Prueba 6: Funcionalidad de Automatización"""
        self.log("🤖 PRUEBA 6: FUNCIONALIDAD DE AUTOMATIZACIÓN", "TEST")
        self.log("=" * 50)
        
        results = []
        
        # 6.1 Verificar scripts de automatización
        automation_scripts = [
            ('start_optimon_auto.bat', 'Script inicio automático'),
            ('stop_optimon.bat', 'Script parada'),
            ('optimon_auto_starter.py', 'Iniciador automático Python'),
            ('check_optimon_status.bat', 'Verificador estado')
        ]
        
        for script_file, name in automation_scripts:
            script_path = self.script_dir / script_file
            if script_path.exists():
                self.log(f"✅ {name}: Encontrado")
                results.append({"test": name, "status": True, "details": "Archivo encontrado"})
                
                # Verificar contenido básico
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if len(content) > 100:  # Archivo no vacío
                        self.log(f"✅ {name}: Contenido válido")
                        results.append({"test": f"{name} contenido", "status": True, "details": f"{len(content)} caracteres"})
                    else:
                        self.log(f"❌ {name}: Archivo muy pequeño")
                        results.append({"test": f"{name} contenido", "status": False, "details": "Archivo muy pequeño"})
                        
                except Exception as e:
                    self.log(f"❌ Error leyendo {name}: {str(e)}")
                    results.append({"test": f"{name} contenido", "status": False, "details": str(e)})
            else:
                self.log(f"❌ {name}: No encontrado")
                results.append({"test": name, "status": False, "details": "Archivo no encontrado"})
                
        # 6.2 Verificar documentación
        docs = [
            ('README.md', 'Documentación principal'),
            ('QUICK_START.md', 'Guía inicio rápido')
        ]
        
        for doc_file, name in docs:
            doc_path = self.script_dir / doc_file
            if doc_path.exists():
                self.log(f"✅ {name}: Encontrado")
                results.append({"test": name, "status": True, "details": "Encontrado"})
            else:
                self.log(f"❌ {name}: No encontrado")
                results.append({"test": name, "status": False, "details": "No encontrado"})
                
        # 6.3 Verificar funcionalidad del iniciador automático
        auto_starter = self.script_dir / 'optimon_auto_starter.py'
        if auto_starter.exists():
            try:
                with open(auto_starter, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar funciones principales
                key_functions = [
                    'start_docker_services',
                    'start_smtp_service', 
                    'start_dashboard_service',
                    'verify_all_services'
                ]
                
                missing_functions = []
                for func in key_functions:
                    if func not in content:
                        missing_functions.append(func)
                        
                if not missing_functions:
                    self.log("✅ Todas las funciones del iniciador automático presentes")
                    results.append({"test": "Funciones iniciador automático", "status": True, "details": "Todas presentes"})
                else:
                    self.log(f"❌ Funciones faltantes: {missing_functions}")
                    results.append({"test": "Funciones iniciador automático", "status": False, "details": f"Faltantes: {missing_functions}"})
                    
            except Exception as e:
                self.log(f"❌ Error verificando iniciador automático: {str(e)}")
                results.append({"test": "Verificación iniciador automático", "status": False, "details": str(e)})
                
        self.results['automation'] = results
        self.log("🏁 Prueba Automatización completada\n")
        
    def generate_comprehensive_report(self):
        """Generar reporte completo de todas las pruebas"""
        self.log("📋 GENERANDO REPORTE COMPLETO", "REPORT")
        self.log("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        # Contar resultados por categoría
        category_stats = {}
        for category, tests in self.results.items():
            category_passed = sum(1 for test in tests if test['status'])
            category_total = len(tests)
            category_stats[category] = {
                'passed': category_passed,
                'total': category_total,
                'percentage': (category_passed / category_total * 100) if category_total > 0 else 0
            }
            total_tests += category_total
            passed_tests += category_passed
            
        # Mostrar estadísticas por categoría
        self.log("\n📊 RESULTADOS POR CATEGORÍA:")
        for category, stats in category_stats.items():
            status = "✅" if stats['percentage'] >= 80 else "⚠️" if stats['percentage'] >= 60 else "❌"
            self.log(f"{status} {category.upper()}: {stats['passed']}/{stats['total']} ({stats['percentage']:.1f}%)")
            
        # Estadísticas generales
        overall_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.log("\n📈 ESTADÍSTICAS GENERALES:")
        self.log(f"Total de pruebas: {total_tests}")
        self.log(f"Pruebas exitosas: {passed_tests}")
        self.log(f"Pruebas fallidas: {total_tests - passed_tests}")
        self.log(f"Porcentaje de éxito: {overall_percentage:.1f}%")
        
        # Estado de servicios
        self.log("\n🔧 ESTADO DE SERVICIOS:")
        for service, status in self.services_status.items():
            icon = "✅" if status else "❌"
            self.log(f"{icon} {service.title()}: {'Funcionando' if status else 'No disponible'}")
            
        # Evaluación de calidad
        self.log("\n🎯 EVALUACIÓN DE CALIDAD:")
        if overall_percentage >= 90:
            self.log("🎉 EXCELENTE - Sistema listo para producción")
            quality = "EXCELENTE"
        elif overall_percentage >= 80:
            self.log("✅ BUENO - Sistema casi listo, revisar fallos menores")
            quality = "BUENO"
        elif overall_percentage >= 70:
            self.log("⚠️ ACEPTABLE - Necesita mejoras antes de producción")
            quality = "ACEPTABLE"
        else:
            self.log("❌ CRÍTICO - Muchos problemas por resolver")
            quality = "CRÍTICO"
            
        # Guardar reporte detallado
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_stats': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_percentage': overall_percentage,
                'quality_rating': quality
            },
            'category_stats': category_stats,
            'services_status': self.services_status,
            'detailed_results': self.results
        }
        
        with open(self.script_dir / 'detailed_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.log(f"\n📄 Reporte detallado guardado en: detailed_test_report.json")
        
        return overall_percentage >= 70
        
    def run_all_modular_tests(self):
        """Ejecutar todas las pruebas modulares"""
        self.log("🧪 OPTIMON - PRUEBAS MODULARES DE FUNCIONALIDADES", "MAIN")
        self.log("Verificación detallada de cada componente del sistema")
        self.log("=" * 70)
        
        # Ejecutar pruebas en orden
        try:
            self.test_docker_functionality()
            self.test_smtp_functionality()
            self.test_dashboard_functionality()
            self.test_monitoring_functionality()
            self.test_installation_functionality()
            self.test_automation_functionality()
        except KeyboardInterrupt:
            self.log("\n⚠️ Pruebas interrumpidas por el usuario")
            return False
        except Exception as e:
            self.log(f"\n❌ Error durante las pruebas: {str(e)}")
            return False
            
        # Generar reporte final
        return self.generate_comprehensive_report()

def main():
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    tester = ModularTester()
    success = tester.run_all_modular_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())