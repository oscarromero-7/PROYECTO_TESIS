#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración Gmail real
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils

def test_gmail_config():
    """Probar envío real con Gmail"""
    print("🧪 Probando configuración Gmail real...")
    
    # Configuración Gmail
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'wacry77@gmail.com',
        'password': 'YOUR_GMAIL_APP_PASSWORD',
        'use_tls': True,
        'from_name': 'OptiMon Sistema de Monitoreo',
        'from_email': 'wacry77@gmail.com'
    }
    
    print(f"✅ Host: {smtp_config['host']}")
    print(f"✅ Puerto: {smtp_config['port']}")
    print(f"✅ Usuario: {smtp_config['username']}")
    print(f"✅ TLS: {smtp_config['use_tls']}")
    print(f"✅ Remitente: {smtp_config['from_email']}")
    
    # Intentar conexión de prueba
    print("\n🔗 Probando conexión SMTP...")
    
    try:
        # Crear mensaje de prueba
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✅ Prueba OptiMon - Gmail Configurado"
        msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg['To'] = smtp_config['username']  # Enviar a sí mismo
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # Contenido HTML
        html_content = """
        <html>
        <body>
            <h2 style="color: #4f46e5;">🎉 OptiMon Gmail Configurado</h2>
            <p>Este es un email de prueba del sistema OptiMon.</p>
            <p><strong>✅ Gmail funciona correctamente!</strong></p>
            <p>El sistema está listo para enviar alertas automáticas.</p>
            <hr>
            <small>OptiMon Sistema de Monitoreo v3.0.0</small>
        </body>
        </html>
        """
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Conectar y enviar
        print("📧 Enviando email de prueba...")
        
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            if smtp_config['use_tls']:
                server.starttls()
            
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        print("✅ EMAIL ENVIADO EXITOSAMENTE!")
        print(f"📥 Revisa tu bandeja de entrada: {smtp_config['username']}")
        print("\n🎉 Gmail está configurado y funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False

if __name__ == "__main__":
    try:
        if test_gmail_config():
            print("\n✅ Configuración Gmail verificada - OptiMon listo para alertas")
        else:
            print("\n❌ Hay problemas con la configuración Gmail")
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")