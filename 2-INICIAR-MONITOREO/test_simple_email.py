#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba Simple de Email OptiMon
Prueba directa del envío de emails usando el servicio SMTP
"""

import requests
import json
from datetime import datetime

def test_email_sending():
    """Prueba directa del envío de emails"""
    
    print("🧪 PRUEBA DIRECTA DE ENVÍO DE EMAILS")
    print("=" * 50)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Datos de prueba simples
    test_data = {
        "alerts": [
            {
                "labels": {
                    "alertname": "TestEmail_OptiMon",
                    "severity": "warning",
                    "server_name": "TEST-SERVER",
                    "instance": "localhost:9100"
                },
                "annotations": {
                    "summary": "Prueba de email OptiMon",
                    "description": "Esta es una prueba del sistema de emails. Si recibes este mensaje, ¡el sistema está funcionando!"
                },
                "startsAt": datetime.now().isoformat() + "Z"
            }
        ],
        "status": "firing"
    }
    
    try:
        print("📧 Enviando datos de prueba al servicio...")
        print(f"📋 Datos: {json.dumps(test_data, indent=2)}")
        print()
        
        # Enviar solicitud
        response = requests.post(
            "http://localhost:5555/send-alert",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📤 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa del servidor:")
            print(f"   📊 Estado: {result.get('status', 'desconocido')}")
            print(f"   📧 Emails enviados: {result.get('sent', 0)}")
            print(f"   ❌ Emails fallidos: {result.get('failed', 0)}")
            print(f"   💬 Mensaje: {result.get('message', 'Sin mensaje')}")
            
            if result.get('sent', 0) > 0:
                print("\n🎉 ¡EMAILS ENVIADOS EXITOSAMENTE!")
                print("📨 Revisa las siguientes bandejas de entrada:")
                print("   • oagr2010@hotmail.com")
                print("   • wacry77@gmail.com")
                print("\n⏰ Los emails pueden tardar 1-2 minutos en llegar")
            else:
                print("\n⚠️  No se enviaron emails - revisar configuración")
                
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Respuesta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio SMTP")
        print("💡 Asegúrate de que esté ejecutándose: python optimon_smtp_service.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_email_sending()