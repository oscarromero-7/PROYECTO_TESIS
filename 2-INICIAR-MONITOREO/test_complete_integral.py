#!/usr/bin/env python3
"""
🧪 OPTIMON - PRUEBA COMPLETA INTEGRAL
=====================================

Prueba completa que incluye:
1. Configuración de credenciales de nube (AWS, Azure, GCP)
2. Configuración de destinatarios de alertas
3. Instalación de Windows Exporter
4. Verificación de todos los servicios
5. Pruebas de email
6. Verificación de APIs del dashboard
7. Validación de integración completa

Autor: OptiMon Team
Versión: 2.0
Fecha: Octubre 2025
"""

import requests
import json
import time
import sys
from datetime import datetime

class OptiMonCompleteTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.service_manager = None
        
    def setup_services(self):
        """Configurar y iniciar servicios en segundo plano"""
        try:
            import subprocess
            import time
            
            self.log("Iniciando servicios OptiMon en segundo plano...")
            
            # Detener servicios existentes
            subprocess.run([
                sys.executable, "optimon_service_manager.py", "--stop"
            ], check=False, capture_output=True)
            
            time.sleep(3)
            
            # Iniciar gestor de servicios en segundo plano
            self.service_manager = subprocess.Popen([
                sys.executable, "optimon_service_manager.py", "--daemon"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Esperar a que los servicios se inicien
            self.log("Esperando a que los servicios se inicien...")
            
            max_wait = 60  # 60 segundos máximo
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    # Verificar dashboard
                    response = requests.get(self.base_url, timeout=5)
                    if response.status_code == 200:
                        self.log("Servicios iniciados correctamente", "SUCCESS")
                        return True
                except:
                    pass
                
                time.sleep(5)
                wait_time += 5
                self.log(f"Esperando servicios... ({wait_time}/{max_wait}s)")
            
            self.log("Timeout esperando servicios", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Error configurando servicios: {e}", "ERROR")
            return False
    
    def cleanup_services(self):
        """Limpiar servicios al finalizar"""
        try:
            if self.service_manager:
                self.service_manager.terminate()
                self.service_manager.wait(timeout=10)
        except:
            pass
        
    def log(self, message, level="INFO"):
        """Log con timestamp y formato"""
        timestamp = time.strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "TEST": "🧪"}
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
    
    def run_test(self, test_name, test_func):
        """Ejecutar una prueba individual"""
        self.total_tests += 1
        self.log(f"Ejecutando: {test_name}", "TEST")
        
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                self.test_results[test_name] = "PASS"
                self.log(f"{test_name}: PASS", "SUCCESS")
            else:
                self.test_results[test_name] = "FAIL"
                self.log(f"{test_name}: FAIL", "ERROR")
            return result
        except Exception as e:
            self.test_results[test_name] = f"ERROR: {str(e)}"
            self.log(f"{test_name}: ERROR - {str(e)}", "ERROR")
            return False
    
    def test_dashboard_availability(self):
        """Prueba 1: Verificar que el dashboard esté disponible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_cloud_credentials_api(self):
        """Prueba 2: Configurar credenciales de nube"""
        # Configurar AWS
        aws_credentials = {
            "aws": {
                "access_key": "AKIATEST123456789012",
                "secret_key": "TEST_SECRET_KEY_FOR_DEMO_PURPOSES_ONLY",
                "region": "us-east-1"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/cloud/credentials",
                json=aws_credentials,
                timeout=10
            )
            if response.status_code != 200:
                return False
            
            # Verificar que se guardó
            response = requests.get(f"{self.base_url}/api/cloud/credentials", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('aws_configured', False)
            return False
        except:
            return False
    
    def test_azure_credentials_api(self):
        """Prueba 3: Configurar credenciales Azure"""
        azure_credentials = {
            "azure": {
                "client_id": "12345678-1234-1234-1234-123456789012",
                "client_secret": "TEST~CLIENT.SECRET-FOR_DEMO",
                "tenant_id": "87654321-4321-4321-4321-210987654321",
                "subscription_id": "11111111-2222-3333-4444-555555555555"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/cloud/credentials",
                json=azure_credentials,
                timeout=10
            )
            if response.status_code != 200:
                return False
            
            # Verificar que se guardó
            response = requests.get(f"{self.base_url}/api/cloud/credentials", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('azure_configured', False)
            return False
        except:
            return False
    
    def test_email_recipients_api(self):
        """Prueba 4: Configurar destinatarios de email"""
        try:
            # Primero limpiar destinatarios existentes
            recipients_response = requests.get(f"{self.base_url}/api/email/recipients", timeout=10)
            if recipients_response.status_code == 200:
                current_recipients = recipients_response.json().get('recipients', [])
                for recipient in current_recipients:
                    requests.delete(
                        f"{self.base_url}/api/email/recipients",
                        json={"email": recipient['email']},
                        timeout=10
                    )
            
            # Agregar destinatarios de prueba
            test_recipients = [
                {
                    "email": "admin@empresa-test.com",
                    "name": "Administrador Test",
                    "active": True
                },
                {
                    "email": "alerts@empresa-test.com", 
                    "name": "Alertas Test",
                    "active": True
                }
            ]
            
            for recipient in test_recipients:
                response = requests.post(
                    f"{self.base_url}/api/email/recipients",
                    json={"add_recipient": recipient},
                    timeout=10
                )
                if response.status_code != 200:
                    return False
            
            # Verificar que se agregaron
            response = requests.get(f"{self.base_url}/api/email/recipients", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return len(data.get('recipients', [])) >= 2
            return False
        except:
            return False
    
    def test_windows_exporter_status(self):
        """Prueba 5: Verificar estado de Windows Exporter"""
        try:
            response = requests.get(f"{self.base_url}/api/local/windows-exporter/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('running', False) and data.get('metrics_count', 0) > 1000
            return False
        except:
            return False
    
    def test_windows_exporter_installation(self):
        """Prueba 6: Instalar/verificar Windows Exporter"""
        try:
            response = requests.post(f"{self.base_url}/api/local/install-node-exporter", timeout=120)
            if response.status_code == 200:
                data = response.json()
                # Esperar un poco para que se inicie
                time.sleep(5)
                # Verificar que está funcionando
                return self.test_windows_exporter_status()
            return False
        except:
            return False
    
    def test_email_system(self):
        """Prueba 7: Probar sistema de email"""
        try:
            test_email_data = {
                "email": "test@empresa-demo.com"
            }
            
            response = requests.post(
                f"{self.base_url}/api/email/test",
                json=test_email_data,
                timeout=30
            )
            
            return response.status_code == 200
        except:
            return False
    
    def test_prometheus_integration(self):
        """Prueba 8: Verificar integración con Prometheus"""
        try:
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
            if response.status_code == 200:
                data = response.json()
                targets = data.get('data', {}).get('activeTargets', [])
                # Buscar target de Windows Exporter
                windows_targets = [t for t in targets if '9182' in t.get('scrapeUrl', '')]
                return len(windows_targets) > 0 and any(t.get('health') == 'up' for t in windows_targets)
            return False
        except:
            return False
    
    def test_metrics_endpoint(self):
        """Prueba 9: Verificar endpoint de métricas"""
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=10)
            if response.status_code == 200:
                metrics_text = response.text
                lines = metrics_text.split('\n')
                windows_metrics = [line for line in lines if 'windows_' in line and not line.startswith('#')]
                return len(windows_metrics) > 100  # Debe tener al menos 100 métricas Windows
            return False
        except:
            return False
    
    def test_docker_services(self):
        """Prueba 10: Verificar servicios Docker"""
        docker_services = [
            ("Prometheus", "http://localhost:9090/api/v1/status/config"),
            ("Grafana", "http://localhost:3000/api/health"),
            ("AlertManager", "http://localhost:9093/api/v1/status")
        ]
        
        working_services = 0
        for service_name, url in docker_services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    working_services += 1
            except:
                pass
        
        return working_services >= 2  # Al menos 2 de 3 servicios funcionando
    
    def test_smtp_service(self):
        """Prueba 11: Verificar servicio SMTP interno"""
        try:
            response = requests.get("http://localhost:5555/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_api_endpoints(self):
        """Prueba 12: Verificar endpoints principales del API"""
        endpoints = [
            "/api/cloud/credentials",
            "/api/email/recipients", 
            "/api/local/windows-exporter/status"
        ]
        
        working_endpoints = 0
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    working_endpoints += 1
            except:
                pass
        
        return working_endpoints == len(endpoints)
    
    def run_complete_test_suite(self):
        """Ejecutar suite completa de pruebas"""
        self.log("=" * 80)
        self.log("🧪 INICIANDO SUITE COMPLETA DE PRUEBAS OPTIMON v2.0")
        self.log("=" * 80)
        
        # Configurar servicios en segundo plano
        if not self.setup_services():
            self.log("Error configurando servicios, ejecutando pruebas limitadas", "WARNING")
        
        try:
            # Lista de pruebas a ejecutar
            tests = [
                ("Dashboard Disponible", self.test_dashboard_availability),
                ("API Credenciales AWS", self.test_cloud_credentials_api),
                ("API Credenciales Azure", self.test_azure_credentials_api),
                ("API Destinatarios Email", self.test_email_recipients_api),
                ("Estado Windows Exporter", self.test_windows_exporter_status),
                ("Instalación Windows Exporter", self.test_windows_exporter_installation),
                ("Sistema de Email", self.test_email_system),
                ("Integración Prometheus", self.test_prometheus_integration),
                ("Endpoint de Métricas", self.test_metrics_endpoint),
                ("Servicios Docker", self.test_docker_services),
                ("Servicio SMTP", self.test_smtp_service),
                ("Endpoints del API", self.test_api_endpoints)
            ]
            
            # Ejecutar todas las pruebas
            for test_name, test_func in tests:
                self.run_test(test_name, test_func)
                time.sleep(1)  # Pausa entre pruebas
            
            # Mostrar resumen
            self.show_test_summary()
            
            return self.passed_tests / self.total_tests if self.total_tests > 0 else 0
            
        finally:
            # Limpiar servicios
            self.cleanup_services()
    
    def show_test_summary(self):
        """Mostrar resumen de pruebas"""
        self.log("=" * 80)
        self.log("📊 RESUMEN DE PRUEBAS")
        self.log("=" * 80)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASS" else "❌"
            self.log(f"{status_icon} {test_name}: {result}")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        self.log("=" * 80)
        self.log(f"🏆 RESULTADO FINAL: {self.passed_tests}/{self.total_tests} pruebas exitosas ({success_rate:.1f}%)")
        
        if success_rate >= 95:
            self.log("🎉 EXCELENTE - Sistema funcionando perfectamente", "SUCCESS")
        elif success_rate >= 85:
            self.log("✅ BUENO - Sistema funcionando bien con problemas menores", "SUCCESS")
        elif success_rate >= 70:
            self.log("⚠️ ACEPTABLE - Sistema funcionando con algunos problemas", "WARNING")
        else:
            self.log("❌ NECESITA ATENCIÓN - Múltiples problemas detectados", "ERROR")
        
        self.log("=" * 80)
        
        # Instrucciones adicionales
        if success_rate < 100:
            self.log("💡 SUGERENCIAS PARA MEJORAR:")
            if "Dashboard Disponible" in self.test_results and self.test_results["Dashboard Disponible"] != "PASS":
                self.log("  • Verificar que el dashboard esté ejecutándose en puerto 5000")
            if "Servicios Docker" in self.test_results and self.test_results["Servicios Docker"] != "PASS":
                self.log("  • Iniciar servicios Docker: docker-compose up -d")
            if "Sistema de Email" in self.test_results and self.test_results["Sistema de Email"] != "PASS":
                self.log("  • Verificar configuración SMTP y credenciales de email")
            self.log("=" * 80)

def main():
    """Función principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🧪 OPTIMON v2.0 - PRUEBA COMPLETA INTEGRAL        ║
║                                                              ║
║  Esta prueba verifica:                                       ║
║  ✅ Dashboard web y APIs                                     ║
║  ✅ Configuración de credenciales de nube                   ║
║  ✅ Gestión de destinatarios de alertas                     ║
║  ✅ Instalación y estado de Windows Exporter               ║
║  ✅ Integración con Prometheus, Grafana, AlertManager      ║
║  ✅ Sistema de emails y SMTP                               ║
║  ✅ Funcionalidad completa end-to-end                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    tester = OptiMonCompleteTest()
    
    try:
        success_rate = tester.run_complete_test_suite()
        return 0 if success_rate >= 0.8 else 1  # 80% mínimo para considerar éxito
    except KeyboardInterrupt:
        tester.log("⏹️ Pruebas interrumpidas por el usuario", "WARNING")
        return 130
    except Exception as e:
        tester.log(f"❌ Error crítico durante las pruebas: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    exit(main())