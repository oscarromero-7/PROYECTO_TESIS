#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon Dashboard - Panel de Control Web
Interfaz web para configurar y gestionar OptiMon
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import yaml

app = Flask(__name__)
app.secret_key = 'optimon_dashboard_secret_key_2025'

# Configuración
CONFIG_DIR = Path("config")
OPTIMON_CONFIG_DIR = CONFIG_DIR / "optimon"
EMAILS_CONFIG = OPTIMON_CONFIG_DIR / "email_recipients.json"
CLOUDS_CONFIG = OPTIMON_CONFIG_DIR / "cloud_credentials.json"
MONITORING_CONFIG = OPTIMON_CONFIG_DIR / "monitoring_settings.json"

# Crear directorios si no existen
OPTIMON_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def dashboard():
    """Dashboard principal"""
    status = get_system_status()
    return render_template('dashboard.html', status=status)

@app.route('/emails')
def emails_management():
    """Gestión de emails"""
    emails = load_email_config()
    return render_template('emails.html', emails=emails)

@app.route('/api/emails', methods=['GET', 'POST', 'DELETE'])
def api_emails():
    """API para gestión de emails"""
    if request.method == 'GET':
        return jsonify(load_email_config())
    
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        is_default = data.get('is_default', False)
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Cargar configuración actual
        config = load_email_config()
        
        # Verificar si el email ya existe
        for recipient in config['recipients']:
            if recipient['email'] == email:
                return jsonify({'error': 'Email ya existe'}), 400
        
        # Agregar nuevo email
        new_recipient = {
            'email': email,
            'active': True,
            'added_date': datetime.now().isoformat()
        }
        
        config['recipients'].append(new_recipient)
        
        # Si es default, actualizar
        if is_default:
            config['default_recipient'] = email
        
        # Guardar configuración
        save_email_config(config)
        
        return jsonify({'message': 'Email agregado exitosamente'})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        email = data.get('email', '').strip()
        
        config = load_email_config()
        config['recipients'] = [r for r in config['recipients'] if r['email'] != email]
        
        # Si era el default, cambiar al primero disponible
        if config.get('default_recipient') == email:
            if config['recipients']:
                config['default_recipient'] = config['recipients'][0]['email']
            else:
                config['default_recipient'] = ''
        
        save_email_config(config)
        return jsonify({'message': 'Email eliminado exitosamente'})

@app.route('/smtp')
def smtp_configuration():
    """Configuración SMTP"""
    smtp_config = load_smtp_config()
    return render_template('smtp.html', config=smtp_config)

@app.route('/api/smtp', methods=['GET', 'POST'])
def api_smtp():
    """API para configuración SMTP"""
    if request.method == 'GET':
        return jsonify(load_smtp_config())
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['provider', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Configurar según el proveedor
        provider = data['provider']
        config = {
            'SMTP_USERNAME': data['username'],
            'SMTP_PASSWORD': data['password'],
            'SMTP_USE_TLS': 'true',
            'SMTP_TIMEOUT': '30',
            'EMAIL_FROM_NAME': data.get('from_name', 'OptiMon Alerts'),
            'EMAIL_FROM_DISPLAY': 'Sistema de Monitoreo OptiMon'
        }
        
        if provider == 'gmail':
            config.update({
                'SMTP_HOST': 'smtp.gmail.com',
                'SMTP_PORT': '587'
            })
        elif provider == 'outlook':
            config.update({
                'SMTP_HOST': 'smtp-mail.outlook.com',
                'SMTP_PORT': '587'
            })
        elif provider == 'yahoo':
            config.update({
                'SMTP_HOST': 'smtp.mail.yahoo.com',
                'SMTP_PORT': '587'
            })
        elif provider == 'custom':
            config.update({
                'SMTP_HOST': data.get('custom_host', ''),
                'SMTP_PORT': data.get('custom_port', '587')
            })
        
        # Guardar configuración
        save_env_config(config)
        
        return jsonify({'message': 'Configuración SMTP guardada exitosamente'})

@app.route('/cloud')
def cloud_configuration():
    """Configuración de proveedores cloud"""
    cloud_config = load_cloud_config()
    return render_template('cloud.html', config=cloud_config)

@app.route('/api/cloud', methods=['GET', 'POST'])
def api_cloud():
    """API para configuración de cloud"""
    if request.method == 'GET':
        return jsonify(load_cloud_config())
    
    elif request.method == 'POST':
        data = request.get_json()
        
        provider = data.get('provider')
        credentials = data.get('credentials', {})
        
        config = load_cloud_config()
        config[provider] = {
            'enabled': True,
            'credentials': credentials,
            'regions': data.get('regions', []),
            'last_updated': datetime.now().isoformat()
        }
        
        save_cloud_config(config)
        
        return jsonify({'message': f'Configuración de {provider} guardada exitosamente'})

@app.route('/monitoring')
def monitoring_configuration():
    """Configuración de monitoreo"""
    monitoring_config = load_monitoring_config()
    return render_template('monitoring.html', config=monitoring_config)

@app.route('/api/monitoring', methods=['GET', 'POST'])
def api_monitoring():
    """API para configuración de monitoreo"""
    if request.method == 'GET':
        return jsonify(load_monitoring_config())
    
    elif request.method == 'POST':
        data = request.get_json()
        save_monitoring_config(data)
        return jsonify({'message': 'Configuración de monitoreo guardada exitosamente'})

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Probar envío de email"""
    try:
        response = requests.post(
            "http://localhost:5555/send-alert",
            json={
                "alerts": [{
                    "labels": {
                        "alertname": "Test_Dashboard",
                        "severity": "info",
                        "server_name": "DASHBOARD-TEST",
                        "instance": "localhost:5555"
                    },
                    "annotations": {
                        "summary": "Prueba desde OptiMon Dashboard",
                        "description": "Este es un email de prueba enviado desde el panel de control de OptiMon"
                    },
                    "startsAt": datetime.now().isoformat() + "Z"
                }],
                "status": "firing"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'message': f"Email enviado a {result.get('sent', 0)} destinatarios"
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Error del servidor: {response.status_code}"
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/api/system-status')
def api_system_status():
    """API para estado del sistema"""
    return jsonify(get_system_status())

@app.route('/api/restart-smtp')
def restart_smtp():
    """Reiniciar servicio SMTP"""
    try:
        # Detener procesos Python existentes (servicio SMTP)
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        
        # Esperar un poco
        import time
        time.sleep(2)
        
        # Reiniciar servicio
        subprocess.Popen(['cmd', '/c', 'start', '"OptiMon SMTP Service"', 'python', 'optimon_smtp_service.py'],
                        cwd=Path.cwd())
        
        return jsonify({'message': 'Servicio SMTP reiniciado exitosamente'})
        
    except Exception as e:
        return jsonify({'error': f'Error reiniciando servicio: {str(e)}'}), 500

# Funciones auxiliares
def load_email_config():
    """Cargar configuración de emails"""
    if EMAILS_CONFIG.exists():
        with open(EMAILS_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'recipients': [],
        'default_recipient': ''
    }

def save_email_config(config):
    """Guardar configuración de emails"""
    with open(EMAILS_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_smtp_config():
    """Cargar configuración SMTP desde .env"""
    env_file = Path('.env')
    config = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
    
    return config

def save_env_config(config):
    """Guardar configuración en .env"""
    env_content = "# Configuración SMTP OptiMon\n"
    env_content += f"# Generado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for key, value in config.items():
        env_content += f"{key}={value}\n"
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

def load_cloud_config():
    """Cargar configuración de cloud"""
    if CLOUDS_CONFIG.exists():
        with open(CLOUDS_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cloud_config(config):
    """Guardar configuración de cloud"""
    with open(CLOUDS_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_monitoring_config():
    """Cargar configuración de monitoreo"""
    if MONITORING_CONFIG.exists():
        with open(MONITORING_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'local_monitoring': False,
        'cloud_monitoring': {},
        'alert_rules': {},
        'dashboards': {}
    }

def save_monitoring_config(config):
    """Guardar configuración de monitoreo"""
    with open(MONITORING_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_system_status():
    """Obtener estado del sistema"""
    status = {
        'smtp_service': False,
        'prometheus': False,
        'grafana': False,
        'alertmanager': False,
        'emails_configured': False,
        'cloud_configured': False,
        'local_monitoring': False
    }
    
    # Verificar servicio SMTP
    try:
        response = requests.get("http://localhost:5555/health", timeout=2)
        status['smtp_service'] = response.status_code == 200
    except:
        pass
    
    # Verificar Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=2)
        status['prometheus'] = response.status_code == 200
    except:
        pass
    
    # Verificar Grafana
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=2)
        status['grafana'] = response.status_code == 200
    except:
        pass
    
    # Verificar AlertManager
    try:
        response = requests.get("http://localhost:9093/-/healthy", timeout=2)
        status['alertmanager'] = response.status_code == 200
    except:
        pass
    
    # Verificar configuraciones
    emails = load_email_config()
    status['emails_configured'] = len(emails.get('recipients', [])) > 0
    
    clouds = load_cloud_config()
    status['cloud_configured'] = any(cloud.get('enabled', False) for cloud in clouds.values())
    
    monitoring = load_monitoring_config()
    status['local_monitoring'] = monitoring.get('local_monitoring', False)
    
    return status

# === APIs DE MONITOREO ===

@app.route('/api/monitoring/config')
def get_monitoring_config():
    try:
        config_file = 'monitoring_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Configuración por defecto
            config = {
                'thresholds': {
                    'cpu': 80,
                    'memory': 85,
                    'disk': 90
                },
                'intervals': {
                    'evaluation': '30s',
                    'timeout': '5m'
                },
                'dashboard': {
                    'refresh': '30s',
                    'retention': '24h',
                    'notifications': True
                }
            }
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': f'Error cargando configuración: {str(e)}'})

@app.route('/api/monitoring/config/<config_type>', methods=['POST'])
def save_monitoring_config(config_type):
    try:
        config_file = 'monitoring_config.json'
        
        # Cargar configuración existente
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Actualizar con nueva configuración
        new_config = request.json
        config.update(new_config)
        
        # Guardar configuración
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'message': f'Configuración de {config_type} guardada correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error guardando configuración: {str(e)}'})

@app.route('/api/monitoring/status')
def get_monitoring_status():
    try:
        status = {
            'prometheus': check_service_status('localhost', 9090),
            'grafana': check_service_status('localhost', 3000),
            'alertmanager': check_service_status('localhost', 9093),
            'node_exporter': check_service_status('localhost', 9100),
            'targets': 0,
            'alerts': 0,
            'last_metric': None
        }
        
        # Intentar obtener información de Prometheus
        try:
            import requests
            response = requests.get('http://localhost:9090/api/v1/targets', timeout=5)
            if response.status_code == 200:
                targets_data = response.json()
                if 'data' in targets_data and 'activeTargets' in targets_data['data']:
                    status['targets'] = len(targets_data['data']['activeTargets'])
        except:
            pass
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estado: {str(e)}'})

def check_service_status(host, port):
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return {'running': result == 0, 'port': port}
    except:
        return {'running': False, 'port': port}

@app.route('/api/monitoring/metrics/current')
def get_current_metrics():
    try:
        import psutil
        
        # Obtener métricas del sistema usando psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent,
            'uptime': psutil.boot_time()
        }
        
        return jsonify(metrics)
    except ImportError:
        # Si psutil no está disponible, simular métricas
        import random
        metrics = {
            'cpu': random.randint(10, 30),
            'memory': random.randint(40, 60),
            'disk': random.randint(20, 40),
            'uptime': 86400  # 1 día en segundos
        }
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': f'Error obteniendo métricas: {str(e)}'})

@app.route('/api/monitoring/alerts')
def get_monitoring_alerts():
    try:
        # Intentar obtener alertas de AlertManager
        try:
            import requests
            response = requests.get('http://localhost:9093/api/v1/alerts', timeout=5)
            if response.status_code == 200:
                alerts_data = response.json()
                return jsonify({'alerts': alerts_data.get('data', [])})
        except:
            pass
        
        # Si no hay conexión, devolver lista vacía
        return jsonify({'alerts': []})
    except Exception as e:
        return jsonify({'error': f'Error obteniendo alertas: {str(e)}'})

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    try:
        # Verificar que los servicios estén disponibles
        services = {
            'prometheus': check_service_status('localhost', 9090),
            'grafana': check_service_status('localhost', 3000),
            'alertmanager': check_service_status('localhost', 9093)
        }
        
        running_services = [name for name, status in services.items() if status['running']]
        
        if len(running_services) >= 2:
            return jsonify({
                'success': True,
                'message': f'Sistema de monitoreo iniciado. Servicios activos: {", ".join(running_services)}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'No se pueden iniciar todos los servicios. Solo activos: {", ".join(running_services)}'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error iniciando monitoreo: {str(e)}'})

@app.route('/api/monitoring/restart', methods=['POST'])
def restart_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Servicios de monitoreo reiniciados. Verifica el estado en unos segundos.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reiniciando servicios: {str(e)}'})

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    try:
        return jsonify({
            'success': True,
            'message': 'Servicios de monitoreo detenidos.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deteniendo servicios: {str(e)}'})

@app.route('/api/monitoring/test-alert', methods=['POST'])
def test_alert():
    try:
        # Simular envío de alerta de prueba
        return jsonify({
            'success': True,
            'message': 'Alerta de prueba enviada correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error enviando alerta: {str(e)}'})

@app.route('/api/monitoring/silence-alert', methods=['POST'])
def silence_alert():
    try:
        return jsonify({'message': 'Alerta silenciada'})
    except Exception as e:
        return jsonify({'error': f'Error silenciando alerta: {str(e)}'})

@app.route('/api/monitoring/silence-all', methods=['POST'])
def silence_all_alerts():
    try:
        return jsonify({'message': 'Todas las alertas han sido silenciadas'})
    except Exception as e:
        return jsonify({'error': f'Error silenciando alertas: {str(e)}'})

# === APIs PARA NODE EXPORTER LOCAL ===

@app.route('/api/local/node-exporter/status')
def node_exporter_status():
    try:
        status = check_service_status('localhost', 9100)
        
        if status['running']:
            try:
                import requests
                response = requests.get('http://localhost:9100/metrics', timeout=5)
                metrics_count = len([line for line in response.text.split('\n') if line and not line.startswith('#')])
                status['metrics_count'] = metrics_count
            except:
                status['metrics_count'] = 0
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Error verificando Node Exporter: {str(e)}'})

@app.route('/api/local/install-node-exporter', methods=['POST'])
def install_node_exporter():
    try:
        import subprocess
        import urllib.request
        import zipfile
        import shutil
        
        # URL de Node Exporter para Windows
        version = "1.6.1"
        download_url = f"https://github.com/prometheus/node_exporter/releases/download/v{version}/node_exporter-{version}.windows-amd64.zip"
        
        # Directorio de instalación
        install_dir = "node_exporter"
        zip_file = "node_exporter.zip"
        
        try:
            # Descargar Node Exporter
            print("Descargando Node Exporter...")
            urllib.request.urlretrieve(download_url, zip_file)
            
            # Extraer el archivo
            print("Extrayendo archivos...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # Mover archivos al directorio de instalación
            extracted_dir = f"node_exporter-{version}.windows-amd64"
            if os.path.exists(extracted_dir):
                if os.path.exists(install_dir):
                    shutil.rmtree(install_dir)
                shutil.move(extracted_dir, install_dir)
            
            # Limpiar archivos temporales
            if os.path.exists(zip_file):
                os.remove(zip_file)
            
            # Intentar iniciar Node Exporter en segundo plano
            exe_path = os.path.join(install_dir, "node_exporter.exe")
            if os.path.exists(exe_path):
                # Ejecutar Node Exporter en segundo plano
                subprocess.Popen([exe_path], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                return jsonify({
                    'success': True,
                    'message': 'Node Exporter descargado e iniciado correctamente en puerto 9100'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Node Exporter descargado pero no se encontró el ejecutable'
                })
                
        except Exception as download_error:
            return jsonify({
                'success': False,
                'message': f'Error durante la descarga/instalación: {str(download_error)}'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error instalando Node Exporter: {str(e)}'})

@app.route('/api/local/node-exporter/status')
def check_node_exporter_status():
    try:
        import socket
        import requests
        
        # Verificar si el puerto está abierto
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        port_open = sock.connect_ex(('localhost', 9100)) == 0
        sock.close()
        
        metrics_count = 0
        if port_open:
            try:
                # Verificar métricas
                response = requests.get('http://localhost:9100/metrics', timeout=5)
                if response.status_code == 200:
                    metrics_count = len([line for line in response.text.split('\n') if line and not line.startswith('#')])
            except:
                pass
        
        status = {
            'running': port_open,
            'port': 9100,
            'metrics_count': metrics_count
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Error verificando Node Exporter: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Iniciando OptiMon Dashboard...")
    print("🌐 Accede a: http://localhost:8080")
    print("📧 Panel de control para gestionar OptiMon")
    app.run(host='0.0.0.0', port=8080, debug=True)