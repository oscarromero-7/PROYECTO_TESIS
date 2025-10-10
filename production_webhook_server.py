#!/usr/bin/env python3
"""
OptiMon - Webhook Receiver para Alertas Críticas de Producción
Sistema para recibir y procesar alertas críticas de AWS/Azure/Physical servers
"""

from flask import Flask, request, jsonify
import json
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_alerts.log'),
        logging.StreamHandler()
    ]
)

class ProductionAlertWebhook:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Configuración de webhooks (configurar según necesidades)
        self.webhook_config = {
            "slack": {
                "enabled": False,
                "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#alerts-production",
                "username": "OptiMon Alert Bot"
            },
            "teams": {
                "enabled": False,
                "url": "https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK"
            },
            "discord": {
                "enabled": False,
                "url": "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
            },
            "custom": {
                "enabled": True,
                "log_file": "production_alerts.log"
            }
        }
    
    def format_slack_message(self, alerts):
        """Formatear mensaje para Slack"""
        message = {
            "channel": self.webhook_config["slack"]["channel"],
            "username": self.webhook_config["slack"]["username"],
            "icon_emoji": ":rotating_light:",
            "attachments": []
        }
        
        for alert in alerts:
            color = "danger" if alert.get("labels", {}).get("severity") == "critical" else "warning"
            
            attachment = {
                "color": color,
                "title": f"🚨 {alert.get('labels', {}).get('alertname', 'Unknown Alert')}",
                "title_link": "http://localhost:3000",
                "fields": [
                    {
                        "title": "Servidor",
                        "value": alert.get("labels", {}).get("server_name", "Unknown"),
                        "short": True
                    },
                    {
                        "title": "Instancia",
                        "value": alert.get("labels", {}).get("instance", "Unknown"),
                        "short": True
                    },
                    {
                        "title": "Severidad",
                        "value": alert.get("labels", {}).get("severity", "Unknown").upper(),
                        "short": True
                    },
                    {
                        "title": "Tipo",
                        "value": alert.get("labels", {}).get("server_type", "Unknown").upper(),
                        "short": True
                    },
                    {
                        "title": "Descripción",
                        "value": alert.get("annotations", {}).get("description", "No description"),
                        "short": False
                    }
                ],
                "footer": "OptiMon Alert System",
                "ts": int(datetime.now().timestamp())
            }
            
            message["attachments"].append(attachment)
        
        return message
    
    def format_teams_message(self, alerts):
        """Formatear mensaje para Microsoft Teams"""
        sections = []
        
        for alert in alerts:
            severity = alert.get("labels", {}).get("severity", "unknown")
            color = "FF0000" if severity == "critical" else "FFA500"
            
            section = {
                "activityTitle": f"🚨 {alert.get('labels', {}).get('alertname', 'Unknown Alert')}",
                "activitySubtitle": f"Servidor: {alert.get('labels', {}).get('server_name', 'Unknown')}",
                "activityImage": "https://img.icons8.com/color/48/000000/error.png",
                "facts": [
                    {"name": "Instancia", "value": alert.get("labels", {}).get("instance", "Unknown")},
                    {"name": "Severidad", "value": severity.upper()},
                    {"name": "Tipo", "value": alert.get("labels", {}).get("server_type", "Unknown").upper()},
                    {"name": "Descripción", "value": alert.get("annotations", {}).get("description", "No description")}
                ],
                "markdown": True
            }
            
            sections.append(section)
        
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000" if any(a.get("labels", {}).get("severity") == "critical" for a in alerts) else "FFA500",
            "summary": f"OptiMon: {len(alerts)} alertas de producción",
            "sections": sections,
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Ver Dashboard",
                    "targets": [{"os": "default", "uri": "http://localhost:3000"}]
                },
                {
                    "@type": "OpenUri", 
                    "name": "Gestionar Alertas",
                    "targets": [{"os": "default", "uri": "http://localhost:9093"}]
                }
            ]
        }
        
        return message
    
    def send_slack_notification(self, alerts):
        """Enviar notificación a Slack"""
        if not self.webhook_config["slack"]["enabled"]:
            return False
        
        try:
            message = self.format_slack_message(alerts)
            response = requests.post(
                self.webhook_config["slack"]["url"],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Alerta enviada a Slack: {len(alerts)} alertas")
                return True
            else:
                logging.error(f"Error enviando a Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando notificación a Slack: {e}")
            return False
    
    def send_teams_notification(self, alerts):
        """Enviar notificación a Microsoft Teams"""
        if not self.webhook_config["teams"]["enabled"]:
            return False
        
        try:
            message = self.format_teams_message(alerts)
            response = requests.post(
                self.webhook_config["teams"]["url"],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Alerta enviada a Teams: {len(alerts)} alertas")
                return True
            else:
                logging.error(f"Error enviando a Teams: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando notificación a Teams: {e}")
            return False
    
    def log_production_alert(self, alerts):
        """Registrar alerta de producción en log"""
        if not self.webhook_config["custom"]["enabled"]:
            return
        
        log_file = self.webhook_config["custom"]["log_file"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"ALERTA DE PRODUCCIÓN - {timestamp}\n")
                f.write(f"{'='*80}\n")
                
                for alert in alerts:
                    labels = alert.get("labels", {})
                    annotations = alert.get("annotations", {})
                    
                    f.write(f"ALERTA: {labels.get('alertname', 'Unknown')}\n")
                    f.write(f"SERVIDOR: {labels.get('server_name', 'Unknown')}\n")
                    f.write(f"INSTANCIA: {labels.get('instance', 'Unknown')}\n")
                    f.write(f"TIPO: {labels.get('server_type', 'Unknown').upper()}\n")
                    f.write(f"SEVERIDAD: {labels.get('severity', 'Unknown').upper()}\n")
                    f.write(f"RESUMEN: {annotations.get('summary', 'No summary')}\n")
                    f.write(f"DESCRIPCIÓN: {annotations.get('description', 'No description')}\n")
                    f.write(f"ESTADO: {alert.get('status', 'Unknown')}\n")
                    f.write(f"{'-'*40}\n")
                
                f.write(f"\n")
            
            logging.info(f"Alerta de producción registrada: {len(alerts)} alertas")
            
        except Exception as e:
            logging.error(f"Error registrando alerta: {e}")

webhook_manager = ProductionAlertWebhook()

@app.route('/webhook/production-critical', methods=['POST'])
def production_critical_webhook():
    """Endpoint para alertas críticas de producción"""
    try:
        data = request.json
        alerts = data.get('alerts', [])
        
        # Filtrar solo alertas de producción (no Windows)
        production_alerts = [
            alert for alert in alerts 
            if alert.get('labels', {}).get('server_type') in ['aws', 'azure', 'linux_physical']
        ]
        
        if not production_alerts:
            return jsonify({"status": "ok", "message": "No production alerts"}), 200
        
        logging.info(f"Recibidas {len(production_alerts)} alertas críticas de producción")
        
        # Procesar alertas
        webhook_manager.log_production_alert(production_alerts)
        
        # Enviar a Slack si está habilitado
        webhook_manager.send_slack_notification(production_alerts)
        
        # Enviar a Teams si está habilitado
        webhook_manager.send_teams_notification(production_alerts)
        
        return jsonify({
            "status": "ok", 
            "message": f"Processed {len(production_alerts)} production alerts"
        }), 200
        
    except Exception as e:
        logging.error(f"Error procesando webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook/test', methods=['POST', 'GET'])
def test_webhook():
    """Endpoint de prueba"""
    test_alert = {
        "alerts": [{
            "labels": {
                "alertname": "TestAlert",
                "server_name": "Test-Server",
                "instance": "test.example.com:9100",
                "server_type": "aws",
                "severity": "critical"
            },
            "annotations": {
                "summary": "Esta es una alerta de prueba",
                "description": "Prueba del sistema de webhooks de OptiMon"
            },
            "status": "firing"
        }]
    }
    
    webhook_manager.log_production_alert(test_alert["alerts"])
    
    return jsonify({
        "status": "ok", 
        "message": "Test alert processed successfully"
    }), 200

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """Estado del sistema de webhooks"""
    return jsonify({
        "status": "running",
        "config": {
            "slack_enabled": webhook_manager.webhook_config["slack"]["enabled"],
            "teams_enabled": webhook_manager.webhook_config["teams"]["enabled"],
            "custom_log_enabled": webhook_manager.webhook_config["custom"]["enabled"]
        },
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("Iniciando Webhook Receiver para Alertas de Producción...")
    print("Endpoints disponibles:")
    print("  POST /webhook/production-critical - Alertas críticas de producción")
    print("  GET/POST /webhook/test - Prueba del sistema")
    print("  GET /webhook/status - Estado del sistema")
    print("\nPara configurar Slack/Teams, edita webhook_config en el código")
    
    app.run(host='0.0.0.0', port=8080, debug=False)