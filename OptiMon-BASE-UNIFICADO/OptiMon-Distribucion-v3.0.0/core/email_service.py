#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon - Email Service Unificado
Servicio SMTP integrado con todas las funcionalidades de alertas y notificaciones
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

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== CONFIGURACIÓN SMTP =====

def get_smtp_config():
    """Obtener configuración SMTP desde variables de entorno o .env"""
    try:
        # Cargar desde .env si existe
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    except Exception as e:
        logger.warning(f"No se pudo cargar .env: {e}")
    
    # Configuración por defecto para OptiMon
    return {
        'host': os.getenv('SMTP_HOST', 'smtp-mail.outlook.com'),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME', 'Proyecto20251985@hotmail.com'),
        'password': os.getenv('SMTP_PASSWORD', 'proyecto2025'),
        'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        'from_name': os.getenv('EMAIL_FROM_NAME', 'OptiMon Sistema de Monitoreo'),
        'timeout': int(os.getenv('SMTP_TIMEOUT', '30'))
    }

# Cargar configuración SMTP
SMTP_CONFIG = get_smtp_config()

def load_email_recipients():
    """Cargar lista de destinatarios configurados"""
    try:
        config_files = [
            Path('config/email_recipients.json'),
            Path('emails_config.json')
        ]
        
        for config_file in config_files:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if isinstance(config, dict) and 'recipients' in config:
                        return [r['email'] for r in config['recipients'] if r.get('active', True)]
                    elif isinstance(config, list):
                        return [email for email in config if email]
        
        # Destinatarios por defecto
        return ['Proyecto20251985@hotmail.com']
        
    except Exception as e:
        logger.error(f"Error cargando destinatarios: {e}")
        return ['Proyecto20251985@hotmail.com']

def send_email(to_email, subject, html_content, from_name=None):
    """Enviar email usando configuración SMTP unificada"""
    
    # Verificar configuración
    if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
        logger.error("❌ Configuración SMTP incompleta")
        return False
    
    try:
        # Configurar mensaje
        display_name = from_name or SMTP_CONFIG['from_name']
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{display_name} <{SMTP_CONFIG['username']}>"
        msg['To'] = to_email
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # Crear versión HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Conectar y enviar
        logger.info(f"📧 Enviando email a {to_email}...")
        
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.set_debuglevel(0)
            
            if SMTP_CONFIG['use_tls']:
                server.starttls()
            
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
            
        logger.info(f"✅ Email enviado exitosamente a {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ Error de autenticación SMTP - Verificar credenciales")
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"❌ Destinatario rechazado: {to_email}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ Error SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False

def generate_alert_html(alerts):
    """Generar HTML para alertas con diseño mejorado"""
    
    # Determinar severidad general
    severity = 'info'
    for alert in alerts:
        alert_severity = alert.get('labels', {}).get('severity', 'info')
        if alert_severity == 'critical':
            severity = 'critical'
            break
        elif alert_severity == 'warning' and severity != 'critical':
            severity = 'warning'
    
    # Configurar colores según severidad
    if severity == 'critical':
        bg_color = '#dc3545'
        border_color = '#dc3545'
        emoji = '🚨'
    elif severity == 'warning':
        bg_color = '#fd7e14'
        border_color = '#fd7e14'
        emoji = '⚠️'
    else:
        bg_color = '#20c997'
        border_color = '#20c997'
        emoji = 'ℹ️'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OptiMon Alert</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: #f8f9fa;
                line-height: 1.6;
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: white; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{ 
                background-color: {bg_color}; 
                color: white; 
                padding: 30px 20px; 
                text-align: center;
                background-image: linear-gradient(135deg, {bg_color} 0%, {bg_color}CC 100%);
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 24px; 
                font-weight: 600;
            }}
            .content {{ 
                padding: 30px 20px; 
            }}
            .alert {{ 
                border: 1px solid #e9ecef; 
                margin: 15px 0; 
                padding: 20px; 
                border-radius: 8px; 
                border-left: 5px solid {border_color};
                background-color: #f8f9fa;
            }}
            .alert-title {{ 
                font-weight: 600; 
                font-size: 18px; 
                color: #343a40;
                margin-bottom: 10px;
            }}
            .alert-description {{ 
                color: #6c757d; 
                margin-bottom: 15px;
            }}
            .alert-details {{ 
                background-color: white; 
                padding: 15px; 
                border-radius: 5px; 
                border: 1px solid #dee2e6;
            }}
            .detail-row {{ 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 8px;
                padding: 5px 0;
                border-bottom: 1px solid #f8f9fa;
            }}
            .detail-row:last-child {{ 
                border-bottom: none; 
                margin-bottom: 0;
            }}
            .detail-label {{ 
                font-weight: 600; 
                color: #495057;
            }}
            .detail-value {{ 
                color: #6c757d;
                word-break: break-word;
            }}
            .footer {{ 
                background-color: #f8f9fa; 
                padding: 20px; 
                text-align: center; 
                border-top: 1px solid #dee2e6;
                color: #6c757d; 
                font-size: 12px;
            }}
            .timestamp {{ 
                background-color: #e9ecef; 
                padding: 10px; 
                border-radius: 5px; 
                text-align: center; 
                margin-top: 20px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #495057;
            }}
            .severity-badge {{
                display: inline-block;
                padding: 4px 12px;
                background-color: {border_color};
                color: white;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} OptiMon Sistema de Alertas</h1>
                <div style="margin-top: 10px; font-size: 16px; opacity: 0.9;">
                    {len(alerts)} Alerta{'s' if len(alerts) != 1 else ''} - Severidad: {severity.title()}
                    <span class="severity-badge">{severity.upper()}</span>
                </div>
            </div>
            
            <div class="content">"""
    
    # Agregar cada alerta
    for i, alert in enumerate(alerts, 1):
        alert_name = alert.get('labels', {}).get('alertname', 'Unknown Alert')
        alert_summary = alert.get('annotations', {}).get('summary', 'No summary available')
        alert_description = alert.get('annotations', {}).get('description', 'No description available')
        alert_instance = alert.get('labels', {}).get('instance', 'Unknown instance')
        alert_job = alert.get('labels', {}).get('job', 'Unknown job')
        alert_severity = alert.get('labels', {}).get('severity', 'info')
        start_time = alert.get('startsAt', datetime.now().isoformat())
        
        html += f"""
                <div class="alert">
                    <div class="alert-title">
                        🔔 Alerta #{i}: {alert_name}
                    </div>
                    <div class="alert-description">
                        <strong>Resumen:</strong> {alert_summary}<br>
                        <strong>Descripción:</strong> {alert_description}
                    </div>
                    <div class="alert-details">
                        <div class="detail-row">
                            <span class="detail-label">Severidad:</span>
                            <span class="detail-value">{alert_severity.upper()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Instancia:</span>
                            <span class="detail-value">{alert_instance}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Job:</span>
                            <span class="detail-value">{alert_job}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Tiempo de inicio:</span>
                            <span class="detail-value">{start_time}</span>
                        </div>
                    </div>
                </div>"""
    
    html += f"""
            </div>
            
            <div class="footer">
                <div style="font-weight: 600; margin-bottom: 10px;">
                    OptiMon - Sistema de Monitoreo Unificado
                </div>
                <div>
                    Este email fue generado automáticamente por el sistema de alertas<br>
                    Versión 3.0.0-UNIFIED | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    📊 <a href="http://localhost:3000" style="color: {border_color};">Grafana Dashboard</a> | 
                    🔍 <a href="http://localhost:9090" style="color: {border_color};">Prometheus</a> | 
                    🎛️ <a href="http://localhost:5000" style="color: {border_color};">Panel de Control</a>
                </div>
                
                <div class="timestamp">
                    Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                    ID: {datetime.now().strftime('%Y%m%d%H%M%S')}
                </div>
            </div>
        </div>
    </body>
    </html>"""
    
    return html

# ===== ENDPOINTS API =====

@app.route('/health', methods=['GET'])
def health_check():
    """Health check del servicio email"""
    return jsonify({
        'status': 'ok',
        'service': 'OptiMon Email Service Unified',
        'version': '3.0.0',
        'timestamp': datetime.now().isoformat(),
        'smtp_configured': bool(SMTP_CONFIG['username'] and SMTP_CONFIG['password'])
    })

@app.route('/send-alert', methods=['POST'])
def send_alert_endpoint():
    """Endpoint principal para recibir alertas de AlertManager"""
    try:
        data = request.get_json()
        
        if not data or 'alerts' not in data:
            return jsonify({'error': 'No alerts data provided'}), 400
        
        alerts = data['alerts']
        
        # Cargar destinatarios
        recipients = load_email_recipients()
        
        if not recipients:
            logger.warning("⚠️ No hay destinatarios configurados")
            return jsonify({'warning': 'No recipients configured'}), 200
        
        # Generar HTML
        html_content = generate_alert_html(alerts)
        
        # Determinar asunto
        severity = 'info'
        for alert in alerts:
            alert_severity = alert.get('labels', {}).get('severity', 'info')
            if alert_severity == 'critical':
                severity = 'critical'
                break
            elif alert_severity == 'warning' and severity != 'critical':
                severity = 'warning'
        
        alert_name = alerts[0].get('labels', {}).get('alertname', 'Multiple Alerts') if alerts else 'Alert'
        
        if severity == 'critical':
            subject = f"🚨 [CRÍTICO] OptiMon: {alert_name}"
        elif severity == 'warning':
            subject = f"⚠️ [ADVERTENCIA] OptiMon: {alert_name}"
        else:
            subject = f"ℹ️ [INFO] OptiMon: {alert_name}"
        
        # Enviar a todos los destinatarios
        sent_count = 0
        failed_count = 0
        
        for recipient_email in recipients:
            if send_email(recipient_email, subject, html_content):
                sent_count += 1
            else:
                failed_count += 1
        
        logger.info(f"📊 Resumen envío: {sent_count} exitosos, {failed_count} fallidos")
        
        return jsonify({
            'status': 'success',
            'sent': sent_count,
            'failed': failed_count,
            'message': f'Alertas enviadas a {sent_count} destinatarios',
            'severity': severity,
            'alert_name': alert_name
        })
        
    except Exception as e:
        logger.error(f"❌ Error procesando alerta: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send', methods=['POST'])
def send_simple_email():
    """Endpoint para envío simple de emails"""
    try:
        data = request.get_json()
        
        to_email = data.get('to_email')
        subject = data.get('subject', 'OptiMon Notification')
        message = data.get('message', '')
        
        if not to_email:
            return jsonify({'error': 'to_email required'}), 400
        
        # Si el mensaje no es HTML, convertirlo
        if not message.strip().startswith('<'):
            message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #495057;">OptiMon Notification</h2>
                    <div style="background-color: white; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff;">
                        {message}
                    </div>
                    <div style="margin-top: 20px; font-size: 12px; color: #6c757d; text-align: center;">
                        OptiMon Sistema Unificado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
            </body>
            </html>
            """
        
        success = send_email(to_email, subject, message)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email enviado correctamente a {to_email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error enviando email'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error en envío simple: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/config', methods=['GET', 'POST'])
def email_config():
    """Configuración del servicio email"""
    if request.method == 'GET':
        return jsonify({
            'smtp_host': SMTP_CONFIG['host'],
            'smtp_port': SMTP_CONFIG['port'],
            'smtp_username': SMTP_CONFIG['username'],
            'smtp_configured': bool(SMTP_CONFIG['username'] and SMTP_CONFIG['password']),
            'recipients': load_email_recipients()
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Actualizar configuración SMTP global
            if 'smtp' in data:
                for key, value in data['smtp'].items():
                    if key in SMTP_CONFIG:
                        SMTP_CONFIG[key] = value
            
            # Guardar destinatarios
            if 'recipients' in data:
                config_path = Path('config/email_recipients.json')
                config_path.parent.mkdir(exist_ok=True)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'recipients': [{'email': email, 'active': True} for email in data['recipients']],
                        'updated': datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'message': 'Configuración actualizada correctamente'
            })
            
        except Exception as e:
            logger.error(f"❌ Error actualizando configuración: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

def check_smtp_configuration():
    """Verificar configuración SMTP antes de iniciar"""
    if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
        logger.error("❌ Configuración SMTP incompleta")
        logger.error("   Configure SMTP_USERNAME y SMTP_PASSWORD")
        return False
    
    logger.info("✅ Configuración SMTP verificada")
    logger.info(f"   Host: {SMTP_CONFIG['host']}:{SMTP_CONFIG['port']}")
    logger.info(f"   Usuario: {SMTP_CONFIG['username']}")
    logger.info(f"   TLS: {'Habilitado' if SMTP_CONFIG['use_tls'] else 'Deshabilitado'}")
    
    return True

# ===== PUNTO DE ENTRADA =====

if __name__ == '__main__':
    logger.info("🚀 Iniciando OptiMon Email Service Unificado...")
    logger.info("📧 Versión: 3.0.0-UNIFIED")
    logger.info("🌐 Puerto: 5555")
    logger.info("=" * 60)
    
    if check_smtp_configuration():
        recipients = load_email_recipients()
        logger.info(f"📋 Destinatarios configurados: {len(recipients)}")
        for recipient in recipients:
            logger.info(f"   📧 {recipient}")
        
        logger.info(f"\n🚀 Iniciando servidor en http://localhost:5555")
        app.run(host='0.0.0.0', port=5555, debug=False)
    else:
        logger.error("\n❌ Servicio NO iniciado debido a configuración incompleta")
        logger.error("   Configure las variables SMTP y vuelva a intentar")