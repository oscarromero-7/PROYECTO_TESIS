#!/usr/bin/env python3
"""
Sistema Automatizado de Verificación y Corrección de Dashboards - OptiMon
Este sistema verifica automáticamente que los dashboards funcionen correctamente
y los corrige si hay problemas.
"""

import requests
import json
import time
import os
import glob
from datetime import datetime
import logging

class DashboardAutoFixer:
    def __init__(self):
        self.grafana_url = "http://localhost:3000"
        self.grafana_auth = ('admin', 'admin')
        self.prometheus_url = "http://localhost:9090"
        self.dashboard_dir = "2-INICIAR-MONITOREO/config/grafana/dashboards"
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('dashboard_auto_fix.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_services_health(self):
        """Verificar que todos los servicios estén funcionando"""
        self.logger.info("Verificando salud de servicios...")
        
        services = {
            "Grafana": self.grafana_url,
            "Prometheus": self.prometheus_url
        }
        
        healthy_services = 0
        for service, url in services.items():
            try:
                response = requests.get(f"{url}/api/health" if service == "Grafana" else f"{url}/api/v1/status/config", 
                                      timeout=5)
                if response.status_code == 200:
                    self.logger.info(f"✅ {service}: OK")
                    healthy_services += 1
                else:
                    self.logger.warning(f"⚠️ {service}: HTTP {response.status_code}")
            except Exception as e:
                self.logger.error(f"❌ {service}: {e}")
        
        return healthy_services == len(services)
    
    def get_correct_datasource_uid(self):
        """Obtener el UID correcto del datasource de Prometheus"""
        try:
            response = requests.get(f"{self.grafana_url}/api/datasources", 
                                  auth=self.grafana_auth, timeout=10)
            if response.status_code == 200:
                for ds in response.json():
                    if ds['type'] == 'prometheus':
                        self.logger.info(f"Datasource Prometheus encontrado: {ds['uid']}")
                        return ds['uid']
            self.logger.error("No se encontró datasource de Prometheus")
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo datasource: {e}")
            return None
    
    def test_prometheus_queries(self):
        """Probar queries básicas de Prometheus"""
        self.logger.info("Probando queries básicas de Prometheus...")
        
        test_queries = {
            "instance_up": "up{instance=\"local-computer\"}",
            "load_average": "node_load1{instance=\"local-computer\"}",
            "memory_total": "node_memory_MemTotal_bytes{instance=\"local-computer\"}",
            "boot_time": "node_boot_time_seconds{instance=\"local-computer\"}"
        }
        
        working_queries = 0
        query_results = {}
        
        for name, query in test_queries.items():
            try:
                response = requests.get(f"{self.prometheus_url}/api/v1/query", 
                                      params={'query': query}, timeout=5)
                if response.status_code == 200:
                    data = response.json()['data']['result']
                    if data:
                        value = data[0]['value'][1]
                        self.logger.info(f"✅ {name}: {value}")
                        query_results[name] = True
                        working_queries += 1
                    else:
                        self.logger.warning(f"⚠️ {name}: Sin datos")
                        query_results[name] = False
                else:
                    self.logger.error(f"❌ {name}: HTTP {response.status_code}")
                    query_results[name] = False
            except Exception as e:
                self.logger.error(f"❌ {name}: {e}")
                query_results[name] = False
        
        return working_queries == len(test_queries), query_results
    
    def scan_dashboard_files(self):
        """Escanear archivos de dashboard en el directorio"""
        dashboard_files = []
        if os.path.exists(self.dashboard_dir):
            for file_path in glob.glob(os.path.join(self.dashboard_dir, "*.json")):
                dashboard_files.append(file_path)
        
        self.logger.info(f"Encontrados {len(dashboard_files)} archivos de dashboard")
        return dashboard_files
    
    def fix_dashboard_datasource_uid(self, dashboard_file, correct_uid):
        """Corregir UID del datasource en un archivo de dashboard"""
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar y reemplazar UIDs incorrectos
            wrong_uids = ['"uid": "prometheus"', '"uid": ""', '"uid": null']
            fixed_count = 0
            
            for wrong_uid in wrong_uids:
                if wrong_uid in content:
                    content = content.replace(wrong_uid, f'"uid": "{correct_uid}"')
                    fixed_count += content.count(f'"uid": "{correct_uid}"') - content.count(wrong_uid)
            
            if fixed_count > 0:
                # Guardar archivo corregido
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.info(f"✅ Corregido {dashboard_file}: {fixed_count} referencias de UID")
                return True
            else:
                self.logger.info(f"ℹ️ {dashboard_file}: No necesita corrección")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error corrigiendo {dashboard_file}: {e}")
            return False
    
    def validate_dashboard_json(self, dashboard_file):
        """Validar que el archivo JSON del dashboard sea válido"""
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON inválido en {dashboard_file}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error leyendo {dashboard_file}: {e}")
            return False
    
    def import_dashboard_to_grafana(self, dashboard_file):
        """Importar dashboard a Grafana"""
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_json = json.load(f)
            
            payload = {
                "dashboard": dashboard_json,
                "overwrite": True,
                "message": f"Auto-imported by OptiMon Auto-Fixer at {datetime.now()}"
            }
            
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=payload,
                headers={'Content-Type': 'application/json'},
                auth=self.grafana_auth,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                dashboard_uid = result.get('uid', 'unknown')
                dashboard_url = f"{self.grafana_url}/d/{dashboard_uid}"
                
                self.logger.info(f"✅ Dashboard importado: {dashboard_file}")
                self.logger.info(f"🔗 URL: {dashboard_url}")
                return True, dashboard_url
            else:
                self.logger.error(f"❌ Error importando {dashboard_file}: {response.status_code}")
                self.logger.error(f"Respuesta: {response.text}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"❌ Error importando {dashboard_file}: {e}")
            return False, None
    
    def test_dashboard_queries_via_grafana(self, datasource_uid):
        """Probar queries a través de la API de Grafana"""
        test_query = "up{instance=\"local-computer\"}"
        
        try:
            response = requests.get(
                f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_uid}/api/v1/query",
                params={'query': test_query},
                auth=self.grafana_auth,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('result'):
                    self.logger.info("✅ Queries via Grafana funcionan correctamente")
                    return True
                else:
                    self.logger.warning("⚠️ Queries via Grafana sin resultados")
                    return False
            else:
                self.logger.error(f"❌ Error query via Grafana: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error probando query via Grafana: {e}")
            return False
    
    def create_backup_dashboard(self):
        """Crear dashboard de respaldo simple que siempre funciona"""
        correct_uid = self.get_correct_datasource_uid()
        if not correct_uid:
            return False, None
        
        backup_dashboard = {
            "dashboard": {
                "id": None,
                "title": "Windows Local - Auto Backup Dashboard",
                "uid": "windows-local-backup",
                "tags": ["windows", "local", "backup", "auto-generated"],
                "timezone": "",
                "panels": [
                    {
                        "datasource": {"type": "prometheus", "uid": correct_uid},
                        "id": 1,
                        "title": "System Status",
                        "type": "stat",
                        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
                        "targets": [
                            {
                                "datasource": {"type": "prometheus", "uid": correct_uid},
                                "expr": "up{instance=\"local-computer\"}",
                                "refId": "A"
                            }
                        ],
                        "options": {
                            "reduceOptions": {"calcs": ["lastNotNull"]},
                            "colorMode": "background"
                        }
                    },
                    {
                        "datasource": {"type": "prometheus", "uid": correct_uid},
                        "id": 2,
                        "title": "Load Average",
                        "type": "stat",
                        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 0},
                        "targets": [
                            {
                                "datasource": {"type": "prometheus", "uid": correct_uid},
                                "expr": "node_load1{instance=\"local-computer\"}",
                                "refId": "A"
                            }
                        ],
                        "options": {
                            "reduceOptions": {"calcs": ["lastNotNull"]},
                            "colorMode": "value"
                        }
                    },
                    {
                        "datasource": {"type": "prometheus", "uid": correct_uid},
                        "id": 3,
                        "title": "Memory Total",
                        "type": "stat",
                        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 0},
                        "targets": [
                            {
                                "datasource": {"type": "prometheus", "uid": correct_uid},
                                "expr": "node_memory_MemTotal_bytes{instance=\"local-computer\"}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "bytes"
                            }
                        },
                        "options": {
                            "reduceOptions": {"calcs": ["lastNotNull"]},
                            "colorMode": "value"
                        }
                    }
                ],
                "time": {"from": "now-15m", "to": "now"},
                "refresh": "30s"
            },
            "overwrite": True,
            "message": "Auto-generated backup dashboard"
        }
        
        try:
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=backup_dashboard,
                headers={'Content-Type': 'application/json'},
                auth=self.grafana_auth,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                dashboard_url = f"{self.grafana_url}/d/{result.get('uid', 'windows-local-backup')}"
                self.logger.info(f"✅ Dashboard de respaldo creado: {dashboard_url}")
                return True, dashboard_url
            else:
                self.logger.error(f"❌ Error creando dashboard de respaldo: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"❌ Error creando dashboard de respaldo: {e}")
            return False, None
    
    def run_full_verification_and_fix(self):
        """Ejecutar verificación completa y corrección automática"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 INICIANDO VERIFICACIÓN Y CORRECCIÓN AUTOMÁTICA DE DASHBOARDS")
        self.logger.info("=" * 80)
        
        # Paso 1: Verificar servicios
        if not self.check_services_health():
            self.logger.error("❌ Servicios no están funcionando correctamente. Abortando.")
            return False
        
        # Paso 2: Verificar queries de Prometheus
        queries_ok, query_results = self.test_prometheus_queries()
        if not queries_ok:
            self.logger.warning("⚠️ Algunas queries de Prometheus fallan")
        
        # Paso 3: Obtener UID correcto del datasource
        correct_uid = self.get_correct_datasource_uid()
        if not correct_uid:
            self.logger.error("❌ No se pudo obtener UID del datasource. Abortando.")
            return False
        
        # Paso 4: Escanear y corregir archivos de dashboard
        dashboard_files = self.scan_dashboard_files()
        fixed_files = 0
        imported_files = 0
        
        for dashboard_file in dashboard_files:
            self.logger.info(f"📁 Procesando: {dashboard_file}")
            
            # Validar JSON
            if not self.validate_dashboard_json(dashboard_file):
                continue
            
            # Corregir UID si es necesario
            if self.fix_dashboard_datasource_uid(dashboard_file, correct_uid):
                fixed_files += 1
            
            # Importar a Grafana
            success, url = self.import_dashboard_to_grafana(dashboard_file)
            if success:
                imported_files += 1
        
        # Paso 5: Probar queries via Grafana
        grafana_queries_ok = self.test_dashboard_queries_via_grafana(correct_uid)
        
        # Paso 6: Crear dashboard de respaldo si es necesario
        if not grafana_queries_ok or imported_files == 0:
            self.logger.warning("⚠️ Creando dashboard de respaldo...")
            backup_success, backup_url = self.create_backup_dashboard()
            if backup_success:
                self.logger.info(f"✅ Dashboard de respaldo disponible: {backup_url}")
        
        # Resumen final
        self.logger.info("=" * 80)
        self.logger.info("📊 RESUMEN DE VERIFICACIÓN Y CORRECCIÓN")
        self.logger.info("=" * 80)
        self.logger.info(f"📁 Archivos encontrados: {len(dashboard_files)}")
        self.logger.info(f"🔧 Archivos corregidos: {fixed_files}")
        self.logger.info(f"📤 Archivos importados: {imported_files}")
        self.logger.info(f"🔍 Queries Prometheus: {'✅ OK' if queries_ok else '❌ ERROR'}")
        self.logger.info(f"🎯 Queries Grafana: {'✅ OK' if grafana_queries_ok else '❌ ERROR'}")
        
        success = (imported_files > 0 or grafana_queries_ok)
        
        if success:
            self.logger.info("🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE")
            self.logger.info(f"🔗 Acceso: {self.grafana_url}")
            self.logger.info("🔑 Credenciales: admin/admin")
        else:
            self.logger.error("❌ VERIFICACIÓN FALLÓ - Revisa los logs para detalles")
        
        return success

def create_auto_runner_script():
    """Crear script para ejecutar automáticamente el verificador"""
    script_content = '''#!/usr/bin/env python3
"""
Auto-runner para verificación automática de dashboards
Ejecuta verificación cada 5 minutos
"""

import time
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_auto_verifier import DashboardAutoFixer

def run_continuous_monitoring():
    """Ejecutar monitoreo continuo"""
    auto_fixer = DashboardAutoFixer()
    
    print("🔄 Iniciando monitoreo continuo de dashboards...")
    print("⏰ Verificación cada 5 minutos")
    print("🛑 Presiona Ctrl+C para detener")
    
    try:
        while True:
            print(f"\\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Ejecutando verificación...")
            auto_fixer.run_full_verification_and_fix()
            
            print("😴 Esperando 5 minutos hasta la siguiente verificación...")
            time.sleep(300)  # 5 minutos
            
    except KeyboardInterrupt:
        print("\\n🛑 Monitoreo detenido por el usuario")
    except Exception as e:
        print(f"\\n❌ Error en monitoreo continuo: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous_monitoring()
    else:
        auto_fixer = DashboardAutoFixer()
        auto_fixer.run_full_verification_and_fix()
'''
    
    with open('dashboard_auto_runner.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script auto-runner creado: dashboard_auto_runner.py")

if __name__ == "__main__":
    auto_fixer = DashboardAutoFixer()
    success = auto_fixer.run_full_verification_and_fix()
    
    if success:
        print("\n🔧 Creando script de ejecución automática...")
        create_auto_runner_script()
        
        print("\n📋 INSTRUCCIONES DE USO:")
        print("1. Verificación única: python dashboard_auto_verifier.py")
        print("2. Monitoreo continuo: python dashboard_auto_runner.py --continuous")
        print("3. Logs en: dashboard_auto_fix.log")
    else:
        print("\n❌ Verificación falló. Revisa los logs para más detalles.")