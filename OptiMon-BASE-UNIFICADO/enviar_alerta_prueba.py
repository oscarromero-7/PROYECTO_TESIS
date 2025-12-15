#!/usr/bin/env python3
"""
🧪 PRUEBA DE ALERTA - Enviar alerta a destinatarios configurados
"""

import requests
import json
from datetime import datetime

def enviar_alerta_prueba():
    """Enviar alerta de prueba a todos los destinatarios"""
    print("🧪 ENVIANDO ALERTA DE PRUEBA")
    print("=" * 40)
    
    # Verificar destinatarios configurados
    try:
        with open('config/email_recipients.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        recipients = config.get('recipients', [])
        
        # Manejar ambos formatos: lista de strings o lista de objetos
        active_recipients = []
        if recipients:
            if isinstance(recipients[0], str):
                # Formato simple: lista de emails
                active_recipients = recipients
            else:
                # Formato completo: lista de objetos
                active_recipients = [r['email'] for r in recipients if r.get('active', True)]
        
        print(f"📧 Destinatarios configurados: {len(active_recipients)}")
        for email in active_recipients:
            print(f"   ✉️  {email}")
        
        if not active_recipients:
            print("❌ No hay destinatarios activos configurados")
            return False
            
    except Exception as e:
        print(f"❌ Error leyendo destinatarios: {e}")
        return False
    
    # Preparar alerta de prueba
    alert_data = {
        "alerts": [
            {
                "labels": {
                    "alertname": "Prueba_Portal_OptiMon",
                    "severity": "warning",
                    "instance": "servidor-prueba-01"
                },
                "annotations": {
                    "summary": "🧪 Alerta de Prueba desde Portal OptiMon",
                    "description": f"Esta es una alerta de prueba enviada a {len(active_recipients)} destinatarios configurados desde el portal web. Sistema funcionando correctamente."
                },
                "startsAt": datetime.now().isoformat(),
                "status": "firing",
                "generatorURL": "http://localhost:5000/test"
            }
        ]
    }
    
    print(f"\n🚨 ENVIANDO ALERTA:")
    print(f"   🎯 Nombre: Prueba_Portal_OptiMon")
    print(f"   ⚠️  Severidad: warning")
    print(f"   🖥️  Servidor: servidor-prueba-01")
    print(f"   📧 Destinatarios: {len(active_recipients)}")
    
    try:
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
            
            print(f"\n✅ RESULTADO:")
            print(f"   📤 Enviados exitosamente: {sent_count}")
            print(f"   ❌ Fallidos: {failed_count}")
            
            if sent_count > 0:
                print(f"\n🎉 ¡ALERTA ENVIADA EXITOSAMENTE!")
                print(f"📬 Revisa las bandejas de entrada de:")
                for email in active_recipients:
                    print(f"   📧 {email}")
            else:
                print(f"\n⚠️  No se pudo enviar a ningún destinatario")
                
        else:
            print(f"\n❌ Error del servidor: {response.status_code}")
            print(f"📝 Mensaje: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error enviando alerta: {e}")
        return False
    
    print(f"\n" + "=" * 40)
    print("🧪 PRUEBA COMPLETADA")
    return True

if __name__ == "__main__":
    enviar_alerta_prueba()