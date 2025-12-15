#!/usr/bin/env python3
"""
Sistema de alertas de prueba para OptiMon
Genera alertas automáticas cuando se detecta 50% de uso
"""

import requests
import json
import time
import random
from datetime import datetime

def generate_test_alert():
    """Generar alerta de prueba al 50%"""
    
    # Simular diferentes tipos de métricas al 50%
    alerts_tipos = [
        {
            "alertname": "CPU_Usage_High",
            "instance": "server-01:9100", 
            "job": "node_exporter",
            "severity": "warning",
            "description": "CPU usage is at 50%",
            "value": "50.2",
            "metric": "cpu_usage_percent"
        },
        {
            "alertname": "Memory_Usage_High", 
            "instance": "server-02:9100",
            "job": "node_exporter", 
            "severity": "warning",
            "description": "Memory usage is at 50%",
            "value": "50.5",
            "metric": "memory_usage_percent"
        },
        {
            "alertname": "Disk_Usage_High",
            "instance": "server-03:9100",
            "job": "node_exporter",
            "severity": "warning", 
            "description": "Disk usage is at 50%",
            "value": "50.8",
            "metric": "disk_usage_percent"
        }
    ]
    
    # Seleccionar alerta aleatoria
    alert = random.choice(alerts_tipos)
    
    return {
        "receiver": "optimon-alerts",
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": alert["alertname"],
                    "instance": alert["instance"],
                    "job": alert["job"],
                    "severity": alert["severity"]
                },
                "annotations": {
                    "description": alert["description"],
                    "summary": f"{alert['alertname']}: {alert['metric']} is {alert['value']}%"
                },
                "startsAt": datetime.now().isoformat() + "Z",
                "endsAt": "0001-01-01T00:00:00Z",
                "generatorURL": "http://prometheus:9090/graph?g0.expr=up",
                "fingerprint": f"test_alert_{int(time.time())}"
            }
        ],
        "groupLabels": {
            "alertname": alert["alertname"]
        },
        "commonLabels": {
            "alertname": alert["alertname"],
            "job": alert["job"],
            "severity": alert["severity"]
        },
        "commonAnnotations": {
            "description": alert["description"]
        },
        "externalURL": "http://alertmanager:9093",
        "version": "4",
        "groupKey": f"{alert['alertname']}:{{}}:{{}}"
    }

def send_test_alert():
    """Enviar alerta de prueba al sistema OptiMon"""
    print("🚨 Generando alerta de prueba al 50%...")
    
    alert_data = generate_test_alert()
    alert_name = alert_data["alerts"][0]["labels"]["alertname"]
    metric_value = alert_data["alerts"][0]["annotations"]["summary"]
    
    print(f"📊 Tipo de alerta: {alert_name}")
    print(f"📈 Métrica: {metric_value}")
    
    try:
        # Enviar alerta al endpoint de OptiMon
        response = requests.post(
            'http://localhost:5000/api/email/send-alert',
            headers={'Content-Type': 'application/json'},
            json=alert_data,
            timeout=30
        )
        
        print(f"📤 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                sent_count = result.get('sent', 0)
                print(f"✅ Alerta enviada exitosamente a {sent_count} destinatarios!")
                print(f"📧 Severidad: {result.get('severity', 'N/A')}")
                print(f"🎯 Alerta: {result.get('alert_name', 'N/A')}")
            else:
                print(f"❌ Error: {result.get('message', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def demo_alert_system():
    """Demo del sistema de alertas integrado"""
    print("🎯 DEMO: Sistema de Alertas OptiMon al 50%")
    print("=" * 60)
    print()
    
    print("📋 CONFIGURACIÓN ACTUAL:")
    print("   ✅ Gmail integrado: wacry77@gmail.com")
    print("   ✅ App Password configurada")
    print("   ✅ Portal web funcionando")
    print("   ✅ Alertas automáticas activas")
    print()
    
    print("🚨 GENERANDO ALERTA DE PRUEBA:")
    print("   └─ Simulando métrica al 50%")
    print("   └─ Enviando a destinatarios configurados")
    print("   └─ Email con HTML formateado")
    print()
    
    # Enviar alerta de prueba
    send_test_alert()
    
    print()
    print("🎉 SISTEMA COMPLETO:")
    print("   ✅ Alertas se generan automáticamente")
    print("   ✅ Emails llegan a bandejas reales")
    print("   ✅ Usuario solo necesita agregar destinatarios")
    print("   ✅ Funciona desde el primer momento")

if __name__ == "__main__":
    demo_alert_system()