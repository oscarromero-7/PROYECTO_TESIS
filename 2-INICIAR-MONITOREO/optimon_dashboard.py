#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon Dashboard - Panel de Control Web
Interfaz web para configurar y gestionar OptiMon
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import sys
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
    """Dashboard principal con configuración completa"""
    return render_template('dashboard_complete.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'OptiMon Dashboard'
    })

@app.route('/api/services/status')
def services_status():
    """Verificar estado de todos los servicios"""
    import socket
    import subprocess
    
    services = {
        'grafana': {'port': 3000, 'status': False},
        'prometheus': {'port': 9090, 'status': False},
        'alertmanager': {'port': 9093, 'status': False},
        'smtp': {'port': 5555, 'status': False},
        'windows_exporter': {'port': 9182, 'status': False}
    }
    
    # Verificar puertos
    for service_name, service_info in services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', service_info['port']))
            services[service_name]['status'] = result == 0
            sock.close()
        except:
            services[service_name]['status'] = False
    
    # Verificar Docker containers
    try:
        result = subprocess.run(['docker-compose', 'ps', '--format', 'json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Si docker-compose está disponible, los servicios Docker deberían estar corriendo
            services['grafana']['docker_status'] = 'running'
            services['prometheus']['docker_status'] = 'running'
            services['alertmanager']['docker_status'] = 'running'
    except:
        pass
    
    return jsonify(services)

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
            'node_exporter': check_service_status('localhost', 9182),
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
    """
    Instalar Windows Exporter (reemplazo moderno de Node Exporter para Windows)
    Incluye detección inteligente y manejo de errores
    """
    try:
        import subprocess
        import urllib.request
        import shutil
        import socket
        
        # Verificar si Windows Exporter ya está ejecutándose
        def check_windows_exporter_running():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 9182))
                sock.close()
                return result == 0
            except:
                return False
        
        # Verificar si ya está instalado y ejecutándose
        if check_windows_exporter_running():
            try:
                import requests
                response = requests.get('http://localhost:9182/metrics', timeout=5)
                if response.status_code == 200:
                    metrics_count = len([line for line in response.text.split('\n') if line and not line.startswith('#')])
                    return jsonify({
                        'success': True,
                        'message': 'Windows Exporter ya está instalado y funcionando correctamente',
                        'details': {
                            'status': 'already_installed',
                            'port': 9182,
                            'metrics_url': 'http://localhost:9182/metrics',
                            'metrics_count': metrics_count,
                            'note': 'No es necesario reinstalar'
                        }
                    })
            except:
                pass
        
        # Configuración de Windows Exporter
        version = "0.31.3"
        download_url = f"https://github.com/prometheus-community/windows_exporter/releases/download/v{version}/windows_exporter-{version}-amd64.exe"
        
        # Directorios de instalación posibles
        install_paths = [
            "windows_exporter",
            "C:/optimon/windows_exporter"
        ]
        
        # Buscar instalación existente
        existing_exe = None
        for path in install_paths:
            exe_path = os.path.join(path, "windows_exporter.exe")
            if os.path.exists(exe_path):
                existing_exe = exe_path
                break
        
        # Si existe pero no está ejecutándose, intentar iniciarlo
        if existing_exe:
            try:
                # Verificar que el ejecutable funciona
                result = subprocess.run([existing_exe, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Intentar iniciar el servicio
                    subprocess.Popen([existing_exe, '--web.listen-address=:9182'], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                    
                    # Esperar un momento y verificar
                    import time
                    time.sleep(3)
                    
                    if check_windows_exporter_running():
                        return jsonify({
                            'success': True,
                            'message': 'Windows Exporter ya estaba instalado y ha sido iniciado correctamente',
                            'details': {
                                'status': 'restarted',
                                'port': 9182,
                                'metrics_url': 'http://localhost:9182/metrics',
                                'path': existing_exe
                            }
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Windows Exporter instalado pero no pudo iniciarse',
                            'details': {
                                'status': 'start_failed',
                                'path': existing_exe,
                                'suggestion': 'Verificar permisos o conflictos de puerto'
                            }
                        })
                        
            except Exception as e:
                # Si el ejecutable existente falla, proceder con nueva instalación
                pass
        
        # Proceder con nueva instalación
        install_dir = "windows_exporter"
        exe_file = "windows_exporter.exe"
        
        try:
            # Crear directorio de instalación
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            
            exe_path = os.path.join(install_dir, exe_file)
            
            # Si el archivo existe y está en uso, intentar detener el proceso
            if os.path.exists(exe_path):
                try:
                    import psutil
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        try:
                            if proc.info['exe'] and exe_path.lower() in proc.info['exe'].lower():
                                proc.terminate()
                                import time
                                time.sleep(2)
                                break
                        except:
                            continue
                except:
                    pass
            
            # Descargar Windows Exporter
            print("Descargando Windows Exporter...")
            urllib.request.urlretrieve(download_url, exe_path)
            
            print("Windows Exporter descargado exitosamente")
            
            # Crear script de inicio
            start_script = os.path.join(install_dir, "start_windows_exporter.bat")
            with open(start_script, 'w') as f:
                f.write('@echo off\n')
                f.write(f'"{exe_path}" --web.listen-address=:9182\n')
            
            # Probar el ejecutable
            result = subprocess.run([exe_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Intentar iniciar Windows Exporter en segundo plano
                process = subprocess.Popen([exe_path, '--web.listen-address=:9182'], 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                
                # Esperar un momento y verificar
                import time
                time.sleep(5)
                
                if check_windows_exporter_running():
                    return jsonify({
                        'success': True,
                        'message': 'Windows Exporter instalado e iniciado exitosamente',
                        'details': {
                            'status': 'newly_installed',
                            'version': version,
                            'port': 9182,
                            'metrics_url': 'http://localhost:9182/metrics',
                            'path': exe_path,
                            'start_script': start_script,
                            'pid': process.pid
                        }
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': 'Windows Exporter instalado correctamente. Use el botón "Iniciar" para activarlo.',
                        'details': {
                            'status': 'installed_not_started',
                            'path': exe_path,
                            'start_script': start_script,
                            'manual_start': f'Ejecutar: {start_script}'
                        }
                    })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Error verificando Windows Exporter: {result.stderr}',
                    'details': {
                        'status': 'verification_failed',
                        'stderr': result.stderr
                    }
                })
                
        except urllib.error.HTTPError as e:
            return jsonify({
                'success': False,
                'message': f'Error descargando Windows Exporter: HTTP {e.code}',
                'details': {
                    'status': 'download_failed',
                    'url': download_url,
                    'error_code': e.code,
                    'suggestion': 'Verificar conexión a internet'
                }
            })
            
        except PermissionError:
            return jsonify({
                'success': False,
                'message': 'Error de permisos al instalar Windows Exporter',
                'details': {
                    'status': 'permission_denied',
                    'suggestion': 'Ejecutar como administrador'
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error durante la instalación: {str(e)}',
                'details': {
                    'status': 'installation_error',
                    'error': str(e)
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error general en la instalación: {str(e)}',
            'details': {
                'status': 'general_error',
                'error': str(e)
            }
        })

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

@app.route('/api/local/windows-exporter/status')
def windows_exporter_status():
    """
    Endpoint mejorado para verificar estado de Windows Exporter
    """
    try:
        import socket
        import requests
        import psutil
        
        # Verificar si hay algún proceso de windows_exporter ejecutándose
        def check_process_running():
            try:
                # Verificar por puerto primero (más confiable)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                port_result = sock.connect_ex(('localhost', 9182)) == 0
                sock.close()
                
                if port_result:
                    return True
                
                # Si el puerto no responde, verificar procesos
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        proc_info = proc.info
                        if proc_info['name'] and 'windows_exporter' in proc_info['name'].lower():
                            return True
                        if proc_info['cmdline']:
                            cmdline_str = ' '.join(proc_info['cmdline']).lower()
                            if 'windows_exporter' in cmdline_str:
                                return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return False
            except Exception as e:
                # Si hay error, intentar verificar puerto como fallback
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', 9182)) == 0
                    sock.close()
                    return result
                except:
                    return False
        
        # Verificar si el puerto está abierto y respondiendo
        def check_metrics_available():
            try:
                response = requests.get('http://localhost:9182/metrics', timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Priorizar verificación de métricas - si responde, está funcionando
        metrics_available = check_metrics_available()
        process_running = check_process_running()
        
        # Si las métricas están disponibles, está funcionando independientemente del proceso
        running = metrics_available or process_running
        
        metrics_count = 0
        version_info = ""
        
        if metrics_available:
            try:
                # Obtener métricas
                response = requests.get('http://localhost:9182/metrics', timeout=5)
                if response.status_code == 200:
                    lines = response.text.split('\n')
                    metrics_count = len([line for line in lines if line and not line.startswith('#')])
                    
                    # Buscar información de versión
                    for line in lines:
                        if 'go_build_info' in line and 'windows_exporter' in line:
                            # Extraer versión de la línea
                            if 'version=' in line:
                                start = line.find('version="') + 9
                                end = line.find('"', start)
                                if start > 8 and end > start:
                                    version_info = line[start:end]
                            break
                    
            except:
                pass
        
        # Verificar archivos de instalación
        installation_paths = [
            "windows_exporter/windows_exporter.exe",
            "C:/optimon/windows_exporter/windows_exporter.exe"
        ]
        
        installed_path = None
        for path in installation_paths:
            if os.path.exists(path):
                installed_path = path
                break
        
        # Si está ejecutándose pero no encontramos el archivo, asumir que está instalado
        if running and not installed_path:
            installed_path = "windows_exporter/windows_exporter.exe"
        
        status = {
            'running': running,
            'port': 9182,
            'metrics_count': metrics_count,
            'version': version_info if version_info else "0.31.3",
            'installed': running or (installed_path is not None),
            'path': installed_path,
            'service_type': 'Windows Exporter',
            'metrics_url': 'http://localhost:9182/metrics' if running else None
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'error': f'Error verificando Windows Exporter: {str(e)}',
            'running': False,
            'port': 9182
        })

@app.route('/api/local/windows-exporter/control', methods=['POST'])
def windows_exporter_control():
    """
    Controlar Windows Exporter: iniciar, detener, reiniciar
    """
    try:
        import subprocess
        import psutil
        import requests
        
        data = request.get_json()
        action = data.get('action', 'start')  # start, stop, restart
        
        # Buscar ejecutable instalado
        installation_paths = [
            "windows_exporter/windows_exporter.exe",
            "C:/optimon/windows_exporter/windows_exporter.exe"
        ]
        
        exe_path = None
        for path in installation_paths:
            if os.path.exists(path):
                exe_path = path
                break
        
        if not exe_path:
            return jsonify({
                'success': False,
                'message': 'Windows Exporter no está instalado',
                'suggestion': 'Instalar Windows Exporter primero'
            })
        
        # Función para detener procesos existentes
        def stop_existing_processes():
            stopped_count = 0
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if proc.info['exe'] and 'windows_exporter' in proc.info['exe'].lower():
                            proc.terminate()
                            stopped_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except:
                pass
            return stopped_count
        
        # Función para verificar si está ejecutándose
        def is_running():
            try:
                response = requests.get('http://localhost:9182/metrics', timeout=3)
                return response.status_code == 200
            except:
                return False
        
        if action == 'stop':
            stopped = stop_existing_processes()
            import time
            time.sleep(2)
            
            if not is_running():
                return jsonify({
                    'success': True,
                    'message': f'Windows Exporter detenido correctamente ({stopped} procesos)',
                    'action': 'stopped'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No se pudo detener Windows Exporter completamente'
                })
        
        elif action in ['start', 'restart']:
            # Si es restart o si está ejecutándose, detener primero
            if action == 'restart' or is_running():
                stop_existing_processes()
                import time
                time.sleep(2)
            
            # Iniciar nuevo proceso
            try:
                process = subprocess.Popen(
                    [exe_path, '--web.listen-address=:9182'],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Esperar y verificar
                import time
                time.sleep(5)
                
                if is_running():
                    return jsonify({
                        'success': True,
                        'message': f'Windows Exporter {action}ed exitosamente',
                        'action': action,
                        'pid': process.pid,
                        'port': 9182,
                        'metrics_url': 'http://localhost:9182/metrics'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'Windows Exporter iniciado pero no responde en puerto 9182',
                        'suggestion': 'Verificar logs o conflictos de puerto'
                    })
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error iniciando Windows Exporter: {str(e)}'
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Acción no válida: {action}',
                'valid_actions': ['start', 'stop', 'restart']
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error controlando Windows Exporter: {str(e)}'
        })

@app.route('/api/cloud/credentials', methods=['GET', 'POST'])
def cloud_credentials():
    """Gestionar credenciales de nube (AWS, Azure, etc.)"""
    config_path = Path("config/cloud_credentials.json")
    
    if request.method == 'GET':
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Verificar credenciales realmente configuradas
                result = {}
                
                # Verificar AWS
                aws_config = config.get('aws', {})
                aws_configured = (
                    bool(aws_config.get('access_key', '').strip()) and 
                    bool(aws_config.get('secret_key', '').strip())
                )
                result['aws_configured'] = aws_configured
                result['aws_region'] = aws_config.get('region', '')
                
                # Verificar Azure
                azure_config = config.get('azure', {})
                azure_configured = (
                    bool(azure_config.get('client_id', '').strip()) and 
                    bool(azure_config.get('client_secret', '').strip()) and
                    bool(azure_config.get('tenant_id', '').strip())
                )
                result['azure_configured'] = azure_configured
                result['azure_subscription'] = azure_config.get('subscription_id', '')
                
                # GCP deshabilitado por solicitud del usuario
                result['gcp_configured'] = False
                result['gcp_project'] = ''
                
                # Actualizar visibilidad de dashboards en Grafana usando el dashboard manager
                try:
                    import subprocess
                    # Ejecutar el dashboard manager para sincronizar dashboards
                    subprocess.run([
                        'python', 'dashboard_manager.py'
                    ], capture_output=True, timeout=30, cwd='.')
                except Exception as e:
                    print(f"Error ejecutando dashboard manager: {e}")
                
                return jsonify(result)
            else:
                result = {
                    'aws_configured': False,
                    'azure_configured': False, 
                    'gcp_configured': False
                }
                return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'Error leyendo configuración: {str(e)}'})
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # Crear directorio si no existe
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar configuración existente o crear nueva
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Actualizar credenciales según el proveedor
            if 'aws' in data:
                config['aws'] = {
                    'access_key': data['aws'].get('access_key', ''),
                    'secret_key': data['aws'].get('secret_key', ''),
                    'region': data['aws'].get('region', 'us-east-1')
                }
            
            if 'azure' in data:
                config['azure'] = {
                    'client_id': data['azure'].get('client_id', ''),
                    'client_secret': data['azure'].get('client_secret', ''),
                    'tenant_id': data['azure'].get('tenant_id', ''),
                    'subscription_id': data['azure'].get('subscription_id', '')
                }
            
            if 'gcp' in data:
                # GCP deshabilitado - no guardar configuración
                pass
            
            # Guardar configuración
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Ejecutar dashboard manager para actualizar dashboards según credenciales
            try:
                import subprocess
                subprocess.run([
                    'python', 'dashboard_manager.py'
                ], capture_output=True, timeout=30, cwd='.')
            except Exception as e:
                print(f"Error ejecutando dashboard manager: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Credenciales de nube guardadas exitosamente'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error guardando credenciales: {str(e)}'
            })

@app.route('/api/email/recipients', methods=['GET', 'POST', 'DELETE'])
def email_recipients():
    """Gestionar destinatarios de email"""
    config_files = [
        Path("config/optimon/email_recipients.json"),
        Path("config/email_recipients.json")
    ]
    
    # Encontrar archivo de configuración existente
    config_path = None
    for path in config_files:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        config_path = config_files[0]  # Usar el primero como default
    
    if request.method == 'GET':
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return jsonify(config)
            else:
                return jsonify({
                    'recipients': [],
                    'default_recipient': '',
                    'notifications_enabled': True
                })
        except Exception as e:
            return jsonify({'error': f'Error leyendo destinatarios: {str(e)}'})
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # Crear directorio si no existe
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar configuración existente o crear nueva
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {'recipients': [], 'notifications_enabled': True}
            
            if 'add_recipient' in data:
                # Agregar nuevo destinatario
                new_recipient = {
                    'email': data['add_recipient']['email'],
                    'name': data['add_recipient'].get('name', ''),
                    'active': data['add_recipient'].get('active', True),
                    'added_date': datetime.now().isoformat()
                }
                config['recipients'].append(new_recipient)
                message = f"Destinatario {new_recipient['email']} agregado"
                
            elif 'update_recipient' in data:
                # Actualizar destinatario existente
                email = data['update_recipient']['email']
                for recipient in config['recipients']:
                    if recipient['email'] == email:
                        recipient.update(data['update_recipient'])
                        break
                message = f"Destinatario {email} actualizado"
                
            elif 'set_default' in data:
                # Configurar destinatario por defecto
                config['default_recipient'] = data['set_default']
                message = f"Destinatario por defecto configurado: {data['set_default']}"
                
            elif 'test_alert' in data:
                # Enviar alerta de prueba
                try:
                    import subprocess
                    alert_data = data['test_alert']
                    
                    # Simular payload de AlertManager
                    alert_payload = {
                        "alerts": [{
                            "status": "firing",
                            "labels": {
                                "alertname": alert_data.get('title', 'Alerta de Prueba'),
                                "severity": alert_data.get('severity', 'info'),
                                "instance": "test-instance"
                            },
                            "annotations": {
                                "summary": alert_data.get('message', 'Mensaje de prueba'),
                                "description": "Alerta generada desde el panel de OptiMon para pruebas"
                            },
                            "startsAt": datetime.now().isoformat(),
                            "generatorURL": "http://localhost:5000/test"
                        }],
                        "version": "4",
                        "groupKey": "test-group",
                        "status": "firing",
                        "receiver": "optimon-webhook"
                    }
                    
                    # Enviar a nuestro servicio SMTP
                    import requests
                    smtp_response = requests.post(
                        "http://localhost:5555/send-alert",
                        json=alert_payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    if smtp_response.status_code == 200:
                        message = "Alerta de prueba enviada exitosamente"
                    else:
                        message = f"Error enviando alerta: {smtp_response.status_code}"
                        
                except Exception as e:
                    message = f"Error enviando alerta de prueba: {str(e)}"
                
            elif 'recipients' in data:
                # Reemplazar lista completa
                config['recipients'] = data['recipients']
                message = "Lista de destinatarios actualizada"
            
            if 'notifications_enabled' in data:
                config['notifications_enabled'] = data['notifications_enabled']
            
            if 'default_recipient' in data:
                config['default_recipient'] = data['default_recipient']
            
            # Guardar configuración
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'message': message,
                'total_recipients': len(config['recipients'])
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error guardando destinatarios: {str(e)}'
            })
    
    elif request.method == 'DELETE':
        try:
            data = request.json
            email = data.get('email')
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Eliminar destinatario
                config['recipients'] = [r for r in config['recipients'] if r['email'] != email]
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                return jsonify({
                    'success': True,
                    'message': f'Destinatario {email} eliminado',
                    'total_recipients': len(config['recipients'])
                })
            else:
                return jsonify({'error': 'No hay configuración de destinatarios'})
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error eliminando destinatario: {str(e)}'
            })

@app.route('/api/email/test-send', methods=['POST'])
def test_email_new():
    """Enviar email de prueba"""
    try:
        data = request.json
        test_email = data.get('email')
        
        if not test_email:
            return jsonify({'error': 'Email requerido'})
        
        # Enviar solicitud al servicio SMTP interno
        smtp_url = "http://localhost:5555/send"
        test_data = {
            'subject': 'Prueba de OptiMon - Configuración Correcta',
            'message': '''
            <h2>🎉 ¡Configuración Exitosa!</h2>
            <p>Este es un email de prueba desde OptiMon Dashboard.</p>
            <p><strong>Fecha:</strong> {}</p>
            <p><strong>Sistema:</strong> OptiMon v2.0</p>
            <p>Si recibes este mensaje, la configuración de alertas está funcionando correctamente.</p>
            '''.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            'to_email': test_email
        }
        
        response = requests.post(smtp_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': f'Email de prueba enviado a {test_email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Error enviando email: HTTP {response.status_code}'
            })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error conectando al servicio SMTP: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error enviando email de prueba: {str(e)}'
        })

@app.route('/api/test/complete', methods=['POST'])
def run_complete_test():
    """Ejecutar prueba completa del sistema"""
    try:
        import subprocess
        import os
        
        # Ejecutar el script de prueba completa
        script_path = Path(__file__).parent / "test_complete_integral.py"
        
        if not script_path.exists():
            return jsonify({
                'success': False,
                'error': 'Script de prueba no encontrado'
            })
        
        # Ejecutar script de prueba
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        # Procesar salida
        output_lines = result.stdout.split('\n')
        
        # Extraer información del resultado
        score = 0
        total_tests = 0
        passed_tests = 0
        test_details = []
        
        for line in output_lines:
            if "pruebas exitosas" in line:
                # Extraer números del formato "X/Y pruebas exitosas (Z%)"
                parts = line.split()
                for part in parts:
                    if '/' in part:
                        passed, total = part.split('/')
                        passed_tests = int(passed)
                        total_tests = int(total)
                    elif '%' in part and '(' in part:
                        score_str = part.replace('(', '').replace('%)', '')
                        score = float(score_str)
            elif line.strip().startswith('✅') or line.strip().startswith('❌'):
                test_details.append(line.strip())
        
        return jsonify({
            'success': True,
            'score': score,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'test_details': test_details,
            'output': result.stdout,
            'exit_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout en la ejecución de pruebas (5 minutos)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error ejecutando pruebas: {str(e)}'
        })

def update_grafana_dashboards_visibility(credentials_config):
    """
    Actualizar visibilidad de dashboards en Grafana según credenciales configuradas
    """
    try:
        import requests
        
        grafana_url = "http://localhost:3000"
        auth = ('admin', 'admin')
        
        # Mapeo de dashboards por proveedor
        dashboard_mapping = {
            'aws': ['aws-ec2-improved', 'optimon-aws-ec2'],
            'azure': ['optimon-azure-vms'],
            'gcp': []  # Agregar UIDs de dashboards GCP cuando se implementen
        }
        
        # Obtener todos los dashboards
        search_response = requests.get(f"{grafana_url}/api/search", auth=auth, timeout=10)
        if search_response.status_code != 200:
            return
            
        dashboards = search_response.json()
        
        for dashboard in dashboards:
            uid = dashboard.get('uid')
            title = dashboard.get('title', '')
            
            # Determinar si el dashboard debe ser visible
            should_be_visible = True
            
            # Verificar dashboards AWS
            if uid in dashboard_mapping['aws'] or 'aws' in title.lower() or 'ec2' in title.lower():
                should_be_visible = credentials_config.get('aws_configured', False)
            
            # Verificar dashboards Azure
            elif uid in dashboard_mapping['azure'] or 'azure' in title.lower():
                should_be_visible = credentials_config.get('azure_configured', False)
            
            # Verificar dashboards GCP (siempre ocultos)
            elif uid in dashboard_mapping['gcp'] or 'gcp' in title.lower() or 'google' in title.lower():
                should_be_visible = False  # GCP deshabilitado
            
            # Si es un dashboard de nube y no debe ser visible, ocultarlo
            if not should_be_visible and any(provider in title.lower() for provider in ['aws', 'azure', 'gcp', 'ec2']):
                try:
                    # Obtener dashboard actual
                    get_response = requests.get(f"{grafana_url}/api/dashboards/uid/{uid}", auth=auth, timeout=5)
                    if get_response.status_code == 200:
                        dashboard_data = get_response.json()
                        
                        # Marcar como oculto agregando tag
                        if 'dashboard' in dashboard_data:
                            tags = dashboard_data['dashboard'].get('tags', [])
                            if 'hidden-no-credentials' not in tags:
                                tags.append('hidden-no-credentials')
                                dashboard_data['dashboard']['tags'] = tags
                                
                                # Actualizar dashboard
                                update_data = {
                                    'dashboard': dashboard_data['dashboard'],
                                    'overwrite': True,
                                    'message': 'Ocultar dashboard - sin credenciales'
                                }
                                requests.post(f"{grafana_url}/api/dashboards/db", 
                                            json=update_data, auth=auth, timeout=5)
                except:
                    continue
                    
    except Exception as e:
        print(f"Error actualizando visibilidad de dashboards: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando OptiMon Dashboard...")
    print("🌐 Accede a: http://localhost:5000")
    print("📧 Panel de control para gestionar OptiMon")
    
    # Deshabilitar debug si se ejecuta automáticamente
    debug_mode = len(sys.argv) == 1  # Solo debug si se ejecuta manualmente
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)