#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Alertas con API v2 - OptiMon
Envía alertas de prueba usando la API v2 de AlertManager
"""

import requests
import json
from datetime import datetime, timezone
import time

def send_test_alert_v2():
    """Envía una alerta de prueba usando API v2"""
    
    # Configurar alerta de prueba
    alert_data = [{
        "labels": {
            "alertname": "Test_Email_Hotmail_Gmail",
            "severity": "warning",
            "server_name": "TEST-EMAIL-SERVER",
            "server_type": "production",  # Para que use los receptores de producción
            "instance": "test-server:9100",
            "job": "email-test"
        },
        "annotations": {
            "summary": "Prueba de email a oagr2010@hotmail.com y wacry77@gmail.com",
            "description": "Esta es una alerta de prueba para verificar que los emails lleguen correctamente a ambas direcciones configuradas en AlertManager."
        },
        "startsAt": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "generatorURL": "http://localhost:3000/test/email"
    }]
    
    try:
        print("📧 Enviando alerta de prueba por email...")
        print(f"   → Direcciones objetivo:")
        print(f"     • oagr2010@hotmail.com")
        print(f"     • wacry77@gmail.com")
        print(f"   → Tipo: Alerta de producción (warning)")
        
        response = requests.post(
            "http://localhost:9093/api/v2/alerts",
            json=alert_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Alerta enviada exitosamente a AlertManager")
            print("📨 Los emails deberían llegar en unos momentos...")
            return True
        else:
            print(f"❌ Error al enviar alerta: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando alerta: {e}")
        return False

def check_alerts():
    """Verifica las alertas activas"""
    try:
        response = requests.get("http://localhost:9093/api/v2/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            print(f"\n📊 Alertas activas: {len(alerts)}")
            for alert in alerts:
                name = alert.get('labels', {}).get('alertname', 'Sin nombre')
                status = alert.get('status', {}).get('state', 'unknown')
                print(f"   • {name} - Estado: {status}")
        else:
            print(f"❌ Error consultando alertas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 PRUEBA DE EMAILS - ALERTMANAGER API v2")
    print("=" * 50)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar alertas existentes
    print("1️⃣ CONSULTANDO ALERTAS EXISTENTES...")
    check_alerts()
    print()
    
    # Enviar alerta de prueba
    print("2️⃣ ENVIANDO ALERTA DE PRUEBA...")
    if send_test_alert_v2():
        print()
        print("3️⃣ ESPERANDO PROCESAMIENTO...")
        time.sleep(5)
        
        print("4️⃣ VERIFICANDO ALERTAS DESPUÉS DEL ENVÍO...")
        check_alerts()
        
        print()
        print("📋 RESUMEN:")
        print("✅ Alerta enviada correctamente")
        print("📧 Revisa las bandejas de entrada:")
        print("   • oagr2010@hotmail.com")
        print("   • wacry77@gmail.com")
        print()
        print("⚠️ Nota: Los emails pueden tardar unos minutos en llegar")
        print("💡 Si no recibes emails, verifica la contraseña SMTP")
    else:
        print("❌ Error enviando la alerta")

if __name__ == "__main__":
    main()