#!/usr/bin/env python3
"""
OptiMon Dashboard Configurator
Configura automáticamente dashboards personalizados en Grafana
"""

import requests
import json
import time
from pathlib import Path

class GrafanaDashboardManager:
    def __init__(self, grafana_url="http://localhost:3000", username="admin", password="admin"):
        self.grafana_url = grafana_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        
    def wait_for_grafana(self, max_attempts=30):
        """Espera a que Grafana esté disponible"""
        print("🔄 Esperando a que Grafana esté disponible...")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.grafana_url}/api/health")
                if response.status_code == 200:
                    print("✅ Grafana está disponible")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            
            if attempt < max_attempts - 1:
                print(f"   Intento {attempt + 1}/{max_attempts}, esperando...")
                time.sleep(2)
        
        print("❌ Grafana no está disponible")
        return False
    
    def create_prometheus_datasource(self):
        """Crea el datasource de Prometheus si no existe"""
        print("🔗 Configurando datasource de Prometheus...")
        
        # Verificar si ya existe
        response = self.session.get(f"{self.grafana_url}/api/datasources/name/Prometheus")
        if response.status_code == 200:
            print("   ✅ Datasource Prometheus ya existe")
            return True
        
        # Crear datasource
        datasource_config = {
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://prometheus:9090",
            "access": "proxy",
            "isDefault": True,
            "basicAuth": False
        }
        
        response = self.session.post(
            f"{self.grafana_url}/api/datasources",
            json=datasource_config
        )
        
        if response.status_code in [200, 201]:
            print("   ✅ Datasource Prometheus creado")
            return True
        else:
            print(f"   ❌ Error creando datasource: {response.text}")
            return False
    
    def import_dashboard(self, dashboard_path):
        """Importa un dashboard desde archivo JSON"""
        dashboard_name = dashboard_path.stem
        print(f"📊 Importando dashboard: {dashboard_name}")
        
        try:
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_json = json.load(f)
            
            # Preparar payload para importación
            import_payload = {
                "dashboard": dashboard_json,
                "overwrite": True,
                "inputs": [],
                "folderId": 0
            }
            
            response = self.session.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=import_payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                dashboard_url = f"{self.grafana_url}{result.get('url', '')}"
                print(f"   ✅ Dashboard importado: {dashboard_url}")
                return True
            else:
                print(f"   ❌ Error importando dashboard: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error procesando archivo: {e}")
            return False
    
    def configure_all_dashboards(self):
        """Configura todos los dashboards de OptiMon"""
        print("🎨 Configurando dashboards de OptiMon...")
        print("=" * 50)
        
        # Esperar a que Grafana esté disponible
        if not self.wait_for_grafana():
            return False
        
        # Configurar datasource
        if not self.create_prometheus_datasource():
            return False
        
        # Buscar archivos de dashboard
        dashboard_dir = Path("config/grafana/dashboards")
        if not dashboard_dir.exists():
            print(f"❌ Directorio de dashboards no encontrado: {dashboard_dir}")
            return False
        
        # Importar cada dashboard
        dashboard_files = list(dashboard_dir.glob("*.json"))
        successful_imports = 0
        
        for dashboard_file in dashboard_files:
            if self.import_dashboard(dashboard_file):
                successful_imports += 1
        
        print("\n" + "=" * 50)
        print(f"✅ Configuración completada!")
        print(f"   📊 Dashboards importados: {successful_imports}/{len(dashboard_files)}")
        print(f"   🌐 Grafana: {self.grafana_url}")
        print(f"   👤 Usuario: {self.username}")
        print(f"   🔑 Contraseña: {self.password}")
        
        if successful_imports > 0:
            print(f"\n🎯 Dashboards disponibles:")
            print(f"   • Infrastructure Overview: {self.grafana_url}/d/optimon-infrastructure")
            print(f"   • Azure VMs Monitoring: {self.grafana_url}/d/optimon-azure-vms")
        
        return successful_imports > 0

def main():
    """Función principal"""
    manager = GrafanaDashboardManager()
    success = manager.configure_all_dashboards()
    
    if success:
        print(f"\n🎉 ¡Dashboards configurados exitosamente!")
        print(f"   Accede a Grafana en: http://localhost:3000")
        print(f"   Usuario: admin, Contraseña: admin")
    else:
        print(f"\n❌ Error configurando dashboards")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())