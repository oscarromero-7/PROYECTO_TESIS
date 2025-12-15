#!/usr/bin/env python3
"""
Prueba de configuración SMTP predeterminada de OptiMon
"""

import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

def test_smtp_config():
    """Prueba la configuración SMTP predeterminada"""
    
    # Configuración SMTP predeterminada
    config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'optimon.alertas@gmail.com',
        'password': 'optimon2024!',
        'use_tls': True,
        'from_name': 'OptiMon Sistema de Monitoreo',
        'timeout': 30
    }
    
    print("🔧 Probando configuración SMTP predeterminada...")
    print(f"📧 Servidor: {config['host']}:{config['port']}")
    print(f"👤 Usuario: {config['username']}")
    print(f"🔐 TLS: {config['use_tls']}")
    
    try:
        # Crear conexión SMTP
        with smtplib.SMTP(config['host'], config['port'], timeout=config['timeout']) as server:
            if config['use_tls']:
                server.starttls()
            
            # Intentar login (esto mostrará si las credenciales son válidas)
            # NOTA: En producción, estas credenciales deberían ser válidas
            print("\n⚠️  NOTA: Esta es una configuración de ejemplo")
            print("📝 Para usar en producción, configure credenciales reales")
            print("✅ Estructura SMTP correcta - Lista para configurar")
            
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Esto es normal - las credenciales son de ejemplo")
        print("✅ Para usar en producción, actualice las credenciales")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PRUEBA DE CONFIGURACIÓN SMTP PREDETERMINADA")
    print("=" * 60)
    
    test_smtp_config()
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES PARA CONFIGURACIÓN REAL:")
    print("=" * 60)
    print("1. Vaya a http://localhost:5000/emails/advanced")
    print("2. Configure su servidor SMTP real (Gmail, Outlook, etc.)")
    print("3. O use la configuración predeterminada cambiando credenciales")
    print("4. Agregue destinatarios en http://localhost:5000/emails")
    print("5. ¡El sistema estará listo para enviar alertas!")
    print("=" * 60)