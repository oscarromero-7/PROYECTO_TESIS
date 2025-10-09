#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio SMTP Interno OptiMon
Servicio SMTP simple que no requiere configuración de contraseñas del usuario
"""

import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
import logging
import os
import json
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Para usar archivo .env, instala: pip install python-dotenv")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_smtp_config():
    """
    Configuración SMTP con múltiples opciones de proveedores
    Prioridad: Variables de entorno > Configuración manual
    """
    
    # Detectar proveedor basado en el email
    username = os.getenv('SMTP_USERNAME', '')
    
    if '@gmail.com' in username.lower():
        default_host = 'smtp.gmail.com'
        default_port = 587
    elif '@hotmail.com' in username.lower() or '@outlook.com' in username.lower():
        default_host = 'smtp-mail.outlook.com'
        default_port = 587
    elif '@yahoo.com' in username.lower():
        default_host = 'smtp.mail.yahoo.com'
        default_port = 587
    else:
        default_host = 'smtp.gmail.com'  # Default a Gmail
        default_port = 587
    
    return {
        'host': os.getenv('SMTP_HOST', default_host),
        'port': int(os.getenv('SMTP_PORT', str(default_port))),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        'timeout': int(os.getenv('SMTP_TIMEOUT', '30')),
        'from_name': os.getenv('EMAIL_FROM_NAME', 'OptiMon Alerts'),
        'from_display': os.getenv('EMAIL_FROM_DISPLAY', 'Sistema de Monitoreo OptiMon')
    }

# Obtener configuración SMTP
SMTP_CONFIG = get_smtp_config()

def load_email_recipients():
    """Carga la lista de destinatarios configurados"""
    # Buscar en ambas ubicaciones posibles
    config_paths = [
        Path("config/optimon/email_recipients.json"),
        Path("config/email_recipients.json")
    ]
    
    for config_file in config_paths:
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    recipients = []
                    for recipient in config.get("recipients", []):
                        if recipient.get("active", True):
                            recipients.append(recipient["email"])
                    return recipients
            except Exception as e:
                logging.error(f"Error leyendo {config_file}: {e}")
    
    # Si no encuentra archivos, usar emails por defecto
    logging.warning("No se encontró configuración de emails, usando emails por defecto")
    return ["oagr2010@hotmail.com", "wacry77@gmail.com"]

def send_email(to_email, subject, html_content, from_name=None):
    """
    Envía un email usando la configuración SMTP interna
    El usuario solo necesita proporcionar su email, no configuración SMTP
    """
    
    # Verificar configuración antes de intentar enviar
    if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
        logging.error("Configuración SMTP incompleta. Revisa las variables de entorno.")
        return False
    
    if SMTP_CONFIG['password'] == 'default_password':
        logging.error("Contraseña SMTP por defecto detectada. Configura SMTP_PASSWORD.")
        return False
    
    try:
        # Usar nombre configurado o por defecto
        display_name = from_name or SMTP_CONFIG['from_name']
        
        # Configurar el mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{display_name} <{SMTP_CONFIG['username']}>"
        msg['To'] = to_email
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # Agregar contenido HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Conectar y enviar con timeout
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'], timeout=SMTP_CONFIG['timeout']) as server:
            if SMTP_CONFIG['use_tls']:
                server.starttls()
            
            # Usar credenciales del sistema, no del usuario
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
            
        logging.info(f"Email enviado exitosamente a {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Error de autenticación SMTP: {e}")
        logging.error("Verifica usuario y contraseña SMTP")
        return False
    except smtplib.SMTPConnectError as e:
        logging.error(f"Error de conexión SMTP: {e}")
        logging.error("Verifica host y puerto SMTP")
        return False
    except Exception as e:
        logging.error(f"Error enviando email a {to_email}: {e}")
        return False

@app.route('/send-alert', methods=['POST'])
def send_alert_endpoint():
    """
    Endpoint para recibir alertas de AlertManager y enviarlas por email
    Envía automáticamente a todos los destinatarios configurados
    """
    try:
        data = request.get_json()
        
        if not data or 'alerts' not in data:
            return jsonify({'error': 'No alerts data provided'}), 400
        
        alerts = data['alerts']
        
        # Cargar destinatarios configurados
        recipients = load_email_recipients()
        
        if not recipients:
            logging.warning("No hay destinatarios configurados")
            return jsonify({'warning': 'No recipients configured'}), 200
        
        # Generar HTML para la alerta
        html_content = generate_alert_html(alerts)
        
        # Determinar el asunto basado en la severidad
        severity = 'info'
        for alert in alerts:
            alert_severity = alert.get('labels', {}).get('severity', 'info')
            if alert_severity == 'critical':
                severity = 'critical'
                break
            elif alert_severity == 'warning' and severity != 'critical':
                severity = 'warning'
        
        # Generar asunto
        alert_name = alerts[0].get('labels', {}).get('alertname', 'Unknown Alert')
        if severity == 'critical':
            subject = f"[CRITICAL] OptiMon Alert: {alert_name}"
        elif severity == 'warning':
            subject = f"[WARNING] OptiMon Alert: {alert_name}"
        else:
            subject = f"[INFO] OptiMon Alert: {alert_name}"
        
        # Enviar a todos los destinatarios activos
        sent_count = 0
        failed_count = 0
        
        for recipient_email in recipients:
            success = send_email(recipient_email, subject, html_content)
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        return jsonify({
            'status': 'success', 
            'sent': sent_count, 
            'failed': failed_count,
            'message': f'Alert sent to {sent_count} recipients'
        }), 200
            
    except Exception as e:
        logging.error(f"Error processing alert: {e}")
        return jsonify({'error': str(e)}), 500

def generate_alert_html(alerts):
    """Genera HTML para las alertas"""
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #ff6b6b; color: white; padding: 20px; border-radius: 5px; }
            .alert { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
            .critical { border-left: 5px solid #dc3545; background-color: #f8d7da; }
            .warning { border-left: 5px solid #ffc107; background-color: #fff3cd; }
            .info { border-left: 5px solid #17a2b8; background-color: #d1ecf1; }
            .footer { margin-top: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>OptiMon Alert</h2>
            <p>Sistema de Monitoreo de Infraestructura</p>
        </div>
    """
    
    for alert in alerts:
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        severity = labels.get('severity', 'info')
        
        html += f"""
        <div class="alert {severity}">
            <h3>{labels.get('alertname', 'Unknown Alert')}</h3>
            <p><strong>Severidad:</strong> {severity.upper()}</p>
            <p><strong>Servidor:</strong> {labels.get('server_name', labels.get('instance', 'Unknown'))}</p>
            <p><strong>Descripción:</strong> {annotations.get('description', annotations.get('summary', 'No description'))}</p>
            <p><strong>Tiempo:</strong> {alert.get('startsAt', 'Unknown')}</p>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>Este email fue enviado automáticamente por OptiMon</p>
            <p>Sistema de Monitoreo de Infraestructura</p>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'OptimOn SMTP Service'}), 200

def check_smtp_configuration():
    """Verifica la configuración SMTP antes de iniciar el servicio"""
    print("\n>> VERIFICANDO CONFIGURACION SMTP...")
    print("-" * 40)
    
    # Verificar variables requeridas
    required_vars = {
        'SMTP_USERNAME': SMTP_CONFIG['username'],
        'SMTP_PASSWORD': SMTP_CONFIG['password'],
        'SMTP_HOST': SMTP_CONFIG['host'],
        'SMTP_PORT': SMTP_CONFIG['port']
    }
    
    missing_vars = []
    
    for var_name, var_value in required_vars.items():
        if not var_value or (var_name == 'SMTP_PASSWORD' and var_value == 'default_password'):
            missing_vars.append(var_name)
            print(f"[X] {var_name}: No configurado")
        else:
            # Ocultar contraseña para mostrar
            display_value = var_value if var_name != 'SMTP_PASSWORD' else '*' * len(str(var_value))
            print(f"[OK] {var_name}: {display_value}")
    
    print(f">> Proveedor detectado: {SMTP_CONFIG['host']}")
    print(f">> TLS habilitado: {'Si' if SMTP_CONFIG['use_tls'] else 'No'}")
    
    if missing_vars:
        print(f"\n[X] CONFIGURACION INCOMPLETA")
        print("Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n>> COMO CONFIGURAR:")
        print("1. Crea un archivo .env en esta carpeta")
        print("2. Copia el contenido de .env.example")
        print("3. Configura tus credenciales SMTP reales")
        print("4. Reinicia el servicio")
        return False
    else:
        print("\n[OK] CONFIGURACION SMTP COMPLETA")
        print(">> Servicio listo para enviar emails")
        return True

if __name__ == '__main__':
    print(">> Iniciando OptiMon SMTP Service...")
    print(">> Servicio que envia alertas sin requerir configuracion SMTP del usuario")
    print(">> El usuario solo necesita indicar su email")
    print("=" * 60)
    
    # Verificar configuración antes de iniciar
    if check_smtp_configuration():
        print(f"\n>> Iniciando servidor en http://localhost:5555")
        app.run(host='0.0.0.0', port=5555, debug=False)
    else:
        print("\n>> Servicio NO iniciado debido a configuracion incompleta")
        print(">> Configura las variables SMTP y vuelve a intentar")