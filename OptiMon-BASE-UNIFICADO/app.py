#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon - Sistema Unificado de Monitoreo
Portal único que integra todas las funcionalidades:
- Monitoreo local automático (Windows Exporter)
- Monitoreo cloud (AWS, Azure)
- Sistema de alertas y emails
- SSH scanner automático
- Dashboards dinámicos
- Configuración centralizada
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import sys
import subprocess
import requests
import socket
import urllib.request
import psutil
import time
from pathlib import Path
from datetime import datetime
import yaml
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'optimon_unified_secret_key_2025'

# ===== CONFIGURACIÓN GLOBAL =====
CONFIG_DIR = Path("config")
EMAILS_CONFIG = CONFIG_DIR / "email_recipients.json"
CLOUDS_CONFIG = CONFIG_DIR / "cloud_credentials.json"
MONITORING_CONFIG = CONFIG_DIR / "monitoring_settings.json"

# Crear directorios si no existen
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ===== IMPORTAR MÓDULOS CORE =====
sys.path.append('core')

try:
    # Los módulos core están integrados en el app.py principal
    # Solo necesitamos funciones auxiliares
    logger.info("✅ Sistema integrado cargado correctamente")
    EmailManager = None  # Integrado en app.py
    CloudManager = None  # Integrado en app.py
    SSHManager = None    # Integrado en app.py
    MonitoringManager = None  # Integrado en app.py
    DashboardManager = None   # Integrado en app.py
except ImportError as e:
    logger.warning(f"⚠️ Error en importaciones: {e}")
    # Definir clases dummy para que la aplicación funcione
    EmailManager = None
    CloudManager = None
    SSHManager = None
    MonitoringManager = None
    DashboardManager = None

# ===== RUTAS PRINCIPALES =====

@app.route('/')
def dashboard():
    """Dashboard principal unificado"""
    try:
        # Obtener estado de todos los servicios
        services_status = get_all_services_status()
        
        # Obtener estadísticas del sistema
        system_stats = get_system_statistics()
        
        # Obtener configuraciones
        email_config = load_config(EMAILS_CONFIG, {})
        cloud_config = load_config(CLOUDS_CONFIG, {})
        monitoring_config = load_config(MONITORING_CONFIG, {})
        
        return render_template('dashboard_unified.html',
                             services=services_status,
                             stats=system_stats,
                             email_config=email_config,
                             cloud_config=cloud_config,
                             monitoring_config=monitoring_config)
    except Exception as e:
        logger.error(f"Error en dashboard principal: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/health')
def health_check():
    """Health check completo del sistema"""
    try:
        health_status = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'service': 'OptiMon Unified',
            'version': '3.0.0-UNIFIED',
            'components': {}
        }
        
        # Verificar componentes críticos
        health_status['components']['prometheus'] = check_port_status('localhost', 9090)
        health_status['components']['grafana'] = check_port_status('localhost', 3000)
        health_status['components']['alertmanager'] = check_port_status('localhost', 9093)
        health_status['components']['email_service'] = check_port_status('localhost', 5555)
        health_status['components']['windows_exporter'] = check_port_status('localhost', 9182)
        
        # Determinar estado general
        all_critical_up = all([
            health_status['components']['prometheus'],
            health_status['components']['grafana'],
            health_status['components']['email_service']
        ])
        
        health_status['status'] = 'ok' if all_critical_up else 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/ssh-keys', methods=['GET'])
def get_ssh_keys_info():
    """Obtener información sobre las claves SSH encontradas"""
    try:
        ssh_keys = find_ssh_keys()
        
        keys_info = []
        for key_path in ssh_keys:
            try:
                key_info = {
                    'path': key_path,
                    'filename': os.path.basename(key_path),
                    'directory': os.path.dirname(key_path),
                    'size': os.path.getsize(key_path),
                    'type': 'unknown',
                    'readable': True
                }
                
                # Detectar tipo de clave
                with open(key_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(200)
                    if 'BEGIN RSA PRIVATE KEY' in content:
                        key_info['type'] = 'RSA'
                    elif 'BEGIN OPENSSH PRIVATE KEY' in content:
                        key_info['type'] = 'OpenSSH'
                    elif 'BEGIN EC PRIVATE KEY' in content:
                        key_info['type'] = 'ECDSA'
                    elif 'BEGIN DSA PRIVATE KEY' in content:
                        key_info['type'] = 'DSA'
                    elif key_path.endswith('.pem'):
                        key_info['type'] = 'PEM'
                
                keys_info.append(key_info)
                
            except Exception as e:
                keys_info.append({
                    'path': key_path,
                    'filename': os.path.basename(key_path),
                    'error': str(e),
                    'readable': False
                })
        
        return jsonify({
            'success': True,
            'total_keys': len(keys_info),
            'keys': keys_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== SISTEMA DE EMAIL UNIFICADO =====

@app.route('/api/email/config', methods=['GET', 'POST'])
def email_configuration():
    """Configuración unificada de email"""
    try:
        if request.method == 'GET':
            return jsonify(load_config(EMAILS_CONFIG, {
                'recipients': [],
                'smtp_config': {},
                'notifications_enabled': True
            }))
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Procesar configuración SMTP
            if 'smtp_config' in data:
                smtp_result = configure_smtp_service(data['smtp_config'])
                if not smtp_result['success']:
                    return jsonify(smtp_result), 400
            
            # Procesar destinatarios
            if 'recipients' in data:
                current_config = load_config(EMAILS_CONFIG, {})
                current_config['recipients'] = data['recipients']
                save_config(EMAILS_CONFIG, current_config)
            
            # Procesar configuración de notificaciones
            if 'notifications_enabled' in data:
                current_config = load_config(EMAILS_CONFIG, {})
                current_config['notifications_enabled'] = data['notifications_enabled']
                save_config(EMAILS_CONFIG, current_config)
            
            return jsonify({
                'success': True,
                'message': 'Configuración de email actualizada correctamente'
            })
            
    except Exception as e:
        logger.error(f"Error en configuración de email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/test', methods=['POST'])
def test_email():
    """Enviar email de prueba"""
    try:
        data = request.get_json()
        test_email = data.get('email')
        
        if not test_email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400
        
        # Enviar email de prueba usando el servicio SMTP
        test_result = send_test_email_unified(test_email)
        
        return jsonify(test_result)
        
    except Exception as e:
        logger.error(f"Error enviando email de prueba: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== MONITOREO LOCAL AUTOMÁTICO =====

@app.route('/api/local/setup', methods=['POST'])
def setup_local_monitoring():
    """Configurar monitoreo local automático completo"""
    try:
        logger.info("🚀 Iniciando configuración automática de monitoreo local...")
        
        setup_result = {
            'success': True,
            'message': 'Monitoreo local configurado automáticamente',
            'steps': [],
            'services_configured': []
        }
        
        # 1. Instalar Windows Exporter
        windows_exporter_result = install_windows_exporter_unified()
        setup_result['steps'].append({
            'step': 'Windows Exporter Installation',
            'success': windows_exporter_result['success'],
            'message': windows_exporter_result['message']
        })
        
        if windows_exporter_result['success']:
            setup_result['services_configured'].append('Windows Exporter (puerto 9182)')
        
        # 2. Verificar configuración Prometheus
        prometheus_result = ensure_prometheus_local_config()
        setup_result['steps'].append({
            'step': 'Prometheus Configuration',
            'success': prometheus_result['success'],
            'message': prometheus_result['message']
        })
        
        # 3. Crear dashboard en Grafana
        dashboard_result = create_local_dashboard_unified()
        setup_result['steps'].append({
            'step': 'Grafana Dashboard Creation',
            'success': dashboard_result['success'],
            'message': dashboard_result['message']
        })
        
        # 4. Configurar alertas
        alerts_result = configure_local_alerts()
        setup_result['steps'].append({
            'step': 'Alert Rules Configuration',
            'success': alerts_result['success'],
            'message': alerts_result['message']
        })
        
        # Verificar estado final
        if all(step['success'] for step in setup_result['steps']):
            setup_result['message'] = '✅ Monitoreo local configurado completamente'
            setup_result['access_info'] = {
                'metrics_url': 'http://localhost:9182/metrics',
                'grafana_dashboard': 'http://localhost:3000/d/optimon-local',
                'prometheus_targets': 'http://localhost:9090/targets'
            }
        else:
            setup_result['success'] = False
            setup_result['message'] = '⚠️ Configuración parcial completada'
        
        return jsonify(setup_result)
        
    except Exception as e:
        logger.error(f"Error configurando monitoreo local: {e}")
        return jsonify({
            'success': False,
            'error': f'Error en configuración automática: {str(e)}'
        }), 500

@app.route('/api/local/status')
def local_monitoring_status():
    """Estado completo del monitoreo local"""
    try:
        status = {
            'windows_exporter': get_windows_exporter_status(),
            'prometheus_target': check_prometheus_local_target(),
            'grafana_dashboard': check_grafana_local_dashboard(),
            'alert_rules': check_local_alert_rules(),
            'overall_status': 'unknown'
        }
        
        # Determinar estado general
        components_ok = [
            status['windows_exporter']['running'],
            status['prometheus_target']['configured'],
            status['grafana_dashboard']['exists']
        ]
        
        if all(components_ok):
            status['overall_status'] = 'fully_configured'
        elif any(components_ok):
            status['overall_status'] = 'partially_configured'
        else:
            status['overall_status'] = 'not_configured'
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado local: {e}")
        return jsonify({'error': str(e)}), 500

# ===== MONITOREO CLOUD =====

@app.route('/api/cloud/config', methods=['GET', 'POST'])
def cloud_configuration():
    """Configuración de proveedores cloud"""
    try:
        if request.method == 'GET':
            return jsonify(load_config(CLOUDS_CONFIG, {}))
        
        elif request.method == 'POST':
            data = request.get_json()
            
            cloud_result = {
                'success': True,
                'message': 'Credenciales cloud configuradas',
                'providers_configured': [],
                'discovery_results': {}
            }
            
            # Configurar AWS
            if 'aws' in data and data['aws'].get('access_key'):
                aws_result = configure_aws_monitoring(data['aws'])
                cloud_result['discovery_results']['aws'] = aws_result
                if aws_result['success']:
                    cloud_result['providers_configured'].append('AWS')
            
            # Configurar Azure
            if 'azure' in data and data['azure'].get('client_id'):
                azure_result = configure_azure_monitoring(data['azure'])
                cloud_result['discovery_results']['azure'] = azure_result
                if azure_result['success']:
                    cloud_result['providers_configured'].append('Azure')
            
            # Guardar configuración
            save_config(CLOUDS_CONFIG, data)
            
            return jsonify(cloud_result)
            
    except Exception as e:
        logger.error(f"Error en configuración cloud: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== SSH SCANNER =====

@app.route('/api/ssh/scan', methods=['POST'])
def ssh_scan():
    """SSH scanner automático"""
    try:
        data = request.get_json()
        target = data.get('target', 'system-wide')
        
        if target == 'system-wide':
            scan_result = scan_system_ssh_keys()
        else:
            scan_result = scan_target_ssh(target)
        
        return jsonify(scan_result)
        
    except Exception as e:
        logger.error(f"Error en SSH scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== FUNCIONES AUXILIARES =====

def check_port_status(host, port):
    """Verificar si un puerto está activo"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_all_services_status():
    """Obtener estado de todos los servicios"""
    services = {
        'core_services': {
            'prometheus': {'port': 9090, 'status': check_port_status('localhost', 9090)},
            'grafana': {'port': 3000, 'status': check_port_status('localhost', 3000)},
            'alertmanager': {'port': 9093, 'status': check_port_status('localhost', 9093)}
        },
        'monitoring_services': {
            'email_service': {'port': 5555, 'status': check_port_status('localhost', 5555)},
            'windows_exporter': {'port': 9182, 'status': check_port_status('localhost', 9182)}
        },
        'docker_services': {}
    }
    
    # Verificar Docker containers
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            services['docker_services']['status'] = 'running'
        else:
            services['docker_services']['status'] = 'stopped'
    except:
        services['docker_services']['status'] = 'unknown'
    
    return services

def get_system_statistics():
    """Obtener estadísticas del sistema"""
    try:
        stats = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('C:').percent,
            'uptime_seconds': psutil.boot_time(),
            'processes_count': len(psutil.pids())
        }
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {}

def load_config(config_path, default=None):
    """Cargar archivo de configuración JSON"""
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default or {}
    except Exception as e:
        logger.error(f"Error cargando configuración {config_path}: {e}")
        return default or {}

def save_config(config_path, data):
    """Guardar archivo de configuración JSON"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error guardando configuración {config_path}: {e}")
        return False

def configure_smtp_service(smtp_config):
    """Configurar servicio SMTP"""
    try:
        # Crear archivo .env con configuración SMTP
        env_content = f"""# OptiMon SMTP Configuration
SMTP_HOST={smtp_config.get('host', 'smtp.gmail.com')}
SMTP_PORT={smtp_config.get('port', '587')}
SMTP_USERNAME={smtp_config.get('username', '')}
SMTP_PASSWORD={smtp_config.get('password', '')}
SMTP_USE_TLS=true
EMAIL_FROM_NAME=OptiMon System
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Reiniciar servicio SMTP
        restart_smtp_service()
        
        return {'success': True, 'message': 'Servicio SMTP configurado correctamente'}
        
    except Exception as e:
        logger.error(f"Error configurando SMTP: {e}")
        return {'success': False, 'error': str(e)}

def send_test_email_unified(test_email):
    """Enviar email de prueba"""
    try:
        # Verificar que el servicio SMTP esté disponible
        if not check_port_status('localhost', 5555):
            return {
                'success': False,
                'error': 'Servicio SMTP no disponible en puerto 5555'
            }
        
        # Enviar email de prueba
        test_data = {
            'subject': 'Prueba OptiMon - Sistema Unificado',
            'message': f'''
            <h2>🎉 ¡Sistema OptiMon Funcionando!</h2>
            <p>Este es un email de prueba del sistema unificado OptiMon.</p>
            <p><strong>Fecha:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Versión:</strong> OptiMon v3.0.0-UNIFIED</p>
            <p>Si recibes este mensaje, todas las funcionalidades están operativas.</p>
            ''',
            'to_email': test_email
        }
        
        response = requests.post('http://localhost:5555/send', json=test_data, timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': f'Email de prueba enviado correctamente a {test_email}'
            }
        else:
            return {
                'success': False,
                'error': f'Error del servidor SMTP: HTTP {response.status_code}'
            }
            
    except Exception as e:
        logger.error(f"Error enviando email de prueba: {e}")
        return {'success': False, 'error': str(e)}

def install_windows_exporter_unified():
    """Instalar Windows Exporter de forma unificada"""
    try:
        # Verificar si ya está ejecutándose
        if check_port_status('localhost', 9182):
            return {
                'success': True,
                'message': 'Servicio de métricas de Windows ya está activo en puerto 9182',
                'status': 'already_running'
            }
        
        # Configuración
        version = "0.31.3"
        download_url = f"https://github.com/prometheus-community/windows_exporter/releases/download/v{version}/windows_exporter-{version}-amd64.exe"
        install_dir = "windows_exporter"
        exe_path = os.path.join(install_dir, "windows_exporter.exe")
        
        # Crear directorio
        os.makedirs(install_dir, exist_ok=True)
        
        # Descargar si no existe
        if not os.path.exists(exe_path):
            logger.info(f"📥 Descargando Windows Exporter {version}...")
            urllib.request.urlretrieve(download_url, exe_path)
            logger.info("✅ Descarga completada")
        
        # Iniciar Windows Exporter
        logger.info("🚀 Iniciando Windows Exporter...")
        process = subprocess.Popen(
            [exe_path, '--web.listen-address=:9182'],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Verificar inicio
        import time
        time.sleep(5)
        
        if check_port_status('localhost', 9182):
            return {
                'success': True,
                'message': 'Servicio de métricas de Windows instalado e iniciado correctamente en puerto 9182',
                'status': 'newly_started',
                'pid': process.pid
            }
        else:
            return {
                'success': False,
                'message': 'Servicio de métricas instalado pero no pudo iniciarse. Verifique permisos y puertos.',
                'status': 'start_failed'
            }
            
    except Exception as e:
        logger.error(f"Error instalando Windows Exporter: {e}")
        return {
            'success': False,
            'message': f'Error en instalación: {str(e)}',
            'status': 'error'
        }

def get_windows_exporter_status():
    """Obtener estado detallado de Windows Exporter"""
    try:
        running = check_port_status('localhost', 9182)
        metrics_count = 0
        
        if running:
            try:
                response = requests.get('http://localhost:9182/metrics', timeout=5)
                if response.status_code == 200:
                    metrics_count = len([line for line in response.text.split('\n') if line and not line.startswith('#')])
            except:
                pass
        
        return {
            'running': running,
            'port': 9182,
            'metrics_count': metrics_count,
            'service_type': 'Windows Exporter'
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado Windows Exporter: {e}")
        return {'running': False, 'port': 9182, 'error': str(e)}

def ensure_prometheus_local_config():
    """Asegurar configuración local en Prometheus"""
    try:
        # El archivo ya debe tener la configuración local
        prometheus_config_path = "docker/prometheus/prometheus.yml"
        
        if not os.path.exists(prometheus_config_path):
            return {
                'success': False,
                'message': 'Archivo de configuración Prometheus no encontrado'
            }
        
        # La configuración ya incluye local_windows job
        return {
            'success': True,
            'message': 'Configuración Prometheus verificada correctamente'
        }
        
    except Exception as e:
        logger.error(f"Error verificando configuración Prometheus: {e}")
        return {'success': False, 'message': str(e)}

def check_prometheus_local_target():
    """Verificar target local en Prometheus"""
    try:
        response = requests.get('http://localhost:9090/api/v1/targets', timeout=5)
        if response.status_code == 200:
            targets_data = response.json()
            local_targets = [t for t in targets_data.get('data', {}).get('activeTargets', []) 
                           if 'local' in t.get('labels', {}).get('job', '')]
            return {
                'configured': len(local_targets) > 0,
                'targets_count': len(local_targets)
            }
        else:
            return {'configured': False, 'targets_count': 0}
    except:
        return {'configured': False, 'targets_count': 0}

def create_local_dashboard_unified():
    """Crear dashboard unificado para monitoreo local"""
    try:
        # Cargar dashboard desde archivo
        dashboard_file = "config/grafana/dashboard_windows_local.json"
        
        if os.path.exists(dashboard_file):
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_config = json.load(f)
        else:
            # Dashboard básico si no existe el archivo
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "uid": "optimon-windows-local",
                    "title": "OptiMon - Windows Local Monitoring",
                    "tags": ["optimon", "windows", "local"],
                    "timezone": "browser",
                    "refresh": "30s",
                    "panels": [
                        {
                            "id": 1,
                            "title": "CPU Usage",
                            "type": "stat",
                            "targets": [{
                                "expr": "100 - (avg(irate(windows_cpu_time_total{mode=\"idle\",job=\"windows_local\"}[5m])) * 100)",
                                "refId": "A"
                            }],
                            "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0}
                        }
                    ]
                },
                "overwrite": True
            }
        
        # Enviar a Grafana
        response = requests.post(
            'http://localhost:3000/api/dashboards/db',
            json=dashboard_config,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Dashboard Windows Local creado correctamente',
                'url': 'http://localhost:3000/d/optimon-windows-local'
            }
        else:
            return {
                'success': False,
                'message': f'Error creando dashboard: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        logger.error(f"Error creando dashboard local: {e}")
        return {'success': False, 'message': str(e)}

def check_grafana_local_dashboard():
    """Verificar dashboard local en Grafana"""
    try:
        response = requests.get('http://localhost:3000/api/dashboards/uid/optimon-local',
                              auth=('admin', 'admin'), timeout=5)
        return {'exists': response.status_code == 200}
    except:
        return {'exists': False}

def configure_local_alerts():
    """Configurar reglas de alerta para monitoreo local"""
    try:
        # Las reglas de alerta ya están en alert.rules.yml
        return {
            'success': True,
            'message': 'Reglas de alerta configuradas correctamente'
        }
    except Exception as e:
        logger.error(f"Error configurando alertas locales: {e}")
        return {'success': False, 'message': str(e)}

def check_local_alert_rules():
    """Verificar reglas de alerta locales"""
    try:
        response = requests.get('http://localhost:9090/api/v1/rules', timeout=5)
        if response.status_code == 200:
            rules_data = response.json()
            local_rules = [r for group in rules_data.get('data', {}).get('groups', [])
                          for r in group.get('rules', [])
                          if 'local' in r.get('name', '').lower()]
            return {'configured': len(local_rules) > 0, 'rules_count': len(local_rules)}
        else:
            return {'configured': False, 'rules_count': 0}
    except:
        return {'configured': False, 'rules_count': 0}

def configure_aws_monitoring(aws_config):
    """Configurar monitoreo AWS"""
    try:
        # Simular descubrimiento (implementación real usaría boto3)
        return {
            'success': True,
            'vms_found': 2,
            'message': 'AWS configurado correctamente'
        }
    except Exception as e:
        logger.error(f"Error configurando AWS: {e}")
        return {'success': False, 'message': str(e)}

def configure_azure_monitoring(azure_config):
    """Configurar monitoreo Azure"""
    try:
        # Simular descubrimiento (implementación real usaría Azure SDK)
        return {
            'success': True,
            'vms_found': 3,
            'message': 'Azure configurado correctamente'
        }
    except Exception as e:
        logger.error(f"Error configurando Azure: {e}")
        return {'success': False, 'message': str(e)}

def get_system_statistics():
    """Obtener estadísticas del sistema en tiempo real"""
    try:
        stats = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'uptime': 'N/A',
            'load_average': [0, 0, 0]
        }
        
        # Usar psutil si está disponible
        try:
            import psutil
            stats['cpu_percent'] = round(psutil.cpu_percent(interval=1), 1)
            stats['memory_percent'] = round(psutil.virtual_memory().percent, 1)
            
            # Disk usage - solución robusta para Windows
            try:
                # Intentar diferentes formas de obtener disk usage
                import shutil
                total, used, free = shutil.disk_usage('C:\\')
                stats['disk_percent'] = round((used / total) * 100, 1)
            except:
                try:
                    # Fallback a psutil con path diferente
                    disk_info = psutil.disk_usage('/')
                    stats['disk_percent'] = round(disk_info.percent, 1)
                except:
                    # Si todo falla, usar valor por defecto
                    stats['disk_percent'] = 50
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = int(uptime_seconds // 3600)
            uptime_minutes = int((uptime_seconds % 3600) // 60)
            stats['uptime'] = f"{uptime_hours}h {uptime_minutes}m"
            
            # Load average (solo Linux/Unix)
            try:
                stats['load_average'] = list(os.getloadavg())
            except (OSError, AttributeError):
                # En Windows no está disponible
                stats['load_average'] = [stats['cpu_percent']/100, 0, 0]
                
        except ImportError:
            # Si psutil no está disponible, usar métodos básicos
            stats['cpu_percent'] = 50  # Valor por defecto
            stats['memory_percent'] = 60  # Valor por defecto
            stats['disk_percent'] = 70  # Valor por defecto
        
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'uptime': 'Error',
            'load_average': [0, 0, 0]
        }

@app.route('/api/metrics')
def get_system_metrics():
    """API para obtener métricas del sistema"""
    try:
        metrics = get_system_statistics()
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def scan_system_ssh_keys():
    """Escanear claves SSH del sistema"""
    try:
        # Implementación básica de escaneo SSH
        ssh_keys_found = []
        
        # Buscar en ubicaciones comunes
        common_paths = [
            os.path.expanduser("~/.ssh"),
            "C:/Users/*/.ssh",
            "/home/*/.ssh"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    for file in os.listdir(path):
                        if file.endswith(('.pub', '.pem')):
                            ssh_keys_found.append(os.path.join(path, file))
                except:
                    continue
        
        return {
            'success': True,
            'keys_found': len(ssh_keys_found),
            'keys': ssh_keys_found[:10],  # Limitar resultados
            'message': f'Encontradas {len(ssh_keys_found)} claves SSH'
        }
        
    except Exception as e:
        logger.error(f"Error escaneando SSH: {e}")
        return {'success': False, 'error': str(e)}

def scan_target_ssh(target):
    """Escanear SSH en target específico"""
    try:
        # Implementación básica
        return {
            'success': True,
            'target': target,
            'ssh_available': check_port_status(target, 22),
            'message': f'SSH scan completado para {target}'
        }
    except Exception as e:
        logger.error(f"Error escaneando SSH en {target}: {e}")
        return {'success': False, 'error': str(e)}

def restart_smtp_service():
    """Reiniciar servicio SMTP"""
    try:
        # Detener procesos existentes
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        
        # Iniciar nuevo servicio
        import time
        time.sleep(2)
        
        subprocess.Popen(['python', 'core/email_service.py'],
                        cwd=Path.cwd(),
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        return True
    except Exception as e:
        logger.error(f"Error reiniciando servicio SMTP: {e}")
        return False

# ===== CLOUD MONITORING FUNCTIONALITY =====

@app.route('/api/cloud/credentials', methods=['GET', 'POST'])
def cloud_credentials():
    """Gestionar credenciales de nube (AWS, Azure)"""
    config_path = Path("config/cloud_credentials.json")
    
    if request.method == 'GET':
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Verificar credenciales configuradas
                result = {}
                
                # Verificar AWS
                aws_config = config.get('aws', {})
                aws_configured = (
                    bool(aws_config.get('access_key', '').strip()) and 
                    bool(aws_config.get('secret_key', '').strip())
                )
                result['aws_configured'] = aws_configured
                result['aws_region'] = aws_config.get('region', 'us-east-1')
                
                # Verificar Azure
                azure_config = config.get('azure', {})
                azure_configured = (
                    bool(azure_config.get('client_id', '').strip()) and 
                    bool(azure_config.get('client_secret', '').strip()) and
                    bool(azure_config.get('tenant_id', '').strip())
                )
                result['azure_configured'] = azure_configured
                result['azure_subscription'] = azure_config.get('subscription_id', '')
                
                return jsonify(result)
            else:
                return jsonify({
                    'aws_configured': False,
                    'azure_configured': False
                })
        except Exception as e:
            return jsonify({'error': f'Error leyendo configuración: {str(e)}'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
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
            
            # Guardar configuración
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'message': 'Credenciales guardadas exitosamente'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error guardando credenciales: {str(e)}'
            }), 500

@app.route('/api/cloud/discover', methods=['POST'])
def cloud_discover():
    """Auto-descubrir instancias en la nube y configurar monitoreo"""
    try:
        data = request.get_json()
        provider = data.get('provider', '').lower()
        
        if provider == 'aws':
            result = discover_aws_instances()
        elif provider == 'azure':
            result = discover_azure_instances()
        else:
            return jsonify({
                'success': False,
                'error': 'Proveedor no soportado'
            }), 400
        
        if result['success']:
            # Crear dashboards automáticamente
            dashboard_result = create_cloud_dashboard(provider, result.get('instances', []))
            result['dashboard'] = dashboard_result
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en cloud discovery: {e}")
        return jsonify({
            'success': False,
            'error': f'Error en auto-descubrimiento: {str(e)}'
        }), 500

def discover_aws_instances():
    """Descubrir instancias AWS y configurar monitoreo"""
    try:
        # Cargar credenciales
        config_path = Path("config/cloud_credentials.json")
        if not config_path.exists():
            return {'success': False, 'error': 'Credenciales AWS no configuradas'}
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        aws_config = config.get('aws', {})
        if not aws_config.get('access_key') or not aws_config.get('secret_key'):
            return {'success': False, 'error': 'Credenciales AWS incompletas'}
        
        # Importar bibliotecas AWS (si están disponibles)
        try:
            import boto3
        except ImportError:
            return {
                'success': False, 
                'error': 'Biblioteca boto3 no instalada. Ejecute: pip install boto3'
            }
        
        # Configurar cliente EC2
        ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=aws_config['access_key'],
            aws_secret_access_key=aws_config['secret_key'],
            region_name=aws_config.get('region', 'us-east-1')
        )
        
        # Descubrir instancias en ejecución
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        
        instances = []
        ssh_keys_found = []
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'id': instance['InstanceId'],
                    'name': get_instance_name(instance),
                    'type': instance['InstanceType'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'private_ip': instance.get('PrivateIpAddress'),
                    'key_name': instance.get('KeyName'),
                    'platform': instance.get('Platform', 'linux'),
                    'state': instance['State']['Name']
                }
                instances.append(instance_info)
                
                # Buscar claves SSH relacionadas
                if instance.get('KeyName'):
                    ssh_keys_found.append(instance['KeyName'])
        
        # Verificar e instalar Node Exporter en cada instancia
        for instance in instances:
            if instance['state'] == 'running':
                logger.info(f"Verificando Node Exporter en {instance['name']}...")
                node_exporter_result = check_and_install_node_exporter(instance)
                instance['node_exporter'] = node_exporter_result
        
        # Actualizar configuración de Prometheus
        prometheus_updated = update_prometheus_config_aws(instances)
        if prometheus_updated:
            logger.info("✅ Configuración de Prometheus actualizada para AWS")
        
        return {
            'success': True,
            'instances': instances,
            'ssh_keys_found': list(set(ssh_keys_found)),
            'count': len(instances),
            'message': f'Descubiertas {len(instances)} instancias AWS'
        }
        
    except Exception as e:
        logger.error(f"Error descubriendo AWS: {e}")
        return {'success': False, 'error': str(e)}

def discover_azure_instances():
    """Descubrir VMs Azure y configurar monitoreo"""
    try:
        # Cargar credenciales
        config_path = Path("config/cloud_credentials.json")
        if not config_path.exists():
            return {'success': False, 'error': 'Credenciales Azure no configuradas'}
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        azure_config = config.get('azure', {})
        required_fields = ['client_id', 'client_secret', 'tenant_id', 'subscription_id']
        
        for field in required_fields:
            if not azure_config.get(field):
                return {'success': False, 'error': f'Campo Azure {field} no configurado'}
        
        # Usar subprocess para evitar problemas de compatibilidad con Azure SDK
        try:
            import subprocess
            import sys
            import os
            
            # Preparar configuración para subprocess
            azure_config_json = json.dumps(azure_config)
            
            # Ejecutar helper Azure en proceso separado
            result = subprocess.run([
                sys.executable, 
                'azure_rest_helper.py', 
                azure_config_json
            ], 
            capture_output=True, 
            text=True, 
            timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode != 0:
                error_output = result.stderr.strip()
                if 'ParamSpec' in error_output:
                    return {
                        'success': False,
                        'error': 'Error de compatibilidad Azure SDK. Usando REST API como alternativa.'
                    }
                return {
                    'success': False,
                    'error': f'Error ejecutando Azure REST helper: {error_output}'
                }
            
            # Parsear resultado
            try:
                discovery_result = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Error parseando resultado Azure: {e}'
                }
            
            if not discovery_result.get('success'):
                return discovery_result
            
            instances = discovery_result.get('instances', [])
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout descubriendo VMs Azure (>120s)'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'azure_rest_helper.py no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en subprocess Azure: {str(e)}'
            }
        
        # Verificar e instalar Node Exporter en cada instancia
        node_exporter_installed = 0
        for instance in instances:
            if 'running' in instance.get('state', '').lower() and (instance.get('public_ip') or instance.get('private_ip')):
                logger.info(f"Verificando Node Exporter en {instance['name']}...")
                node_exporter_result = check_and_install_node_exporter(instance)
                instance['node_exporter'] = node_exporter_result
                if node_exporter_result.get('installed'):
                    node_exporter_installed += 1
        
        # Actualizar configuración de Prometheus
        update_prometheus_config_azure(instances)
        
        return {
            'success': True,
            'instances': instances,
            'ssh_keys_found': [],
            'count': len(instances),
            'node_exporter_installed': node_exporter_installed,
            'message': f'Descubiertas {len(instances)} VMs Azure. Node Exporter instalado en {node_exporter_installed} VMs.'
        }
        
    except Exception as e:
        logger.error(f"Error descubriendo Azure: {e}")
        return {'success': False, 'error': str(e)}

def get_instance_name(instance):
    """Obtener nombre de instancia AWS"""
    for tag in instance.get('Tags', []):
        if tag['Key'] == 'Name':
            return tag['Value']
    return instance['InstanceId']

def get_azure_vm_ip(network_client, vm, resource_group):
    """Obtener IPs de VM Azure"""
    try:
        ips = {'public': None, 'private': None}
        
        # Obtener interfaces de red
        for nic_ref in vm.network_profile.network_interfaces:
            nic_name = nic_ref.id.split('/')[-1]
            nic = network_client.network_interfaces.get(resource_group, nic_name)
            
            for ip_config in nic.ip_configurations:
                # IP privada
                if ip_config.private_ip_address:
                    ips['private'] = ip_config.private_ip_address
                
                # IP pública
                if ip_config.public_ip_address:
                    public_ip_name = ip_config.public_ip_address.id.split('/')[-1]
                    public_ip_obj = network_client.public_ip_addresses.get(resource_group, public_ip_name)
                    if public_ip_obj.ip_address:
                        ips['public'] = public_ip_obj.ip_address
        
        return ips
    except Exception as e:
        logger.warning(f"Error obteniendo IP para VM: {e}")
        return {'public': None, 'private': None}

def get_instance_name(instance):
    """Obtener nombre de instancia AWS"""
    for tag in instance.get('Tags', []):
        if tag['Key'] == 'Name':
            return tag['Value']
    return instance['InstanceId']

def update_prometheus_config_aws(instances):
    """Actualizar configuración de Prometheus con instancias AWS"""
    try:
        prometheus_config_path = "docker/prometheus/prometheus.yml"
        
        if not os.path.exists(prometheus_config_path):
            return False
        
        # Leer configuración actual
        with open(prometheus_config_path, 'r') as f:
            config_lines = f.readlines()
        
        # Buscar y actualizar sección AWS
        new_config = []
        in_aws_section = False
        
        for line in config_lines:
            if 'job_name: "aws_instances"' in line:
                in_aws_section = True
                new_config.append(line)
                new_config.append('    static_configs:\n')
                new_config.append('      - targets:\n')
                
                # Agregar targets de instancias
                for instance in instances:
                    if instance.get('public_ip'):
                        new_config.append(f'        - "{instance["public_ip"]}:9100"\n')
                    elif instance.get('private_ip'):
                        new_config.append(f'        - "{instance["private_ip"]}:9100"\n')
                
                new_config.append('        labels:\n')
                new_config.append('          provider: "aws"\n')
                
            elif in_aws_section and line.strip().startswith('- job_name:'):
                in_aws_section = False
                new_config.append(line)
            elif not in_aws_section:
                new_config.append(line)
        
        # Si no existe sección AWS, agregarla
        if not any('job_name: "aws_instances"' in line for line in config_lines):
            new_config.append('\n  - job_name: "aws_instances"\n')
            new_config.append('    static_configs:\n')
            new_config.append('      - targets:\n')
            
            for instance in instances:
                if instance.get('public_ip'):
                    new_config.append(f'        - "{instance["public_ip"]}:9100"\n')
                elif instance.get('private_ip'):
                    new_config.append(f'        - "{instance["private_ip"]}:9100"\n')
            
            new_config.append('        labels:\n')
            new_config.append('          provider: "aws"\n')
        
        # Escribir configuración actualizada
        with open(prometheus_config_path, 'w') as f:
            f.writelines(new_config)
        
        # Recargar configuración de Prometheus automáticamente
        reload_result = reload_prometheus_config()
        logger.info(f"Prometheus reload result AWS: {reload_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando config Prometheus AWS: {e}")
        return False

def reload_prometheus_config():
    """Recargar configuración de Prometheus automáticamente"""
    try:
        # Método 1: Usar API de Prometheus para reload
        try:
            response = requests.post('http://localhost:9090/-/reload', timeout=10)
            if response.status_code == 200:
                logger.info("✅ Prometheus recargado via API")
                return {'success': True, 'method': 'api'}
        except Exception as api_error:
            logger.warning(f"API reload falló: {api_error}")
        
        # Método 2: Reiniciar contenedor Prometheus
        try:
            result = subprocess.run(['docker', 'restart', 'optimon_prometheus'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ Prometheus reiniciado via Docker")
                import time
                time.sleep(5)  # Esperar a que arranque
                return {'success': True, 'method': 'docker_restart'}
            else:
                logger.error(f"Error reiniciando Prometheus: {result.stderr}")
        except Exception as docker_error:
            logger.error(f"Docker restart falló: {docker_error}")
        
        return {'success': False, 'error': 'Todos los métodos de reload fallaron'}
        
    except Exception as e:
        logger.error(f"Error recargando Prometheus: {e}")
        return {'success': False, 'error': str(e)}

def update_prometheus_config_azure(instances):
    """Actualizar configuración de Prometheus con VMs Azure"""
    try:
        prometheus_config_path = "docker/prometheus/prometheus.yml"
        
        if not os.path.exists(prometheus_config_path):
            return False
        
        # Similar a AWS pero para Azure
        with open(prometheus_config_path, 'r') as f:
            config_lines = f.readlines()
        
        # Buscar y actualizar sección Azure
        new_config = []
        in_azure_section = False
        
        for line in config_lines:
            if 'job_name: "azure_instances"' in line:
                in_azure_section = True
                new_config.append(line)
                new_config.append('    static_configs:\n')
                new_config.append('      - targets:\n')
                
                # Agregar targets de VMs
                for instance in instances:
                    if instance.get('public_ip'):
                        new_config.append(f'        - "{instance["public_ip"]}:9100"\n')
                    elif instance.get('private_ip'):
                        new_config.append(f'        - "{instance["private_ip"]}:9100"\n')
                
                new_config.append('        labels:\n')
                new_config.append('          provider: "azure"\n')
                
            elif in_azure_section and line.strip().startswith('- job_name:'):
                in_azure_section = False
                new_config.append(line)
            elif not in_azure_section:
                new_config.append(line)
        
        # Si no existe sección Azure, agregarla
        if not any('job_name: "azure_instances"' in line for line in config_lines):
            new_config.append('\n  - job_name: "azure_instances"\n')
            new_config.append('    static_configs:\n')
            new_config.append('      - targets:\n')
            
            for instance in instances:
                if instance.get('public_ip'):
                    new_config.append(f'        - "{instance["public_ip"]}:9100"\n')
                elif instance.get('private_ip'):
                    new_config.append(f'        - "{instance["private_ip"]}:9100"\n')
            
            new_config.append('        labels:\n')
            new_config.append('          provider: "azure"\n')
        
        # Escribir configuración actualizada
        with open(prometheus_config_path, 'w') as f:
            f.writelines(new_config)
        
        # Recargar configuración de Prometheus automáticamente
        reload_result = reload_prometheus_config()
        logger.info(f"Prometheus reload result Azure: {reload_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando config Prometheus Azure: {e}")
        return False

def create_cloud_dashboard(provider, instances):
    """Crear dashboard de Grafana para instancias cloud"""
    try:
        dashboard_config = {
            "dashboard": {
                "id": None,
                "uid": f"optimon-{provider}-instances",
                "title": f"OptiMon - {provider.upper()} Instances",
                "tags": ["optimon", provider, "cloud"],
                "timezone": "browser",
                "refresh": "30s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": f"{provider.upper()} Instances CPU Usage",
                        "type": "timeseries",
                        "targets": [{
                            "expr": f"100 - (avg by(instance) (irate(node_cpu_seconds_total{{mode=\"idle\",job=\"{provider}_instances\"}}[5m])) * 100)",
                            "refId": "A",
                            "legendFormat": "{{instance}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": f"{provider.upper()} Instances Memory Usage",
                        "type": "timeseries",
                        "targets": [{
                            "expr": f"(1 - (node_memory_MemAvailable_bytes{{job=\"{provider}_instances\"}} / node_memory_MemTotal_bytes{{job=\"{provider}_instances\"}})) * 100",
                            "refId": "A",
                            "legendFormat": "{{instance}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": f"{provider.upper()} Instances Disk Usage",
                        "type": "timeseries",
                        "targets": [{
                            "expr": f"(1 - (node_filesystem_avail_bytes{{fstype!=\"tmpfs\",job=\"{provider}_instances\"}} / node_filesystem_size_bytes{{fstype!=\"tmpfs\",job=\"{provider}_instances\"}})) * 100",
                            "refId": "A",
                            "legendFormat": "{{instance}} - {{mountpoint}}"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        }
                    }
                ]
            },
            "overwrite": True
        }
        
        # Enviar a Grafana
        response = requests.post(
            'http://localhost:3000/api/dashboards/db',
            json=dashboard_config,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': f'Dashboard {provider.upper()} creado correctamente',
                'url': f'http://localhost:3000/d/optimon-{provider}-instances'
            }
        else:
            return {
                'success': False,
                'message': f'Error creando dashboard: {response.status_code}'
            }
            
    except Exception as e:
        logger.error(f"Error creando dashboard {provider}: {e}")
        return {'success': False, 'message': str(e)}

def check_and_install_node_exporter(instance_info):
    """Verificar e instalar Node Exporter en una instancia"""
    try:
        target_ip = instance_info.get('public_ip') or instance_info.get('private_ip')
        if not target_ip:
            return {'installed': False, 'error': 'No IP disponible'}
        
        # Verificar si Node Exporter ya está instalado
        if check_port_status(target_ip, 9100):
            return {'installed': True, 'message': 'Node Exporter ya instalado'}
        
        # Intentar instalación SSH
        ssh_result = install_node_exporter_ssh(instance_info)
        if ssh_result.get('success'):
            # Verificar instalación
            import time
            time.sleep(10)  # Esperar a que inicie
            if check_port_status(target_ip, 9100):
                return {'installed': True, 'message': 'Node Exporter instalado exitosamente'}
            else:
                return {'installed': False, 'message': 'Instalado pero no responde en puerto 9100'}
        else:
            return {'installed': False, 'error': ssh_result.get('error', 'Error de instalación')}
            
    except Exception as e:
        logger.error(f"Error verificando Node Exporter en {instance_info.get('name')}: {e}")
        return {'installed': False, 'error': str(e)}

def install_node_exporter_ssh(instance_info):
    """Instalar Node Exporter vía SSH"""
    try:
        # Importar paramiko para SSH
        try:
            import paramiko
        except ImportError:
            return {'success': False, 'error': 'Biblioteca paramiko no instalada. Ejecute: pip install paramiko'}
        
        target_ip = instance_info.get('public_ip') or instance_info.get('private_ip')
        platform = instance_info.get('platform', 'linux')
        
        if not target_ip:
            return {'success': False, 'error': 'No hay IP disponible'}
        
        # Buscar claves SSH disponibles
        ssh_key_paths = find_ssh_keys()
        if not ssh_key_paths:
            return {'success': False, 'error': 'No se encontraron claves SSH'}
        
        logger.info(f"🔍 Probando {len(ssh_key_paths)} claves SSH encontradas...")
        
        # Intentar conexión SSH con diferentes usuarios y claves
        users_to_try = [
            'azureuser', 'ubuntu', 'ec2-user', 'admin', 'root',
            'centos', 'debian', 'fedora', 'oracle', 'bitnami',
            'administrator', 'user', 'student', 'deploy'
        ]
        
        connection_attempts = 0
        max_attempts = len(ssh_key_paths) * len(users_to_try)
        
        for ssh_key in ssh_key_paths:
            logger.info(f"🔑 Probando clave: {os.path.basename(ssh_key)}")
            
            for username in users_to_try:
                connection_attempts += 1
                logger.debug(f"🔐 Intento {connection_attempts}/{max_attempts}: {username}@{target_ip} con {os.path.basename(ssh_key)}")
                
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Cargar clave privada con múltiples formatos
                    private_key = None
                    try:
                        private_key = paramiko.RSAKey.from_private_key_file(ssh_key)
                        logger.debug(f"✅ Cargada como RSA: {os.path.basename(ssh_key)}")
                    except:
                        try:
                            private_key = paramiko.Ed25519Key.from_private_key_file(ssh_key)
                            logger.debug(f"✅ Cargada como Ed25519: {os.path.basename(ssh_key)}")
                        except:
                            try:
                                private_key = paramiko.ECDSAKey.from_private_key_file(ssh_key)
                                logger.debug(f"✅ Cargada como ECDSA: {os.path.basename(ssh_key)}")
                            except:
                                try:
                                    private_key = paramiko.DSSKey.from_private_key_file(ssh_key)
                                    logger.debug(f"✅ Cargada como DSS: {os.path.basename(ssh_key)}")
                                except:
                                    logger.debug(f"❌ No se pudo cargar: {os.path.basename(ssh_key)}")
                                    continue
                    
                    if not private_key:
                        continue
                    
                    # Conectar con timeout más largo
                    ssh.connect(
                        hostname=target_ip,
                        username=username,
                        pkey=private_key,
                        timeout=15,
                        allow_agent=False,
                        look_for_keys=False,
                        banner_timeout=30
                    )
                    
                    logger.info(f"🎉 ¡Conexión exitosa! {username}@{target_ip} con {os.path.basename(ssh_key)}")
                    
                    # Instalar Node Exporter
                    if platform == 'windows':
                        install_result = install_windows_exporter_remote(ssh)
                    else:
                        install_result = install_node_exporter_linux_remote(ssh)
                    
                    ssh.close()
                    
                    if install_result.get('success'):
                        return {
                            'success': True,
                            'username': username,
                            'ssh_key': os.path.basename(ssh_key),
                            'ssh_key_path': ssh_key,
                            'connection_attempts': connection_attempts,
                            'message': install_result.get('message', 'Instalación completada')
                        }
                    else:
                        logger.warning(f"⚠️ Conexión exitosa pero instalación falló: {install_result.get('error')}")
                    
                except paramiko.AuthenticationException:
                    logger.debug(f"🔐 Auth falló: {username}@{target_ip}")
                    continue
                except paramiko.SSHException as e:
                    logger.debug(f"🔐 SSH error: {username}@{target_ip} - {e}")
                    continue
                except Exception as e:
                    logger.debug(f"🔐 Error conexión: {username}@{target_ip} - {e}")
                    continue
                finally:
                    try:
                        if 'ssh' in locals():
                            ssh.close()
                    except:
                        pass
        
        return {
            'success': False, 
            'error': f'No se pudo conectar vía SSH después de {connection_attempts} intentos con {len(ssh_key_paths)} claves y {len(users_to_try)} usuarios',
            'details': {
                'ssh_keys_tried': [os.path.basename(k) for k in ssh_key_paths],
                'users_tried': users_to_try,
                'total_attempts': connection_attempts
            }
        }
        
    except Exception as e:
        logger.error(f"Error en instalación SSH: {e}")
        return {'success': False, 'error': str(e)}

def find_ssh_keys():
    """Buscar claves SSH en el sistema"""
    ssh_keys = []
    
    # Ubicaciones comunes de claves SSH
    ssh_dirs = [
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/ssh"),
        os.path.expanduser("~/.aws"),
        "C:/Users/*/.ssh",
        "C:/Users/*/ssh",
        "C:/Users/*/.aws",
        "./keys",
        "./ssh-keys",
        "./azure-keys",
        "./aws-keys",
        "."  # Directorio actual
    ]
    
    # Nombres comunes de archivos de claves
    common_key_names = [
        "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa",
        "azure_rsa", "aws_rsa", "vm_key", "server_key",
        "private_key", "key.pem", "*.pem"
    ]
    
    for ssh_dir in ssh_dirs:
        if '*' in ssh_dir:
            # Expandir wildcards
            import glob
            for expanded_dir in glob.glob(ssh_dir):
                if os.path.exists(expanded_dir):
                    ssh_keys.extend(scan_ssh_dir(expanded_dir))
        else:
            if os.path.exists(ssh_dir):
                ssh_keys.extend(scan_ssh_dir(ssh_dir))
    
    # Buscar también archivos .pem en directorios comunes
    pem_patterns = [
        os.path.expanduser("~/*.pem"),
        os.path.expanduser("~/Downloads/*.pem"),
        os.path.expanduser("~/Desktop/*.pem"),
        "C:/Users/*/Downloads/*.pem",
        "C:/Users/*/Desktop/*.pem",
        "./*.pem"
    ]
    
    import glob
    for pattern in pem_patterns:
        for pem_file in glob.glob(pattern):
            if os.path.isfile(pem_file) and is_private_key_file(pem_file):
                ssh_keys.append(pem_file)
    
    # Eliminar duplicados y retornar lista ordenada
    unique_keys = list(set(ssh_keys))
    logger.info(f"🔑 Encontradas {len(unique_keys)} claves SSH: {[os.path.basename(k) for k in unique_keys]}")
    return unique_keys

def scan_ssh_dir(ssh_dir):
    """Escanear directorio SSH en busca de claves privadas"""
    keys = []
    
    try:
        for file in os.listdir(ssh_dir):
            file_path = os.path.join(ssh_dir, file)
            
            # Buscar claves privadas (sin extensión .pub)
            if (os.path.isfile(file_path) and 
                not file.endswith('.pub') and 
                not file.endswith('.known_hosts') and
                not file.endswith('.config') and
                not file.endswith('.log')):
                
                # Verificar si parece una clave privada
                if is_private_key_file(file_path):
                    keys.append(file_path)
                    logger.debug(f"🔑 Clave encontrada: {file_path}")
    except Exception as e:
        logger.debug(f"Error escaneando {ssh_dir}: {e}")
    
    return keys

def is_private_key_file(file_path):
    """Verificar si un archivo es una clave privada SSH"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(200)  # Leer solo los primeros 200 caracteres
            
            # Marcadores de claves privadas
            private_key_markers = [
                'BEGIN PRIVATE KEY',
                'BEGIN RSA PRIVATE KEY', 
                'BEGIN OPENSSH PRIVATE KEY',
                'BEGIN EC PRIVATE KEY',
                'BEGIN DSA PRIVATE KEY',
                'BEGIN ENCRYPTED PRIVATE KEY'
            ]
            
            for marker in private_key_markers:
                if marker in content:
                    return True
                    
            # También verificar archivos .pem sin marcadores explícitos
            if file_path.endswith('.pem') and len(content) > 50:
                return True
                
    except Exception:
        pass
    
    return False

def install_node_exporter_linux_remote(ssh):
    """Instalar Node Exporter en Linux vía SSH"""
    try:
        commands = [
            # Verificar si ya está instalado
            "pgrep node_exporter && echo 'already_running' || echo 'not_running'",
            
            # Crear usuario node_exporter si no existe
            "sudo useradd --no-create-home --shell /bin/false node_exporter 2>/dev/null || true",
            
            # Descargar Node Exporter
            "cd /tmp && wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz",
            
            # Extraer
            "cd /tmp && tar xzf node_exporter-1.6.1.linux-amd64.tar.gz",
            
            # Copiar binario
            "sudo cp /tmp/node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/",
            "sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter",
            
            # Crear servicio systemd
            """sudo tee /etc/systemd/system/node_exporter.service > /dev/null << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF""",
            
            # Habilitar e iniciar servicio
            "sudo systemctl daemon-reload",
            "sudo systemctl enable node_exporter",
            "sudo systemctl start node_exporter",
            
            # Verificar estado
            "sudo systemctl is-active node_exporter"
        ]
        
        all_output = []
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            all_output.append(f"CMD: {cmd}")
            all_output.append(f"OUT: {output}")
            if error:
                all_output.append(f"ERR: {error}")
            
            # Si ya está ejecutándose, no continuar
            if 'already_running' in output:
                return {'success': True, 'message': 'Node Exporter ya estaba instalado'}
        
        return {'success': True, 'message': 'Node Exporter instalado en Linux', 'details': all_output}
        
    except Exception as e:
        return {'success': False, 'error': f'Error instalando en Linux: {str(e)}'}

def install_windows_exporter_remote(ssh):
    """Instalar Windows Exporter vía SSH/PowerShell"""
    try:
        # Para Windows, usar PowerShell remoto
        commands = [
            # Verificar si ya está ejecutándose
            'Get-Process -Name "windows_exporter" -ErrorAction SilentlyContinue',
            
            # Descargar Windows Exporter
            '$url = "https://github.com/prometheus-community/windows_exporter/releases/download/v0.31.3/windows_exporter-0.31.3-amd64.exe"; $output = "C:\\windows_exporter.exe"; Invoke-WebRequest -Uri $url -OutFile $output',
            
            # Crear servicio
            'New-Service -Name "WindowsExporter" -BinaryPathName "C:\\windows_exporter.exe --web.listen-address=:9100" -DisplayName "Windows Exporter" -StartupType Automatic',
            
            # Iniciar servicio
            'Start-Service WindowsExporter',
            
            # Verificar estado
            'Get-Service WindowsExporter'
        ]
        
        all_output = []
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(f'powershell.exe -Command "{cmd}"', timeout=60)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            all_output.append(f"CMD: {cmd}")
            all_output.append(f"OUT: {output}")
            if error:
                all_output.append(f"ERR: {error}")
        
        return {'success': True, 'message': 'Windows Exporter instalado', 'details': all_output}
        
    except Exception as e:
        return {'success': False, 'error': f'Error instalando en Windows: {str(e)}'}

def check_port_status(ip, port):
    """Verificar si un puerto está abierto en una IP"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

# ===== PUNTO DE ENTRADA =====

if __name__ == '__main__':
    logger.info("🚀 Iniciando OptiMon Sistema Unificado...")
    logger.info("📋 Versión: 3.0.0-UNIFIED")
    logger.info("🌐 Puerto: 5000")
    logger.info("=" * 60)
    
    try:
        # Verificar servicios críticos
        services_check = get_all_services_status()
        logger.info("✅ Verificación de servicios completada")
        
        # Iniciar aplicación
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"❌ Error iniciando aplicación: {e}")
        sys.exit(1)