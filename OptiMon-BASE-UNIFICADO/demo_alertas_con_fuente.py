#!/usr/bin/env python3
"""
🎯 DEMO - ALERTAS CON INFORMACIÓN DE FUENTE
Demostración de alertas que identifican exactamente qué recurso disparó la alerta
"""

import requests
import json
from datetime import datetime

def demo_alertas_con_fuente():
    """Demostración de alertas con información detallada de fuente"""
    print("🎯 DEMO: ALERTAS CON INFORMACIÓN DE FUENTE")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    
    # Verificar conexión
    try:
        response = requests.get(f"{base_url}")
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return
        print("✅ Servidor OptiMon activo")
    except:
        print("❌ No se puede conectar al servidor")
        return
    
    # Crear alertas con información detallada de fuente
    alertas_especificas = [
        {
            "name": "AWS_EC2_CPU_Critical",
            "description": "CPU crítico en instancia EC2 de producción",
            "metric": "cpu_usage_percent",
            "threshold": 85.0,
            "operator": ">",
            "severity": "critical",
            "enabled": True,
            "resource_type": "aws_ec2",
            "resource_name": "i-0123456789abcdef0",
            "region": "us-east-1",
            "environment": "production",
            "tags": ["aws", "ec2", "produccion", "critico"]
        },
        {
            "name": "Azure_VM_Memory_Warning",
            "description": "Memoria alta en VM de Azure (desarrollo)",
            "metric": "memory_usage_percent",
            "threshold": 75.0,
            "operator": ">=",
            "severity": "warning", 
            "enabled": True,
            "resource_type": "azure_vm",
            "resource_name": "dev-vm-webserver-01",
            "region": "West Europe",
            "environment": "development",
            "tags": ["azure", "vm", "desarrollo", "memoria"]
        },
        {
            "name": "Physical_Server_Disk_Alert",
            "description": "Disco lleno en servidor físico del datacenter",
            "metric": "disk_usage_percent",
            "threshold": 90.0,
            "operator": ">=",
            "severity": "critical",
            "enabled": True,
            "resource_type": "physical_server",
            "resource_name": "srv-db-prod-01.empresa.com",
            "region": "Datacenter-Principal",
            "environment": "production",
            "tags": ["fisico", "servidor", "disco", "database"]
        },
        {
            "name": "K8s_Pod_Response_Time",
            "description": "Tiempo de respuesta alto en pod de Kubernetes",
            "metric": "response_time_ms",
            "threshold": 200.0,
            "operator": ">",
            "severity": "warning",
            "enabled": True,
            "resource_type": "kubernetes",
            "resource_name": "web-app-pod-7c5f9d8b4-x9k2m",
            "region": "us-west-2",
            "environment": "staging",
            "tags": ["kubernetes", "pod", "performance", "web"]
        }
    ]
    
    print(f"\n🚨 CREANDO ALERTAS CON INFORMACIÓN DE FUENTE:")
    print("-" * 70)
    
    created_alerts = []
    for i, alerta in enumerate(alertas_especificas, 1):
        try:
            response = requests.post(
                f"{base_url}/api/custom-alerts",
                json=alerta,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    created_alerts.append(result['alert'])
                    print(f"   {i}. ✅ {alerta['name']}")
                    print(f"      🎯 Recurso: {alerta['resource_name']} ({alerta['resource_type']})")
                    print(f"      🌍 Región: {alerta['region']} | Ambiente: {alerta['environment']}")
                    print(f"      📊 {alerta['metric']} {alerta['operator']} {alerta['threshold']}")
                    print()
                else:
                    if "Ya existe una alerta" in result.get('error', ''):
                        print(f"   {i}. ⚠️  {alerta['name']} - Ya existe")
                    else:
                        print(f"   {i}. ❌ Error: {result.get('error', 'Error desconocido')}")
            else:
                print(f"   {i}. ❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   {i}. ❌ Error: {e}")
    
    # Listar alertas configuradas
    print(f"📋 ALERTAS CONFIGURADAS CON INFORMACIÓN DETALLADA:")
    print("-" * 70)
    
    try:
        response = requests.get(f"{base_url}/api/custom-alerts")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            
            if alerts:
                for alert in alerts:
                    status = "🟢" if alert.get('enabled') else "🔴"
                    severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️" if alert['severity'] == 'warning' else "ℹ️"
                    
                    print(f"   {severity_icon} {status} {alert['name']}")
                    
                    # Mostrar información de la fuente si está disponible
                    if alert.get('resource_name'):
                        resource_types = {
                            "aws_ec2": "☁️ AWS EC2",
                            "aws_rds": "🗄️ AWS RDS",
                            "azure_vm": "☁️ Azure VM",
                            "physical_server": "🖥️ Servidor Físico",
                            "kubernetes": "⚡ Kubernetes Pod",
                            "container": "📦 Container"
                        }
                        
                        resource_display = resource_types.get(alert.get('resource_type', ''), '🖥️')
                        print(f"      📍 Fuente: {resource_display} - {alert['resource_name']}")
                        
                        if alert.get('region'):
                            print(f"      🌍 Región: {alert['region']}")
                        if alert.get('environment'):
                            print(f"      🏷️  Ambiente: {alert['environment']}")
                    
                    print(f"      📊 Métrica: {alert['metric']} {alert['operator']} {alert['threshold']}")
                    print()
            else:
                print("   📝 No hay alertas configuradas")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar una alerta con información detallada
    if created_alerts:
        print(f"🧪 PROBANDO ALERTA CON INFORMACIÓN DETALLADA:")
        print("-" * 70)
        
        test_alert = None
        for alert in created_alerts:
            if alert.get('resource_name'):
                test_alert = alert
                break
        
        if test_alert:
            try:
                response = requests.post(
                    f"{base_url}/api/custom-alerts/{test_alert['id']}/test"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ Alerta enviada: {test_alert['name']}")
                        print(f"   📧 Destinatarios: {result.get('sent', 0)}")
                        print(f"   📍 Recurso: {test_alert.get('resource_name', 'N/A')}")
                        print(f"   🌍 Región: {test_alert.get('region', 'N/A')}")
                        print(f"   🏷️  Ambiente: {test_alert.get('environment', 'N/A')}")
                        print()
                        print("   📬 El email incluye información detallada sobre:")
                        print("      • Qué servidor/instancia disparó la alerta")
                        print("      • En qué región/zona se encuentra")
                        print("      • Qué ambiente está afectado (prod/dev/staging)")
                        print("      • El valor exacto de la métrica")
                    else:
                        print(f"   ❌ Error: {result.get('message', 'Error desconocido')}")
                else:
                    print(f"   ❌ Error HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Resumen final
    print(f"\n" + "=" * 70)
    print("🎉 SISTEMA DE ALERTAS CON INFORMACIÓN DETALLADA")
    print("✅ Cada alerta identifica exactamente QUÉ recurso está afectado")
    print("✅ Incluye información de ubicación (región/zona)")
    print("✅ Especifica el ambiente (producción/desarrollo/staging)")
    print("✅ Diferencia entre tipos de recursos (AWS/Azure/Físico/K8s)")
    print("✅ Los emails contienen información completa para troubleshooting")
    print()
    print("🌐 Gestión web: http://localhost:5000/custom-alerts")
    print("=" * 70)

if __name__ == "__main__":
    demo_alertas_con_fuente()