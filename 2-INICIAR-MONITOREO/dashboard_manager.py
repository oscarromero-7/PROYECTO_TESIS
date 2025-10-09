#!/usr/bin/env python3
"""
OptiMon Dashboard Manager
Gestiona la visibilidad de dashboards basado en configuración de credenciales
"""

import json
import requests
import os
from typing import Dict, List

class DashboardManager:
    def __init__(self):
        self.grafana_url = "http://localhost:3000"
        self.grafana_auth = ("admin", "admin")
        
    def check_credentials(self) -> Dict[str, bool]:
        """Verificar qué credenciales están configuradas"""
        credentials = {
            'aws': False,
            'azure': False,
            'gcp': False
        }
        
        # Verificar archivo principal de credenciales (mismo que usa optimon_dashboard.py)
        config_path = "config/cloud_credentials.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    
                # Verificar AWS
                aws_config = config_data.get('aws', {})
                if aws_config.get('access_key') and aws_config.get('secret_key'):
                    credentials['aws'] = True
                    
                # Verificar Azure
                azure_config = config_data.get('azure', {})
                if (azure_config.get('client_id') and 
                    azure_config.get('client_secret') and 
                    azure_config.get('tenant_id')):
                    credentials['azure'] = True
                    
            except Exception as e:
                print(f"Error leyendo credenciales: {e}")
                
        return credentials
    
    def get_dashboard_templates(self) -> Dict[str, Dict]:
        """Plantillas de dashboards para cada proveedor"""
        return {
            'aws': {
                'uid': 'aws-infrastructure',
                'title': 'AWS Infrastructure Overview',
                'tags': ['aws', 'cloud', 'infrastructure'],
                'folder': 'Cloud Monitoring',
                'template': 'aws_dashboard_template.json'
            },
            'azure': {
                'uid': 'azure-infrastructure', 
                'title': 'Azure Infrastructure Overview',
                'tags': ['azure', 'cloud', 'infrastructure'],
                'folder': 'Cloud Monitoring',
                'template': 'azure_dashboard_template.json'
            },
            'gcp': {
                'uid': 'gcp-infrastructure',
                'title': 'GCP Infrastructure Overview', 
                'tags': ['gcp', 'cloud', 'infrastructure'],
                'folder': 'Cloud Monitoring',
                'template': 'gcp_dashboard_template.json'
            }
        }
    
    def create_aws_dashboard(self) -> Dict:
        """Crear dashboard de AWS con paneles útiles"""
        dashboard = {
            "dashboard": {
                "uid": "aws-infrastructure",
                "title": "AWS Infrastructure Overview",
                "tags": ["aws", "cloud", "ec2"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "EC2 Instance CPU Usage",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\",provider=\"aws\"}[5m])) * 100)",
                                "legendFormat": "{{instance}} CPU %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "EC2 Memory Usage",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "(1 - (node_memory_MemAvailable_bytes{provider=\"aws\"} / node_memory_MemTotal_bytes{provider=\"aws\"})) * 100",
                                "legendFormat": "{{instance}} Memory %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "EC2 Disk Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "(1 - (node_filesystem_avail_bytes{provider=\"aws\",fstype!=\"tmpfs\"} / node_filesystem_size_bytes{provider=\"aws\",fstype!=\"tmpfs\"})) * 100",
                                "legendFormat": "{{instance}} {{mountpoint}}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            },
            "folderId": 0,
            "overwrite": True
        }
        return dashboard
    
    def create_azure_dashboard(self) -> Dict:
        """Crear dashboard de Azure"""
        dashboard = {
            "dashboard": {
                "uid": "azure-infrastructure",
                "title": "Azure Infrastructure Overview", 
                "tags": ["azure", "cloud", "vm"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Azure VM CPU Usage",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\",provider=\"azure\"}[5m])) * 100)",
                                "legendFormat": "{{instance}} CPU %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Azure VM Memory Usage",
                        "type": "stat", 
                        "targets": [
                            {
                                "expr": "(1 - (node_memory_MemAvailable_bytes{provider=\"azure\"} / node_memory_MemTotal_bytes{provider=\"azure\"})) * 100",
                                "legendFormat": "{{instance}} Memory %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            },
            "folderId": 0,
            "overwrite": True
        }
        return dashboard
    
    def dashboard_exists(self, uid: str) -> bool:
        """Verificar si un dashboard existe"""
        try:
            response = requests.get(
                f"{self.grafana_url}/api/dashboards/uid/{uid}",
                auth=self.grafana_auth
            )
            return response.status_code == 200
        except:
            return False
    
    def create_dashboard(self, dashboard_data: Dict) -> bool:
        """Crear dashboard en Grafana"""
        try:
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=dashboard_data,
                auth=self.grafana_auth,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error creando dashboard: {e}")
            return False
    
    def delete_dashboard(self, uid: str) -> bool:
        """Eliminar dashboard"""
        try:
            response = requests.delete(
                f"{self.grafana_url}/api/dashboards/uid/{uid}",
                auth=self.grafana_auth
            )
            return response.status_code == 200
        except:
            return False
    
    def sync_dashboards(self):
        """Sincronizar dashboards basado en credenciales configuradas"""
        credentials = self.check_credentials()
        
        print(f"🔍 Verificando credenciales: {credentials}")
        
        # AWS Dashboard
        if credentials['aws']:
            if not self.dashboard_exists('aws-infrastructure'):
                print("📊 Creando dashboard de AWS...")
                aws_dashboard = self.create_aws_dashboard()
                if self.create_dashboard(aws_dashboard):
                    print("✅ Dashboard de AWS creado")
                else:
                    print("❌ Error creando dashboard de AWS")
        else:
            if self.dashboard_exists('aws-infrastructure'):
                print("🗑️ Eliminando dashboard de AWS (sin credenciales)")
                self.delete_dashboard('aws-infrastructure')
        
        # Azure Dashboard  
        if credentials['azure']:
            if not self.dashboard_exists('azure-infrastructure'):
                print("📊 Creando dashboard de Azure...")
                azure_dashboard = self.create_azure_dashboard()
                if self.create_dashboard(azure_dashboard):
                    print("✅ Dashboard de Azure creado")
                else:
                    print("❌ Error creando dashboard de Azure")
        else:
            if self.dashboard_exists('azure-infrastructure'):
                print("🗑️ Eliminando dashboard de Azure (sin credenciales)")
                self.delete_dashboard('azure-infrastructure')

def main():
    """Función principal"""
    manager = DashboardManager()
    manager.sync_dashboards()

if __name__ == "__main__":
    main()