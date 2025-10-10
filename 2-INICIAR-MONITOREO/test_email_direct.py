#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba Directa de Emails OptiMon
Prueba el envío de emails directamente a través de nuestro servicio SMTP
"""

import requests
import json
from datetime import datetime

def test_webhook_directly():
    """Prueba el servicio webhook directamente"""
    
    # Datos de prueba que simularían los que envía AlertManager
    test_alert_data = {
        "alerts": [
            {
                "labels": {
                    "alertname": "Test_Email_Direct",
                    "severity": "warning",
                    "server_name": "TEST-EMAIL-SERVER",
                    "server_type": "production",
                    "instance": "test-server:9100",
                    "job": "email-test"
                },
                "annotations": {
                    "summary": "Prueba directa de email - OptiMon",
                    "description": "Esta es una prueba directa del servicio de emails de OptiMon enviando a oagr2010@hotmail.com y wacry77@gmail.com"
                },
                "startsAt": datetime.now().isoformat() + "Z",
                "endsAt": "",
                "generatorURL": "http://localhost:3000/test/direct"
            }
        ],
        "status": "firing"
    }
    
    try:
        print("🧪 PRUEBA DIRECTA DEL SERVICIO DE EMAILS")
        print("=" * 50)
        print("📧 Enviando alerta de prueba directamente al servicio webhook...")
        
        # Probar conexión con el servicio
        health_response = requests.get("http://localhost:5555/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Servicio SMTP está funcionando")
            health_data = health_response.json()
            print(f"   → Estado: {health_data.get('status', 'unknown')}")
        else:
            print("❌ Servicio SMTP no responde")
            return False
        
        # Enviar alerta de prueba
        response = requests.post(
            "http://localhost:5555/send-alert",
            json=test_alert_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Alerta enviada exitosamente!")
            print(f"   → Estado: {result.get('status', 'unknown')}")
            print(f"   → Emails enviados: {result.get('sent', 0)}")
            print(f"   → Emails fallidos: {result.get('failed', 0)}")
            print(f"   → Mensaje: {result.get('message', 'Sin mensaje')}")
            
            print("\n📨 Los emails deberían llegar a:")
            print("   • oagr2010@hotmail.com")
            print("   • wacry77@gmail.com")
            print("\n⏰ Revisa tus bandejas de entrada en unos minutos")
            
            return True
        else:
            print(f"❌ Error enviando alerta: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def check_email_config():
    """Verifica la configuración de emails"""
    try:
        with open("config/optimon/email_recipients.json", 'r') as f:
            config = json.load(f)
            
        print("📧 CONFIGURACIÓN DE EMAILS:")
        print("=" * 30)
        
        if config.get("recipients"):
            for i, recipient in enumerate(config["recipients"], 1):
                default = " (PRINCIPAL)" if recipient["email"] == config.get("default_recipient") else ""
                status = "✅" if recipient.get("active", True) else "❌"
                print(f"{i}. {recipient['email']}{default} {status}")
        else:
            print("❌ No hay destinatarios configurados")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ Archivo de configuración de emails no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA DE SISTEMA DE EMAILS OPTIMON")
    print("=" * 60)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar configuración de emails
    print("1️⃣ VERIFICANDO CONFIGURACIÓN DE EMAILS...")
    if not check_email_config():
        print("\n❌ Configuración de emails no válida")
        print("💡 Ejecuta: python email_config.py list")
        return
    print()
    
    # 2. Probar el servicio directamente
    print("2️⃣ PROBANDO SERVICIO DE EMAILS...")
    if test_webhook_directly():
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("\n📋 SIGUIENTE PASO:")
        print("• Revisa tus bandejas de entrada")
        print("• Los emails pueden tardar 1-2 minutos en llegar")
        print("• Si no llegan, verifica la configuración SMTP del servicio")
    else:
        print("\n❌ PRUEBA FALLÓ")
        print("💡 Verifica que el servicio SMTP esté ejecutándose:")
        print("   python optimon_smtp_service.py")

if __name__ == "__main__":
    main()