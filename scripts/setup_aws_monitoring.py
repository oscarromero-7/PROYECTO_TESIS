#!/usr/bin/env python3
"""
OptiMon - Configurador de Monitoreo AWS
Instala Node Exporter en instancias AWS detectadas
"""

import os
import sys
import yaml
import json
import boto3
import paramiko
import concurrent.futures
from pathlib import Path
from datetime import datetime

class AWSMonitoringSetup:
    def __init__(self):
        self.config_file = Path("config/aws-credentials.yml")
        self.config = None
        self.ec2_client = None
        self.instances = []
        
    def load_config(self):
        """Carga la configuracion AWS"""
        if not self.config_file.exists():
            print("[ERROR] Archivo de configuracion AWS no encontrado")
            print("   Crea config/aws-credentials.yml usando el ejemplo")
            sys.exit(1)
            
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
        print("[OK] Configuracion AWS cargada")
    
    def setup_aws_client(self):
        """Configura el cliente AWS"""
        try:
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=self.config['aws']['access_key_id'],
                aws_secret_access_key=self.config['aws']['secret_access_key'],
                region_name=self.config['aws']['region']
            )
            
            # Verificar conexion
            self.ec2_client.describe_regions()
            print("[OK] Conexion AWS establecida")
            
        except Exception as e:
            print(f"[ERROR] Error conectando a AWS: {e}")
            sys.exit(1)
    
    def discover_instances(self):
        """Descubre instancias AWS para monitorear"""
        print("[INFO] Descubriendo instancias AWS...")
        
        try:
            # Construir filtros
            filters = [
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
            
            # Anadir filtros personalizados si existen
            if 'monitoring' in self.config['aws'] and 'instance_filters' in self.config['aws']['monitoring']:
                filters.extend(self.config['aws']['monitoring']['instance_filters'])
            
            response = self.ec2_client.describe_instances(Filters=filters)
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = self._process_instance(instance)
                    if instance_info:
                        self.instances.append(instance_info)
            
            print(f"[INFO] {len(self.instances)} instancias encontradas para monitorear")
            
        except Exception as e:
            print(f"[ERROR] Error descubriendo instancias: {e}")
    
    def _process_instance(self, instance):
        """Procesa informacion de una instancia"""
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        
        # Obtener IPs
        private_ip = instance.get('PrivateIpAddress', '')
        public_ip = instance.get('PublicIpAddress', '')
        
        # Obtener tags
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        name = tags.get('Name', instance_id)
        
        # Verificar si debe ser incluida
        if not self._should_monitor_instance(instance, tags):
            return None
        
        # Determinar metodo de conexion
        target_ip = public_ip if public_ip else private_ip
        if not target_ip:
            print(f"  [WARN]  {name}: No se pudo determinar IP")
            return None
        
        # Determinar usuario SSH
        platform = instance.get('Platform', 'linux')
        if platform == 'windows':
            print(f"  [WARN]  {name}: Instancia Windows, saltando (no soportado aun)")
            return None
        
        ssh_user = self._get_ssh_user(instance, tags)
        
        return {
            'instance_id': instance_id,
            'name': name,
            'ip': target_ip,
            'private_ip': private_ip,
            'public_ip': public_ip,
            'instance_type': instance_type,
            'platform': platform,
            'ssh_user': ssh_user,
            'tags': tags
        }
    
    def _should_monitor_instance(self, instance, tags):
        """Verifica si una instancia debe ser monitorizada"""
        # Verificar tipos excluidos
        monitoring_config = self.config['aws'].get('monitoring', {})
        exclude_types = monitoring_config.get('exclude_instance_types', [])
        
        if instance['InstanceType'] in exclude_types:
            return False
        
        # Verificar tags de inclusion
        include_tags = monitoring_config.get('include_tags', [])
        if include_tags:
            for tag_filter in include_tags:
                if '=' in tag_filter:
                    key, value = tag_filter.split('=', 1)
                    if tags.get(key) != value:
                        return False
                else:
                    if tag_filter not in tags:
                        return False
        
        return True
    
    def _get_ssh_user(self, instance, tags):
        """Determina el usuario SSH apropiado"""
        ssh_config = self.config['aws'].get('ssh', {})
        
        # Verificar si hay un usuario especifico en tags
        if 'ssh_user' in tags:
            return tags['ssh_user']
        
        # Usar configuracion por OS
        image_id = instance.get('ImageId', '')
        if image_id:
            try:
                # Obtener informacion de la AMI
                ami_response = self.ec2_client.describe_images(ImageIds=[image_id])
                if ami_response['Images']:
                    ami = ami_response['Images'][0]
                    name = ami.get('Name', '').lower()
                    
                    users_by_os = ssh_config.get('users_by_os', {})
                    
                    if 'ubuntu' in name:
                        return users_by_os.get('ubuntu', 'ubuntu')
                    elif 'centos' in name:
                        return users_by_os.get('centos', 'centos')
                    elif 'rhel' in name or 'redhat' in name:
                        return users_by_os.get('rhel', 'ec2-user')
                    elif 'suse' in name:
                        return users_by_os.get('suse', 'ec2-user')
                    
            except Exception:
                pass
        
        # Usuario por defecto
        return ssh_config.get('default_user', 'ec2-user')
    
    def install_node_exporter_batch(self):
        """Instala Node Exporter en todas las instancias en paralelo"""
        if not self.instances:
            print("[WARN]  No hay instancias para configurar")
            return
        
        print(f"[OptiMon] Instalando Node Exporter en {len(self.instances)} instancias...")
        
        # Usar ThreadPoolExecutor para instalacion paralela
        max_workers = min(5, len(self.instances))  # Maximo 5 conexiones paralelas
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for instance in self.instances:
                future = executor.submit(self._install_node_exporter_single, instance)
                futures.append((future, instance))
            
            # Procesar resultados
            successful = 0
            failed = 0
            
            for future, instance in futures:
                try:
                    result = future.result(timeout=300)  # 5 minutos timeout
                    if result:
                        successful += 1
                        print(f"  [OK] {instance['name']} ({instance['ip']})")
                    else:
                        failed += 1
                        print(f"  [ERROR] {instance['name']} ({instance['ip']})")
                except Exception as e:
                    failed += 1
                    print(f"  [ERROR] {instance['name']} ({instance['ip']}): {e}")
        
        print(f"\n[INFO] Resumen de instalacion:")
        print(f"  [OK] Exitosas: {successful}")
        print(f"  [ERROR] Fallidas: {failed}")
    
    def _install_node_exporter_single(self, instance):
        """Instala Node Exporter en una instancia especifica"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Configurar conexion SSH
            ssh_config = self.config['aws']['ssh']
            connect_params = {
                'hostname': instance['ip'],
                'username': instance['ssh_user'],
                'port': ssh_config.get('port', 22),
                'timeout': 30
            }
            
            # Usar clave SSH si esta configurada
            if 'key_file' in ssh_config:
                connect_params['key_filename'] = ssh_config['key_file']
            
            ssh.connect(**connect_params)
            
            # Script de instalacion
            install_script = self._get_install_script()
            
            # Ejecutar instalacion
            stdin, stdout, stderr = ssh.exec_command(install_script)
            
            # Esperar a que termine
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                return True
            else:
                error_output = stderr.read().decode()
                print(f"    Error en {instance['name']}: {error_output}")
                return False
                
        except Exception as e:
            print(f"    Error conectando a {instance['name']}: {e}")
            return False
        finally:
            try:
                ssh.close()
            except:
                pass
    
    def _get_install_script(self):
        """Genera el script de instalacion de Node Exporter"""
        node_config = self.config.get('general', {}).get('node_exporter', {})
        version = node_config.get('version', '1.6.1')
        port = node_config.get('port', 9100)
        install_path = node_config.get('install_path', '/opt/node_exporter')
        service_user = node_config.get('service_user', 'node_exporter')
        
        return f"""#!/bin/bash
set -e

echo "[INFO] Instalando Node Exporter v{version}..."

# Descargar Node Exporter
cd /tmp
wget -q https://github.com/prometheus/node_exporter/releases/download/v{version}/node_exporter-{version}.linux-amd64.tar.gz

# Extraer
tar xzf node_exporter-{version}.linux-amd64.tar.gz

# Crear usuario del servicio
sudo useradd --no-create-home --shell /bin/false {service_user} 2>/dev/null || true

# Crear directorios
sudo mkdir -p {install_path}

# Copiar binario
sudo cp node_exporter-{version}.linux-amd64/node_exporter {install_path}/
sudo chown {service_user}:{service_user} {install_path}/node_exporter
sudo chmod +x {install_path}/node_exporter

# Crear servicio systemd
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User={service_user}
Group={service_user}
Type=simple
ExecStart={install_path}/node_exporter --web.listen-address=:{port}
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

# Verificar estado
sudo systemctl is-active node_exporter

echo "[OK] Node Exporter instalado y ejecutandose en puerto {port}"
"""
    
    def update_prometheus_config(self):
        """Actualiza la configuracion de Prometheus con las nuevas instancias"""
        print("📝 Actualizando configuracion de Prometheus...")
        
        prometheus_dir = Path("config/prometheus")
        prometheus_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar targets para Prometheus
        targets = []
        for instance in self.instances:
            target = {
                'targets': [f"{instance['ip']}:9100"],
                'labels': {
                    'job': 'node-exporter',
                    'instance': instance['name'],
                    'provider': 'aws',
                    'instance_id': instance['instance_id'],
                    'instance_type': instance['instance_type'],
                    'region': self.config['aws']['region']
                }
            }
            
            # Anadir tags como labels
            for key, value in instance['tags'].items():
                if key.lower() not in ['name']:
                    target['labels'][f'tag_{key.lower()}'] = value
            
            targets.append(target)
        
        # Guardar targets
        targets_file = prometheus_dir / "aws_targets.json"
        with open(targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
        
        print(f"[OK] Targets AWS guardados en {targets_file}")
        
        # Regenerar configuracion completa de Prometheus
        os.system("python scripts/setup_prometheus.py")
    
    def run(self):
        """Ejecuta la configuracion completa de AWS"""
        print("[OptiMon] OptiMon - Configurador de Monitoreo AWS")
        print("=" * 50)
        
        self.load_config()
        self.setup_aws_client()
        self.discover_instances()
        
        if self.instances:
            response = input(f"\nInstalar Node Exporter en {len(self.instances)} instancias? (y/N): ")
            if response.lower() in ['y', 'yes', 's', 'si']:
                self.install_node_exporter_batch()
                self.update_prometheus_config()
                print("\n[OK] Configuracion AWS completada")
            else:
                print("⏭️  Instalacion cancelada")
        else:
            print("\n[WARN]  No se encontraron instancias para monitorear")

if __name__ == "__main__":
    try:
        setup = AWSMonitoringSetup()
        setup.run()
    except KeyboardInterrupt:
        print("\n[ERROR] Configuracion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error durante la configuracion: {e}")
        sys.exit(1)