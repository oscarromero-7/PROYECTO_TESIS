#!/usr/bin/env python3
"""
Test de alerta real - Simular alta CPU para probar alertas
"""

import requests
import json
import time

def trigger_test_alert():
    """Disparar una alerta real a través de AlertManager"""
    print("🚨 Generando alerta de prueba real...")
    
    # Crear alerta simulada para AlertManager
    alert_data = [{
        "labels": {
            "alertname": "HighCPUUsage",
            "instance": "localhost:9182",
            "job": "local_windows",
            "severity": "warning"
        },
        "annotations": {
            "summary": "Alto uso de CPU detectado",
            "description": "El uso de CPU ha superado el 80% por más de 5 minutos"
        },
        "startsAt": "2025-10-09T19:00:00.000Z",
        "endsAt": "0001-01-01T00:00:00.000Z",
        "generatorURL": "http://localhost:9090/graph?g0.expr=windows_cpu_time_total&g0.tab=1"
    }]
    
    try:
        # Enviar alerta directamente a AlertManager usando API v2
        response = requests.post(
            "http://localhost:9093/api/v2/alerts",
            json=alert_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Alerta enviada a AlertManager exitosamente")
            print("📧 AlertManager debería procesar y enviar por email...")
            
            # Esperar un poco para que se procese
            print("⏱️ Esperando procesamiento de alerta...")
            time.sleep(10)
            
            # Verificar alertas activas en AlertManager usando API v2
            alerts_response = requests.get("http://localhost:9093/api/v2/alerts")
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                active_alerts = len(alerts)
                print(f"📊 Alertas activas en AlertManager: {active_alerts}")
            
        else:
            print(f"❌ Error enviando alerta: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_test_alert()