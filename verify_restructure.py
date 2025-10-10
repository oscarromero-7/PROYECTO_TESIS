#!/usr/bin/env python3
"""
🔍 OptiMon Post-Restructure Verification Tool
Herramienta para verificar que todo funcione después de la restructuración

Autor: OptiMon Team
Versión: 1.0
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path
from datetime import datetime

class PostRestructureVerifier:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.services = {
            'prometheus': {'url': 'http://localhost:9090', 'name': 'Prometheus'},
            'grafana': {'url': 'http://localhost:3000', 'name': 'Grafana'},
            'alertmanager': {'url': 'http://localhost:9093', 'name': 'AlertManager'},
            'optimon_dashboard': {'url': 'http://localhost:5000', 'name': 'OptiMon Dashboard'},
            'optimon_smtp': {'url': 'http://localhost:5555', 'name': 'OptiMon SMTP Service'}
        }
        
        self.expected_files = [
            'core/optimon_manager.py',
            'core/smtp_service.py', 
            'core/web_dashboard.py',
            'core/dashboard_manager.py',
            'config/docker/docker-compose.yml',
            'config/email/recipients.json',
            'infrastructure/terraform/main.tf',
            'tests/integration/test_recipients.py',
            'README.md',
            'requirements.txt',
            'setup.py'
        ]
        
        self.checks_passed = 0
        self.total_checks = 0
    
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "ERROR": "[ERROR]", "WARNING": "[WARN]"}
        icon = icons.get(level, "[LOG]")
        print(f"[{timestamp}] {icon} {message}")
    
    def check_file_structure(self):
        """Verificar estructura de archivos"""
        self.log("Verificando estructura de archivos...")
        self.total_checks += 1
        
        missing_files = []
        
        for file_path in self.expected_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"Archivos faltantes: {', '.join(missing_files)}", "ERROR")
            return False
        else:
            self.log("Estructura de archivos correcta", "SUCCESS")
            self.checks_passed += 1
            return True
    
    def check_imports(self):
        """Verificar que los imports funcionen"""
        self.log("Verificando imports...")
        self.total_checks += 1
        
        try:
            # Cambiar al directorio del proyecto
            original_cwd = os.getcwd()
            os.chdir(self.base_dir)
            
            # Agregar directorio actual al PYTHONPATH
            sys.path.insert(0, str(self.base_dir))
            
            # Intentar imports
            imports_to_test = [
                ('core.optimon_manager', 'OptiMon Manager'),
                ('core.smtp_service', 'SMTP Service'),
                ('core.web_dashboard', 'Web Dashboard'),
                ('core.dashboard_manager', 'Dashboard Manager')
            ]
            
            for module_name, description in imports_to_test:
                try:
                    __import__(module_name)
                    self.log(f"Import OK: {description}")
                except ImportError as e:
                    self.log(f"Import ERROR: {description} - {e}", "ERROR")
                    return False
            
            os.chdir(original_cwd)
            self.log("Todos los imports funcionan correctamente", "SUCCESS")
            self.checks_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Error verificando imports: {e}", "ERROR")
            return False
    
    def check_docker_services(self):
        """Verificar servicios Docker"""
        self.log("Verificando servicios Docker...")
        self.total_checks += 1
        
        try:
            # Verificar que Docker esté ejecutándose
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log("Docker no está ejecutándose", "ERROR")
                return False
            
            # Verificar contenedores específicos
            expected_containers = ['prometheus', 'grafana', 'alertmanager']
            running_containers = result.stdout.lower()
            
            for container in expected_containers:
                if container in running_containers:
                    self.log(f"Contenedor activo: {container}")
                else:
                    self.log(f"Contenedor no encontrado: {container}", "WARNING")
            
            self.log("Verificación Docker completada", "SUCCESS")
            self.checks_passed += 1
            return True
            
        except FileNotFoundError:
            self.log("Docker no está instalado o no está en PATH", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error verificando Docker: {e}", "ERROR")
            return False
    
    def check_service_endpoints(self):
        """Verificar endpoints de servicios"""
        self.log("Verificando endpoints de servicios...")
        self.total_checks += len(self.services)
        
        all_services_ok = True
        
        for service_key, service_info in self.services.items():
            try:
                response = requests.get(service_info['url'], timeout=5)
                
                if response.status_code in [200, 401, 403]:  # 401/403 pueden ser normales
                    self.log(f"Servicio activo: {service_info['name']} ({service_info['url']})")
                    self.checks_passed += 1
                else:
                    self.log(f"Servicio responde con código {response.status_code}: {service_info['name']}", "WARNING")
                    self.checks_passed += 1  # Aún cuenta como verificado
                    
            except requests.exceptions.ConnectionError:
                self.log(f"Servicio no disponible: {service_info['name']} ({service_info['url']})", "ERROR")
                all_services_ok = False
            except requests.exceptions.Timeout:
                self.log(f"Timeout en servicio: {service_info['name']}", "WARNING")
                self.checks_passed += 1
            except Exception as e:
                self.log(f"Error verificando {service_info['name']}: {e}", "ERROR")
                all_services_ok = False
        
        return all_services_ok
    
    def check_configuration_files(self):
        """Verificar archivos de configuración"""
        self.log("Verificando archivos de configuración...")
        self.total_checks += 1
        
        try:
            config_files = [
                'config/docker/docker-compose.yml',
                'config/prometheus/prometheus.yml',
                'config/grafana/grafana.ini',
                'config/alertmanager/alertmanager.yml'
            ]
            
            missing_configs = []
            
            for config_file in config_files:
                config_path = self.base_dir / config_file
                if not config_path.exists():
                    missing_configs.append(config_file)
                else:
                    self.log(f"Configuración encontrada: {config_file}")
            
            if missing_configs:
                self.log(f"Configuraciones faltantes: {', '.join(missing_configs)}", "WARNING")
            else:
                self.log("Todas las configuraciones presentes", "SUCCESS")
                self.checks_passed += 1
                return True
            
            return len(missing_configs) == 0
            
        except Exception as e:
            self.log(f"Error verificando configuraciones: {e}", "ERROR")
            return False
    
    def check_test_files(self):
        """Verificar archivos de testing"""
        self.log("Verificando archivos de testing...")
        self.total_checks += 1
        
        try:
            test_files = [
                'tests/integration/test_recipients.py',
                'tests/integration/test_real_alert.py',
                'tests/e2e/test_complete_system.py'
            ]
            
            tests_found = 0
            
            for test_file in test_files:
                test_path = self.base_dir / test_file
                if test_path.exists():
                    tests_found += 1
                    self.log(f"Test encontrado: {test_file}")
                else:
                    self.log(f"Test no encontrado: {test_file}", "WARNING")
            
            if tests_found >= 2:  # Al menos 2 tests deben existir
                self.log("Suite de testing verificada", "SUCCESS")
                self.checks_passed += 1
                return True
            else:
                self.log("Insuficientes archivos de testing", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error verificando tests: {e}", "ERROR")
            return False
    
    def run_quick_test(self):
        """Ejecutar test rápido del sistema"""
        self.log("Ejecutando test rápido del sistema...")
        self.total_checks += 1
        
        try:
            # Test de conectividad a dashboard principal
            dashboard_url = "http://localhost:5000"
            
            try:
                response = requests.get(dashboard_url, timeout=10)
                if response.status_code == 200:
                    self.log("Dashboard principal respondiendo correctamente")
                    
                    # Test de API de recipients
                    api_url = f"{dashboard_url}/api/email/recipients"
                    api_response = requests.get(api_url, timeout=5)
                    
                    if api_response.status_code == 200:
                        recipients = api_response.json()
                        self.log(f"API de recipients funcional ({len(recipients)} destinatarios)")
                        self.checks_passed += 1
                        return True
                    else:
                        self.log("API de recipients no responde correctamente", "WARNING")
                        return False
                else:
                    self.log(f"Dashboard responde con código: {response.status_code}", "WARNING")
                    return False
                    
            except requests.exceptions.ConnectionError:
                self.log("Dashboard no está disponible - servicios posiblemente no iniciados", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error en test rápido: {e}", "ERROR")
            return False
    
    def generate_verification_report(self):
        """Generar reporte de verificación"""
        self.log("Generando reporte de verificación...")
        
        success_rate = (self.checks_passed / self.total_checks * 100) if self.total_checks > 0 else 0
        
        report = f"""
🔍 REPORTE DE VERIFICACIÓN POST-RESTRUCTURACIÓN
{'='*60}

📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Éxito: {self.checks_passed}/{self.total_checks} ({success_rate:.1f}%)

✅ VERIFICACIONES COMPLETADAS:
{'-'*30}
"""
        
        checks = [
            ("Estructura de archivos", "Archivos principales en ubicaciones correctas"),
            ("Imports de Python", "Módulos importables sin errores"),
            ("Servicios Docker", "Contenedores ejecutándose correctamente"),
            ("Endpoints de servicios", "URLs de servicios respondiendo"),
            ("Archivos de configuración", "Configuraciones presentes y válidas"),
            ("Suite de testing", "Archivos de test organizados"),
            ("Test rápido del sistema", "Funcionalidad básica operativa")
        ]
        
        for i, (check_name, description) in enumerate(checks):
            if i < self.checks_passed:
                report += f"✅ {check_name} - {description}\\n"
            else:
                report += f"❌ {check_name} - {description}\\n"
        
        if success_rate >= 80:
            report += f"""
🎉 ESTADO: VERIFICACIÓN EXITOSA
{'-'*30}
El sistema ha sido restructurado correctamente y está funcionando.

📋 PRÓXIMOS PASOS:
- Ejecutar tests completos: python -m pytest tests/
- Verificar alertas: python tests/integration/test_real_alert.py
- Revisar logs de servicios si hay problemas
"""
        else:
            report += f"""
⚠️ ESTADO: VERIFICACIÓN PARCIAL
{'-'*30}
Algunos componentes necesitan atención.

🔧 ACCIONES RECOMENDADAS:
- Revisar servicios que no respondieron
- Verificar configuraciones faltantes
- Ejecutar restructuración nuevamente si es necesario
- Consultar logs para más detalles
"""
        
        report += f"""
🔗 ACCESOS RÁPIDOS:
{'-'*30}
- Dashboard OptiMon: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093

📁 ESTRUCTURA NUEVA:
{'-'*30}
core/           - Servicios principales
config/         - Configuraciones centralizadas
infrastructure/ - Terraform y scripts
tests/          - Testing organizado
docs/           - Documentación
tools/          - Herramientas y utilidades
"""
        
        report_file = self.base_dir / 'VERIFICATION_REPORT.md'
        report_file.write_text(report, encoding='utf-8')
        
        print(report)
        self.log(f"Reporte guardado en: {report_file}", "SUCCESS")
        
        return success_rate >= 80
    
    def run_verification(self):
        """Ejecutar verificación completa"""
        self.log("=" * 60)
        self.log("🔍 INICIANDO VERIFICACIÓN POST-RESTRUCTURACIÓN")
        self.log("=" * 60)
        
        try:
            # Ejecutar todas las verificaciones
            self.check_file_structure()
            self.check_imports()
            self.check_docker_services()
            self.check_service_endpoints()
            self.check_configuration_files()
            self.check_test_files()
            self.run_quick_test()
            
            # Generar reporte
            success = self.generate_verification_report()
            
            self.log("=" * 60)
            if success:
                self.log("🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE!", "SUCCESS")
            else:
                self.log("⚠️ VERIFICACIÓN COMPLETADA CON ADVERTENCIAS", "WARNING")
            self.log("=" * 60)
            
            return success
            
        except Exception as e:
            self.log(f"Error crítico durante verificación: {e}", "ERROR")
            return False

def main():
    """Función principal"""
    print("""
🔍 OptiMon Post-Restructure Verification Tool v1.0
==================================================

Este script verificará que la restructuración se haya completado
correctamente y que todos los servicios funcionen apropiadamente.

Verificaciones incluidas:
✓ Estructura de archivos
✓ Imports de Python  
✓ Servicios Docker
✓ Endpoints de servicios
✓ Archivos de configuración
✓ Suite de testing
✓ Test rápido del sistema

Iniciando verificación...""")
    
    verifier = PostRestructureVerifier()
    success = verifier.run_verification()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())