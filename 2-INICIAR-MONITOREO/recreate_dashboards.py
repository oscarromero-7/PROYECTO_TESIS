#!/usr/bin/env python3
"""
Script para recrear dashboards de nube cuando se configuren credenciales
"""

import requests
import json
import os

def create_aws_dashboard():
    """Crear dashboard básico de AWS EC2"""
    dashboard_config = {
        "dashboard": {
            "title": "OptiMon - AWS EC2 Instances",
            "tags": ["aws", "ec2", "optimon", "monitoring"],
            "timezone": "browser",
            "refresh": "30s",
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "title": "AWS EC2 Instance Count",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "aws_ec2_instances_total",
                            "refId": "A"
                        }
                    ],
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 0,
                        "y": 0
                    }
                }
            ]
        },
        "message": "Created by OptiMon automation",
        "overwrite": True
    }
    return dashboard_config

def create_azure_dashboard():
    """Crear dashboard básico de Azure VMs"""
    dashboard_config = {
        "dashboard": {
            "title": "OptiMon - Azure VMs Monitoring", 
            "tags": ["azure", "vm", "optimon", "monitoring"],
            "timezone": "browser",
            "refresh": "30s",
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "title": "Azure VM Count",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "azure_vm_instances_total",
                            "refId": "A"
                        }
                    ],
                    "gridPos": {
                        "h": 8,
                        "w": 12,
                        "x": 0,
                        "y": 0
                    }
                }
            ]
        },
        "message": "Created by OptiMon automation",
        "overwrite": True
    }
    return dashboard_config

def recreate_cloud_dashboards(aws_enabled=False, azure_enabled=False):
    """Recrear dashboards según credenciales configuradas"""
    grafana_url = "http://localhost:3000"
    auth = ('admin', 'admin')
    
    created_count = 0
    
    try:
        if aws_enabled:
            print("🔄 Creando dashboard de AWS...")
            aws_dashboard = create_aws_dashboard()
            response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                   json=aws_dashboard, auth=auth)
            if response.status_code == 200:
                print("✅ Dashboard de AWS creado exitosamente")
                created_count += 1
            else:
                print(f"❌ Error creando dashboard AWS: {response.status_code}")
        
        if azure_enabled:
            print("🔄 Creando dashboard de Azure...")
            azure_dashboard = create_azure_dashboard()
            response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                   json=azure_dashboard, auth=auth)
            if response.status_code == 200:
                print("✅ Dashboard de Azure creado exitosamente")
                created_count += 1
            else:
                print(f"❌ Error creando dashboard Azure: {response.status_code}")
        
        print(f"\n🎯 Total de dashboards creados: {created_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    import sys
    
    aws_enabled = 'aws' in sys.argv
    azure_enabled = 'azure' in sys.argv
    
    if not aws_enabled and not azure_enabled:
        print("Uso: python recreate_dashboards.py [aws] [azure]")
        print("Ejemplo: python recreate_dashboards.py aws azure")
    else:
        recreate_cloud_dashboards(aws_enabled, azure_enabled)