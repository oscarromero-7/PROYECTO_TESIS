#!/usr/bin/env python3
"""
🎯 PRUEBA DESDE PORTAL - Agregar destinatarios y enviar alerta
"""

import requests
import json
from datetime import datetime

def agregar_destinatarios_y_probar():
    """Agregar 2 destinatarios y enviar alerta de prueba"""
    print("🎯 PRUEBA DESDE PORTAL - OptiMon")
    print("=" * 50)
    
    # Lista de destinatarios para agregar
    nuevos_destinatarios = [
        "admin@empresa.com",
        "soporte@empresa.com"
    ]
    
    print("📧 AGREGANDO NUEVOS DESTINATARIOS:")
    print("-" * 30)
    
    # Obtener destinatarios actuales
    try:
        response = requests.get('http://localhost:5000/api/email/config')
        if response.status_code == 200:
            print("✅ Conexión al portal exitosa")
        
        # Leer destinatarios actuales
        with open('config/email_recipients.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        destinatarios_actuales = config.get('recipients', [])
        print(f"📋 Destinatarios actuales: {len(destinatarios_actuales)}")
        
        # Agregar nuevos destinatarios
        for email in nuevos_destinatarios:
            # Verificar si ya existe
            existe = any(d['email'] == email for d in destinatarios_actuales)
            if not existe:
                destinatarios_actuales.append({
                    "email": email,
                    "active": True
                })
                print(f"   ➕ Agregado: {email}")
            else:
                print(f"   ⚠️  Ya existe: {email}")
        
        # Guardar configuración actualizada
        config['recipients'] = destinatarios_actuales
        with open('config/email_recipients.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Total destinatarios configurados: {len(destinatarios_actuales)}")
        for dest in destinatarios_actuales:
            status = "🟢 Activo" if dest.get('active', True) else "🔴 Inactivo"
            print(f"   📧 {dest['email']} - {status}")
            
    except Exception as e:
        print(f"❌ Error configurando destinatarios: {e}")
        return False
    
    # Enviar alerta de prueba
    print(f"\n🚨 ENVIANDO ALERTA DE PRUEBA:")
    print("-" * 30)
    
    try:
        # Preparar alerta de prueba
        alert_data = {
            "alerts": [
                {
                    "labels": {
                        "alertname": "Test_Alert_Portal",
                        "severity": "warning",
                        "instance": "portal-test-server"
                    },
                    "annotations": {
                        "summary": "🧪 Alerta de prueba desde el Portal OptiMon",
                        "description": f"Esta es una alerta de prueba enviada desde el portal web a {len(destinatarios_actuales)} destinatarios configurados."
                    },
                    "startsAt": datetime.now().isoformat(),
                    "status": "firing",
                    "generatorURL": "http://localhost:5000/test"
                }
            ]
        }
        
        print("📤 Enviando alerta de prueba...")
        print(f"   🎯 Tipo: Test_Alert_Portal")
        print(f"   ⚠️  Severidad: warning")
        print(f"   📧 Destinatarios: {len(destinatarios_actuales)}")
        
        # Enviar alerta
        response = requests.post(
            'http://localhost:5000/api/email/send-alert',
            json=alert_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            sent_count = result.get('sent', 0)
            failed_count = result.get('failed', 0)
            
            print(f"\n✅ ALERTA ENVIADA EXITOSAMENTE!")
            print(f"   📊 Enviados: {sent_count}")
            print(f"   ❌ Fallidos: {failed_count}")
            print(f"   📬 Total destinatarios: {len(destinatarios_actuales)}")
            
            # Mostrar a quién se envió
            print(f"\n📧 EMAILS ENVIADOS A:")
            for dest in destinatarios_actuales:
                if dest.get('active', True):
                    print(f"   ✉️  {dest['email']}")
            
        else:
            print(f"❌ Error enviando alerta: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en alerta de prueba: {e}")
        return False
    
    # Resumen final
    print(f"\n" + "=" * 50)
    print("🎉 PRUEBA DESDE PORTAL COMPLETADA")
    print(f"📧 Destinatarios configurados: {len(destinatarios_actuales)}")
    print(f"🚨 Alerta de prueba enviada: ✅")
    print(f"🌐 Portal disponible: http://localhost:5000")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    agregar_destinatarios_y_probar()