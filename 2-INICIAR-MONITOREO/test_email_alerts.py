#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Probador de Alertas OptiMon - Versión para Test de Emails
Prueba el envío de alertas por email a las nuevas direcciones configuradas
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuración
ALERTMANAGER_URL = "http://localhost:9093"
WEBHOOK_URL = "http://localhost:8080"

def test_alertmanager_connection():
    """Prueba la conexión con AlertManager usando API v2"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ AlertManager está funcionando correctamente (API v2)")
            print(f"   → Estado del cluster: {status_data.get('cluster', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"❌ AlertManager respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con AlertManager: {e}")
        return False

def send_test_alert_v2(alert_type="email_test"):
    """Envía una alerta de prueba usando la API v2 de AlertManager"""
    
    alert_configs = {
        "email_test": {
            "labels": {
                "alertname": "Test_Email_Notification",
                "severity": "warning",
                "server_name": "TEST-SERVER",
                "server_type": "production",  # Para probar emails de producción
                "instance": "test-instance:9100",
                "job": "email-test"
            },
            "annotations": {
                "summary": "Prueba de envío de email a nuevas direcciones",
                "description": "Esta es una alerta de prueba para verificar que los emails lleguen correctamente a oagr2010@outlook.com y wacry77@gmail.com"
            }
        },
        "local_test": {
            "labels": {
                "alertname": "Test_Local_Email",
                "severity": "critical", 
                "server_name": "LOCAL-PC",
                "server_type": "local",  # Para probar emails locales
                "instance": "localhost:9100",
                "job": "local-test"
            },
            "annotations": {
                "summary": "Prueba de alerta local urgente",
                "description": "Test de notificación para PC local - verificando recepción en nuevas direcciones de email"
            }
        },
        "emergency_test": {
            "labels": {
                "alertname": "Test_Emergency_Email",
                "severity": "critical",
                "server_name": "PROD-EMERGENCY", 
                "server_type": "production",
                "instance": "emergency-server:9100",
                "job": "emergency-test"
            },
            "annotations": {
                "summary": "🚨 PRUEBA DE EMERGENCIA - Test de email crítico",
                "description": "Test de alerta crítica de emergencia para verificar plantilla HTML y recepción en ambas direcciones de correo"
            }
        }
    }
    
    if alert_type not in alert_configs:
        print(f"❌ Tipo de alerta '{alert_type}' no reconocido")
        return False
        
    config = alert_configs[alert_type]
    
    # Crear payload para AlertManager API v2
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    alerts_payload = [{
        "labels": config["labels"],
        "annotations": config["annotations"],
        "startsAt": current_time,
        "generatorURL": f"http://localhost:3000/test/{alert_type}"
    }]
    
    try:
        print(f"📧 Enviando alerta de prueba tipo '{alert_type}'...")
        print(f"   → Servidor: {config['labels']['server_name']}")
        print(f"   → Tipo: {config['labels']['server_type']}")
        print(f"   → Severidad: {config['labels']['severity']}")
        
        response = requests.post(
            f"{ALERTMANAGER_URL}/api/v2/alerts",
            json=alerts_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Alerta '{alert_type}' enviada correctamente a AlertManager")
            print(f"   → Los emails deberían llegar a:")
            print(f"     • oagr2010@outlook.com")
            print(f"     • wacry77@gmail.com")
            return True
        else:
            print(f"❌ Error enviando alerta: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando alerta: {e}")
        return False

def check_alertmanager_alerts():
    """Verifica las alertas activas en AlertManager usando API v2"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            print(f"\n📊 Alertas activas en AlertManager: {len(alerts)}")
            
            for alert in alerts:
                name = alert.get('labels', {}).get('alertname', 'Sin nombre')
                status = alert.get('status', {}).get('state', 'unknown')
                print(f"   • {name} - Estado: {status}")
            return True
        else:
            print(f"❌ Error consultando alertas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error consultando AlertManager: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DE EMAIL - ALERTAS OPTIMON")
    print("=" * 60)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📧 Direcciones de prueba:")
    print(f"   • oagr2010@outlook.com")
    print(f"   • wacry77@gmail.com")
    print()
    
    # 1. Verificar conexión con AlertManager
    print("1️⃣ VERIFICANDO CONEXIÓN CON ALERTMANAGER...")
    if not test_alertmanager_connection():
        print("❌ No se puede continuar sin AlertManager")
        return
    print()
    
    # 2. Verificar alertas existentes
    print("2️⃣ CONSULTANDO ALERTAS EXISTENTES...")
    check_alertmanager_alerts()
    print()
    
    # 3. Enviar diferentes tipos de alertas de prueba
    test_types = [
        ("email_test", "📧 Alerta de prueba general (producción)"),
        ("local_test", "💻 Alerta de PC local"),
        ("emergency_test", "🚨 Alerta de emergencia crítica")
    ]
    
    successful_tests = 0
    
    for test_type, description in test_types:
        print(f"3️⃣ PROBANDO: {description}")
        if send_test_alert_v2(test_type):
            successful_tests += 1
            print("   ✅ Enviado correctamente")
        else:
            print("   ❌ Error en el envío")
        
        print("   ⏳ Esperando 3 segundos...")
        time.sleep(3)
        print()
    
    # 4. Verificar que las alertas se registraron
    print("4️⃣ VERIFICANDO ALERTAS DESPUÉS DEL ENVÍO...")
    check_alertmanager_alerts()
    print()
    
    # 5. Resumen final
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 40)
    print(f"✅ Pruebas exitosas: {successful_tests}/{len(test_types)}")
    print(f"📧 Emails enviados a: oagr2010@outlook.com, wacry77@gmail.com")
    print()
    print("📝 INSTRUCCIONES:")
    print("• Revisa las bandejas de entrada de ambas direcciones")
    print("• Verifica que lleguen 3 emails diferentes (por dirección)")
    print("• Cada email debería tener formato HTML diferente según el tipo")
    print("• Los emails de emergencia deberían ser más llamativos (rojos)")
    print()
    print("🔗 ENLACES ÚTILES:")
    print(f"• AlertManager: {ALERTMANAGER_URL}")
    print(f"• Grafana: http://localhost:3000")
    print()
    print("✅ Pruebas de email completadas!")

if __name__ == "__main__":
    main()