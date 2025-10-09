#!/usr/bin/env python3
"""
Test de gestión de destinatarios de alertas
"""

import requests
import json
from datetime import datetime

def test_recipients_management():
    """Probar la gestión completa de destinatarios"""
    base_url = "http://localhost:5000"
    
    print("🧪 Probando gestión de destinatarios de alertas")
    print("=" * 50)
    
    # 1. Obtener destinatarios actuales
    print("\n1. 📋 Obteniendo destinatarios actuales...")
    response = requests.get(f"{base_url}/api/email/recipients")
    if response.status_code == 200:
        current = response.json()
        print(f"✅ Destinatarios actuales: {len(current.get('recipients', []))}")
        for recipient in current.get('recipients', []):
            print(f"   📧 {recipient['name']} <{recipient['email']}> - {'✅' if recipient['active'] else '❌'}")
    else:
        print(f"❌ Error obteniendo destinatarios: {response.status_code}")
        return
    
    # 2. Agregar nuevo destinatario
    print("\n2. ➕ Agregando nuevo destinatario...")
    new_recipient = {
        "add_recipient": {
            "email": "test@ejemplo.com",
            "name": "Usuario Test",
            "active": True
        }
    }
    
    response = requests.post(
        f"{base_url}/api/email/recipients",
        json=new_recipient,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Destinatario agregado: {result.get('message', 'OK')}")
    else:
        print(f"❌ Error agregando destinatario: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # 3. Verificar que se agregó
    print("\n3. 🔍 Verificando destinatarios después de agregar...")
    response = requests.get(f"{base_url}/api/email/recipients")
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ Total de destinatarios: {len(updated.get('recipients', []))}")
        for recipient in updated.get('recipients', []):
            print(f"   📧 {recipient['name']} <{recipient['email']}> - {'✅' if recipient['active'] else '❌'}")
    
    # 4. Configurar destinatario por defecto
    print("\n4. ⭐ Configurando destinatario por defecto...")
    default_config = {
        "set_default": "test@ejemplo.com"
    }
    
    response = requests.post(
        f"{base_url}/api/email/recipients",
        json=default_config,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("✅ Destinatario por defecto configurado")
    else:
        print(f"❌ Error configurando destinatario por defecto: {response.status_code}")
    
    # 5. Probar envío de alerta de prueba
    print("\n5. 📤 Enviando alerta de prueba...")
    test_alert = {
        "test_alert": {
            "title": "Alerta de Prueba OptiMon",
            "message": "Esta es una alerta de prueba para verificar el sistema de notificaciones.",
            "severity": "info",
            "recipient": "test@ejemplo.com"
        }
    }
    
    response = requests.post(
        f"{base_url}/api/email/recipients",
        json=test_alert,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("✅ Alerta de prueba enviada")
    else:
        print(f"❌ Error enviando alerta de prueba: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 Test de destinatarios completado")

if __name__ == "__main__":
    test_recipients_management()