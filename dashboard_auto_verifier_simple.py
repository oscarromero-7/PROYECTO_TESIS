#!/usr/bin/env python3
"""
Dashboard Auto Verifier Simple - Version compatible con Windows
Sistema automatizado de verificacion y correccion de dashboards para OptiMon
Sin emojis para evitar problemas de encoding en Windows
"""

import os
import json
import requests
import time
from datetime import datetime

class DashboardAutoFixerSimple:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.grafana_url = "http://localhost:3000"
        self.prometheus_url = "http://localhost:9090"
        self.grafana_user = "admin"
        self.grafana_password = "admin"
        
        # Directorios de dashboards
        self.dashboard_dirs = [
            os.path.join(self.base_dir, "grafana", "dashboards"),
            os.path.join(self.base_dir, "grafana", "provisioning", "dashboards"),
            self.base_dir  # Directorio raiz tambien
        ]
        
        self.log_file = os.path.join(self.base_dir, "dashboard_verification.log")
        
    def log(self, message):
        """Escribir mensaje al log y consola"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except:
            pass
    
    def check_services_health(self):
        """Verificar que Grafana y Prometheus estén funcionando"""
        services_ok = True
        
        # Verificar Prometheus
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=10)
            if response.status_code == 200:
                self.log("Prometheus: OK")
            else:
                self.log(f"Prometheus: ERROR - Status {response.status_code}")
                services_ok = False
        except Exception as e:
            self.log(f"Prometheus: ERROR - {e}")
            services_ok = False
        
        # Verificar Grafana
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=10)
            if response.status_code == 200:
                self.log("Grafana: OK")
            else:
                self.log(f"Grafana: ERROR - Status {response.status_code}")
                services_ok = False
        except Exception as e:
            self.log(f"Grafana: ERROR - {e}")
            services_ok = False
        
        return services_ok
    
    def get_correct_datasource_uid(self):
        """Obtener el UID correcto del datasource de Prometheus en Grafana"""
        try:
            auth = (self.grafana_user, self.grafana_password)
            response = requests.get(f"{self.grafana_url}/api/datasources", auth=auth, timeout=10)
            
            if response.status_code == 200:
                datasources = response.json()
                for ds in datasources:
                    if ds.get('type') == 'prometheus':
                        uid = ds.get('uid')
                        self.log(f"Datasource UID encontrado: {uid}")
                        return uid
                
                self.log("No se encontro datasource de Prometheus")
                return None
            else:
                self.log(f"Error obteniendo datasources: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"Error obteniendo datasource UID: {e}")
            return None
    
    def find_dashboard_files(self):
        """Buscar todos los archivos .json de dashboards"""
        dashboard_files = []
        
        for directory in self.dashboard_dirs:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.json') and 'dashboard' in file.lower():
                            dashboard_files.append(os.path.join(root, file))
        
        # Buscar en directorio actual archivos que parezcan dashboards
        current_dir_files = [
            "windows_local_dashboard.json",
            "windows_local_fixed.json", 
            "aws-ec2.json",
            "azure-vm.json",
            "linux-physical.json",
            "aws-linux.json"
        ]
        
        for file in current_dir_files:
            full_path = os.path.join(self.base_dir, file)
            if os.path.exists(full_path):
                dashboard_files.append(full_path)
        
        return list(set(dashboard_files))  # Eliminar duplicados
    
    def is_valid_json(self, file_path):
        """Verificar si un archivo JSON es valido"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except:
            return False
    
    def fix_dashboard_datasource_uid(self, dashboard_file, correct_uid):
        """Corregir el UID del datasource en un dashboard"""
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            
            changes_made = False
            
            # Buscar y corregir UIDs en el dashboard
            if 'panels' in dashboard_data:
                for panel in dashboard_data['panels']:
                    if 'datasource' in panel:
                        if isinstance(panel['datasource'], dict):
                            if panel['datasource'].get('uid') != correct_uid:
                                panel['datasource']['uid'] = correct_uid
                                changes_made = True
                        elif isinstance(panel['datasource'], str):
                            panel['datasource'] = {"type": "prometheus", "uid": correct_uid}
                            changes_made = True
                    
                    # Verificar targets tambien
                    if 'targets' in panel:
                        for target in panel['targets']:
                            if 'datasource' in target:
                                if isinstance(target['datasource'], dict):
                                    if target['datasource'].get('uid') != correct_uid:
                                        target['datasource']['uid'] = correct_uid
                                        changes_made = True
            
            if changes_made:
                # Guardar archivo corregido
                backup_file = dashboard_file + '.backup'
                os.rename(dashboard_file, backup_file)
                
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
                
                self.log(f"Dashboard corregido: {os.path.basename(dashboard_file)}")
                return True
            else:
                self.log(f"Dashboard ya correcto: {os.path.basename(dashboard_file)}")
                return False
                
        except Exception as e:
            self.log(f"Error corrigiendo {os.path.basename(dashboard_file)}: {e}")
            return False
    
    def import_dashboard_to_grafana(self, dashboard_file):
        """Importar un dashboard a Grafana"""
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            
            # Preparar datos para importacion
            import_data = {
                "dashboard": dashboard_data,
                "overwrite": True,
                "inputs": []
            }
            
            auth = (self.grafana_user, self.grafana_password)
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                auth=auth,
                headers=headers,
                json=import_data,
                timeout=30
            )
            
            if response.status_code in [200, 412]:  # 412 = ya existe, pero se actualiza
                self.log(f"Dashboard importado: {os.path.basename(dashboard_file)}")
                return True
            else:
                self.log(f"Error importando {os.path.basename(dashboard_file)}: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Error importando {os.path.basename(dashboard_file)}: {e}")
            return False
    
    def test_prometheus_queries(self):
        """Probar algunas consultas basicas de Prometheus"""
        test_queries = [
            "up",
            "node_cpu_seconds_total",
            "node_memory_MemTotal_bytes",
            "windows_cpu_time_total"
        ]
        
        working_queries = 0
        
        for query in test_queries:
            try:
                params = {'query': query}
                response = requests.get(f"{self.prometheus_url}/api/v1/query", params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        working_queries += 1
                        
            except Exception as e:
                pass  # Continuar con la siguiente consulta
        
        self.log(f"Consultas de Prometheus funcionando: {working_queries}/{len(test_queries)}")
        return working_queries > 0
    
    def run_full_verification(self):
        """Ejecutar verificacion completa del sistema"""
        self.log("INICIANDO VERIFICACION AUTOMATICA DE DASHBOARDS")
        self.log("=" * 60)
        
        # 1. Verificar servicios
        if not self.check_services_health():
            self.log("ERROR: Servicios no disponibles")
            return False
        
        # 2. Obtener UID correcto del datasource
        correct_uid = self.get_correct_datasource_uid()
        if not correct_uid:
            self.log("ERROR: No se pudo obtener UID del datasource")
            return False
        
        # 3. Buscar dashboards
        dashboard_files = self.find_dashboard_files()
        self.log(f"Dashboards encontrados: {len(dashboard_files)}")
        
        # 4. Procesar cada dashboard
        corrected_count = 0
        imported_count = 0
        
        for dashboard_file in dashboard_files:
            dashboard_name = os.path.basename(dashboard_file)
            
            # Verificar si es JSON valido
            if not self.is_valid_json(dashboard_file):
                self.log(f"SALTANDO - JSON invalido: {dashboard_name}")
                continue
            
            # Corregir UID si es necesario
            if self.fix_dashboard_datasource_uid(dashboard_file, correct_uid):
                corrected_count += 1
            
            # Importar a Grafana
            if self.import_dashboard_to_grafana(dashboard_file):
                imported_count += 1
        
        # 5. Probar consultas de Prometheus
        queries_ok = self.test_prometheus_queries()
        
        # Resumen final
        self.log("=" * 60)
        self.log("RESUMEN DE VERIFICACION:")
        self.log(f"Dashboards encontrados: {len(dashboard_files)}")
        self.log(f"Dashboards corregidos: {corrected_count}")
        self.log(f"Dashboards importados: {imported_count}")
        self.log(f"Consultas Prometheus: {'OK' if queries_ok else 'ERROR'}")
        
        if imported_count > 0 and queries_ok:
            self.log("AUTOMATIZACION COMPLETADA EXITOSAMENTE")
            return True
        else:
            self.log("AUTOMATIZACION COMPLETADA CON ADVERTENCIAS")
            return False

def main():
    """Funcion principal"""
    fixer = DashboardAutoFixerSimple()
    return fixer.run_full_verification()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)