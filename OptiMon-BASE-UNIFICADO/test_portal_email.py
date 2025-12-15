#!/usr/bin/env python3
"""
Test del endpoint de envío de emails desde el portal
"""

import requests
import json

def test_portal_email():
    """Probar envío desde el portal web"""
    print("🧪 Probando envío de email desde el portal...")
    
    # Datos del email de prueba
    email_data = {
        'to_email': 'wacry77@gmail.com',
        'subject': 'Prueba desde Portal OptiMon',
        'message': 'Este es un email de prueba enviado desde el portal web de OptiMon.',
        'type': 'info'
    }
    
    try:
        print(f"📧 Enviando a: {email_data['to_email']}")
        print(f"📋 Asunto: {email_data['subject']}")
        
        # Realizar petición POST al endpoint
        response = requests.post(
            'http://localhost:5000/api/email/send',
            headers={'Content-Type': 'application/json'},
            json=email_data,
            timeout=30
        )
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Respuesta completa: {result}")
            if result.get('success'):
                print("✅ Email enviado exitosamente desde el portal!")
                print(f"📝 Mensaje: {result.get('message', 'N/A')}")
            else:
                print(f"❌ Error en envío: {result.get('error', 'Error desconocido')}")
                print(f"📋 Detalles: {result}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_portal_email()