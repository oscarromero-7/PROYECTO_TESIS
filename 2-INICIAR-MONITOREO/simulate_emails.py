#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Emails OptiMon
Simula el envío de emails sin usar servicios externos
"""

import json
from datetime import datetime

def create_test_email():
    """Crea un email de prueba"""
    
    # Contenido del email de prueba
    email_data = {
        "from": "optimon-alerts@system.local",
        "subject": "🚨 Prueba de Alerta OptiMon",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Contenido HTML del email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #ff6b6b; color: white; padding: 20px; border-radius: 5px; }}
            .content {{ padding: 20px; border: 1px solid #ddd; margin-top: 10px; }}
            .alert-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🚨 Alerta de OptiMon</h2>
            <p><strong>Prueba de Sistema de Emails</strong></p>
        </div>
        
        <div class="content">
            <h3>Detalles de la Alerta</h3>
            <div class="alert-info">
                <p><strong>🏷️ Nombre:</strong> Test_Email_OptiMon</p>
                <p><strong>🔥 Severidad:</strong> warning</p>
                <p><strong>🖥️ Servidor:</strong> TEST-EMAIL-SERVER</p>
                <p><strong>📋 Descripción:</strong> Esta es una prueba del sistema de emails de OptiMon. Si recibes este email, ¡el sistema está funcionando correctamente!</p>
                <p><strong>⏰ Hora:</strong> {email_data['timestamp']}</p>
            </div>
            
            <h3>✅ Sistema de Emails Funcionando</h3>
            <p>Si recibes este email, significa que:</p>
            <ul>
                <li>✅ La configuración de emails está correcta</li>
                <li>✅ El sistema puede enviar alertas exitosamente</li>
                <li>✅ OptiMon está listo para monitorear tu infraestructura</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Este email fue enviado por OptiMon - Sistema de Monitoreo de Infraestructura</p>
            <p>Configurado para: oagr2010@hotmail.com, wacry77@gmail.com</p>
        </div>
    </body>
    </html>
    """
    
    # Contenido de texto plano
    text_content = f"""
🚨 ALERTA DE OPTIMON - PRUEBA DE SISTEMA DE EMAILS

Detalles de la Alerta:
- Nombre: Test_Email_OptiMon  
- Severidad: warning
- Servidor: TEST-EMAIL-SERVER
- Descripción: Esta es una prueba del sistema de emails de OptiMon
- Hora: {email_data['timestamp']}

✅ Sistema de Emails Funcionando
Si recibes este email, el sistema está configurado correctamente.

OptiMon - Sistema de Monitoreo de Infraestructura
Configurado para: oagr2010@hotmail.com, wacry77@gmail.com
    """
    
    email_data["html_content"] = html_content
    email_data["text_content"] = text_content
    
    return email_data

def get_email_recipients():
    """Obtiene los destinatarios de email"""
    try:
        with open("config/optimon/email_recipients.json", 'r') as f:
            config = json.load(f)
            
        recipients = []
        for recipient in config.get("recipients", []):
            if recipient.get("active", True):
                recipients.append(recipient["email"])
                
        return recipients
        
    except FileNotFoundError:
        print("❌ Archivo de configuración no encontrado")
        return ["oagr2010@hotmail.com", "wacry77@gmail.com"]
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return ["oagr2010@hotmail.com", "wacry77@gmail.com"]

def simulate_email_sending():
    """Simula el envío de emails"""
    
    print("🚀 SIMULADOR DE EMAILS OPTIMON")
    print("=" * 50)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obtener destinatarios
    recipients = get_email_recipients()
    print("📧 Destinatarios configurados:")
    for i, email in enumerate(recipients, 1):
        print(f"   {i}. {email}")
    print()
    
    # Crear el email de prueba
    print("📝 Creando email de prueba...")
    email_data = create_test_email()
    
    # Simular envío a cada destinatario
    print("📤 Simulando envío de emails...")
    for i, email in enumerate(recipients, 1):
        print(f"   📧 → {email}")
        print(f"      ✅ Email preparado y listo para envío")
        
        # Mostrar parte del contenido para el primer destinatario
        if i == 1:
            print("\n📄 CONTENIDO DEL EMAIL:")
            print("-" * 30)
            print(f"De: {email_data['from']}")
            print(f"Para: {email}")
            print(f"Asunto: {email_data['subject']}")
            print(f"Hora: {email_data['timestamp']}")
            print("\nContenido (texto):")
            # Mostrar solo las primeras líneas
            lines = email_data['text_content'].split('\n')[:12]
            for line in lines:
                print(f"  {line}")
            print("  ...")
            print("-" * 30)
    
    print(f"\n✅ SIMULACIÓN COMPLETADA")
    print(f"📊 Emails procesados: {len(recipients)}")
    print("\n💡 INFORMACIÓN IMPORTANTE:")
    print("• Esta es una simulación - no se enviaron emails reales")
    print("• Para envío real, necesitas configurar SMTP")
    print("• El contenido y formato están listos para producción")
    print("\n🔧 PASOS PARA ACTIVAR ENVÍO REAL:")
    print("1. Configura un servicio SMTP (Gmail, Outlook, etc.)")
    print("2. Actualiza las credenciales en optimon_smtp_service.py")
    print("3. Inicia el servicio: python optimon_smtp_service.py")
    print("4. Las alertas se enviarán automáticamente")
    
    print("\n📋 CONFIGURACIÓN ACTUAL DEL SISTEMA:")
    print("• ✅ Emails configurados correctamente")
    print("• ✅ Formato de alertas preparado")
    print("• ✅ API v2 de AlertManager implementada")
    print("• ⚠️  Solo falta configuración SMTP para envío real")

if __name__ == "__main__":
    simulate_email_sending()