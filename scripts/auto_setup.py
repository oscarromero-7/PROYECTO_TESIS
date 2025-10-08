#!/usr/bin/env python3
"""
OptiMon - Auto Configurador Inteligente
Detecta y configura automaticamente toda la infraestructura
"""

import os
import sys
import yaml
import json
import boto3
import paramiko
import concurrent.futures
import socket
import subprocess
import shutil
import glob
import re
from pathlib import Path
from datetime import datetime

class SSHKeyManager:
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"
        self.potential_locations = [
            Path.home() / "Downloads",
            Path.home() / "Desktop", 
            Path.home() / "Documents",
            Path("."),  # Directorio actual del proyecto
        ]
        
        # Patrones de nombres de archivos de claves SSH
        self.key_patterns = [
            "*_key.pem", "*.pem", "*_key", "*key*", 
            "id_rsa", "id_ed25519", "azure*", "aws*",
            "*private*", "*ssh*", "Optimon*"
        ]
    
    def find_ssh_keys_system_wide(self):
        """Busca claves SSH en el sistema"""
        found_keys = []
        
        for location in self.potential_locations:
            if not location.exists():
                continue
                
            try:
                for pattern in self.key_patterns:
                    # Buscar archivos con el patrón
                    for key_file in location.rglob(pattern):
                        if self._is_potential_ssh_key(key_file):
                            found_keys.append(key_file)
                                    
            except (PermissionError, OSError):
                continue
        
        return found_keys
    
    def _is_potential_ssh_key(self, file_path):
        """Verifica si un archivo podría ser una clave SSH"""
        if not file_path.is_file():
            return False
            
        # Verificar tamaño (claves SSH típicamente 1KB-10KB)
        size = file_path.stat().st_size
        if size < 100 or size > 50000:
            return False
        
        try:
            # Leer primeras líneas para verificar formato
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(1000)
                
            # Verificar marcadores de claves SSH
            ssh_markers = [
                '-----BEGIN OPENSSH PRIVATE KEY-----',
                '-----BEGIN RSA PRIVATE KEY-----',
                '-----BEGIN EC PRIVATE KEY-----',
                '-----BEGIN PRIVATE KEY-----',
            ]
            
            return any(marker in first_lines for marker in ssh_markers)
            
        except Exception:
            return False
    
    def setup_ssh_keys_for_vm(self, vm_name, vm_provider):
        """Configura automáticamente las claves SSH para una VM específica"""
        # Crear directorio .ssh si no existe
        self.ssh_dir.mkdir(exist_ok=True)
        
        # Buscar claves en el sistema
        found_keys = self.find_ssh_keys_system_wide()
        
        configured_keys = []
        
        for key_file in found_keys:
            # Determinar nombre de destino
            dest_name = f"{vm_provider}_{vm_name}_key.pem"
            dest_path = self.ssh_dir / dest_name
            
            # Copiar si no existe
            if not dest_path.exists():
                try:
                    shutil.copy2(key_file, dest_path)
                    # Configurar permisos en sistemas Unix-like
                    if os.name != 'nt':
                        os.chmod(dest_path, 0o600)
                    configured_keys.append(dest_path)
                except Exception:
                    continue
            else:
                configured_keys.append(dest_path)
        
        return configured_keys

class IntelligentAutoSetup:
    def __init__(self):
        self.config_file = Path("config/credentials.simple.yml")
        self.config = None
        self.discovered_instances = []
        self.successful_installs = 0
        self.failed_installs = 0
        self.ssh_key_manager = SSHKeyManager()
        
    def load_config(self):
        """Carga configuracion simplificada"""
        if not self.config_file.exists():
            print("[ERROR] Archivo de configuracion no encontrado")
            print("   Crea config/credentials.simple.yml con tus credenciales")
            sys.exit(1)
            
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        print("[OK] Configuracion cargada")
    
    def auto_discover_aws(self):
        """Descubre y configura automaticamente AWS"""
        if 'aws' not in self.config or not self.config['aws'].get('access_key_id'):
            return
            
        print("[CLOUD]  Descubrimiento automatico AWS...")
        
        try:
            ec2 = boto3.client(
                'ec2',
                aws_access_key_id=self.config['aws']['access_key_id'],
                aws_secret_access_key=self.config['aws']['secret_access_key'],
                region_name=self.config['aws']['region']
            )
            
            # Obtener todas las instancias en ejecucion
            response = ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = self._process_aws_instance(ec2, instance)
                    if instance_info:
                        self.discovered_instances.append(instance_info)
            
            print(f"[INFO] AWS: {len([i for i in self.discovered_instances if i['provider'] == 'aws'])} instancias encontradas")
            
        except Exception as e:
            print(f"[ERROR] Error AWS: {e}")
    
    def _process_aws_instance(self, ec2_client, instance):
        """Procesa una instancia AWS automaticamente"""
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        
        # Verificar filtros si existen
        if not self._passes_aws_filters(instance):
            return None
        
        # Obtener informacion de red
        private_ip = instance.get('PrivateIpAddress', '')
        public_ip = instance.get('PublicIpAddress', '')
        
        # Determinar IP a usar (preferir publica)
        target_ip = public_ip if public_ip else private_ip
        if not target_ip:
            return None
        
        # Obtener tags
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        name = tags.get('Name', instance_id)
        
        # Solo Linux por ahora
        platform = instance.get('Platform', 'linux')
        if platform == 'windows':
            return None
        
        # Detectar usuario SSH automaticamente
        ssh_user = self._detect_aws_ssh_user(ec2_client, instance)
        
        # Detectar clave SSH automaticamente
        key_name = instance.get('KeyName')
        
        return {
            'provider': 'aws',
            'instance_id': instance_id,
            'name': name,
            'ip': target_ip,
            'instance_type': instance_type,
            'ssh_user': ssh_user,
            'key_name': key_name,
            'tags': tags,
            'region': self.config['aws']['region']
        }
    
    def _passes_aws_filters(self, instance):
        """Verifica si la instancia pasa los filtros"""
        filters = self.config['aws'].get('filters', {})
        
        # Verificar tipos excluidos
        exclude_types = filters.get('exclude_types', [])
        if instance['InstanceType'] in exclude_types:
            return False
        
        # Verificar tags de inclusion
        include_tags = filters.get('include_tags', [])
        if include_tags:
            instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            for tag_filter in include_tags:
                if '=' in tag_filter:
                    key, value = tag_filter.split('=', 1)
                    if instance_tags.get(key) != value:
                        return False
        
        return True
    
    def _detect_aws_ssh_user(self, ec2_client, instance):
        """Detecta automaticamente el usuario SSH correcto"""
        # Obtener informacion de la AMI
        image_id = instance.get('ImageId', '')
        if not image_id:
            return 'ec2-user'  # Por defecto
        
        try:
            ami_response = ec2_client.describe_images(ImageIds=[image_id])
            if ami_response['Images']:
                ami = ami_response['Images'][0]
                name = ami.get('Name', '').lower()
                description = ami.get('Description', '').lower()
                
                # Detectar basado en nombre/descripcion de AMI
                if 'ubuntu' in name or 'ubuntu' in description:
                    return 'ubuntu'
                elif 'centos' in name or 'centos' in description:
                    return 'centos'
                elif 'rhel' in name or 'redhat' in name:
                    return 'ec2-user'
                elif 'suse' in name:
                    return 'ec2-user'
                elif 'debian' in name:
                    return 'admin'
                elif 'amazon' in name:
                    return 'ec2-user'
                    
        except Exception:
            pass
        
        return 'ec2-user'  # Valor por defecto mas comun
    
    def auto_discover_azure(self):
        """Descubre y configura automaticamente Azure"""
        if 'azure' not in self.config or not self.config['azure'].get('subscription_id'):
            return
            
        print("[CLOUD]  Descubrimiento automatico Azure...")
        
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.network import NetworkManagementClient
            
            # Autenticacion
            credential = ClientSecretCredential(
                tenant_id=self.config['azure']['tenant_id'],
                client_id=self.config['azure']['client_id'],
                client_secret=self.config['azure']['client_secret']
            )
            
            compute_client = ComputeManagementClient(
                credential, 
                self.config['azure']['subscription_id']
            )
            
            network_client = NetworkManagementClient(
                credential,
                self.config['azure']['subscription_id']
            )
            
            # Obtener VMs segun filtros
            vms = self._get_filtered_azure_vms(compute_client)
            
            for vm in vms:
                vm_info = self._process_azure_vm(network_client, vm)
                if vm_info:
                    self.discovered_instances.append(vm_info)
            
            print(f"[INFO] Azure: {len([i for i in self.discovered_instances if i['provider'] == 'azure'])} VMs encontradas")
            
        except Exception as e:
            print(f"[ERROR] Error Azure: {e}")
    
    def _get_filtered_azure_vms(self, compute_client):
        """Obtiene VMs filtradas segun configuracion"""
        filters = self.config['azure'].get('filters', {})
        resource_groups = filters.get('resource_groups', [])
        regions = filters.get('regions', [])
        
        vms = []
        
        if resource_groups:
            # Buscar en grupos especificos
            for rg in resource_groups:
                try:
                    rg_vms = list(compute_client.virtual_machines.list(rg))
                    vms.extend(rg_vms)
                except Exception:
                    continue
        else:
            # Buscar en todas las VMs
            vms = list(compute_client.virtual_machines.list_all())
        
        # Filtrar por region si se especifica
        if regions:
            vms = [vm for vm in vms if vm.location in regions]
        
        # Solo VMs activas y Linux
        filtered_vms = []
        for vm in vms:
            if (vm.provisioning_state == 'Succeeded' and 
                vm.storage_profile.os_disk.os_type.lower() == 'linux'):
                filtered_vms.append(vm)
        
        return filtered_vms
    
    def _process_azure_vm(self, network_client, vm):
        """Procesa una VM Azure automaticamente"""
        rg_name = vm.id.split('/')[4]
        
        # Obtener IP
        vm_ip = self._get_azure_vm_ip(network_client, vm, rg_name)
        if not vm_ip:
            return None
        
        # Detectar usuario SSH automaticamente
        ssh_user = self._detect_azure_ssh_user(vm)
        
        return {
            'provider': 'azure',
            'name': vm.name,
            'ip': vm_ip,
            'resource_group': rg_name,
            'location': vm.location,
            'vm_size': vm.hardware_profile.vm_size,
            'ssh_user': ssh_user,
            'tags': vm.tags or {},
            'vm_id': vm.vm_id
        }
    
    def _get_azure_vm_ip(self, network_client, vm, rg_name):
        """Obtiene IP de VM Azure"""
        try:
            for nic_ref in vm.network_profile.network_interfaces:
                nic_name = nic_ref.id.split('/')[-1]
                nic = network_client.network_interfaces.get(rg_name, nic_name)
                
                for ip_config in nic.ip_configurations:
                    # Preferir IP publica si existe
                    if ip_config.public_ip_address:
                        pip_name = ip_config.public_ip_address.id.split('/')[-1]
                        pip = network_client.public_ip_addresses.get(rg_name, pip_name)
                        if pip.ip_address:
                            return pip.ip_address
                    
                    # Usar IP privada como respaldo
                    if ip_config.private_ip_address:
                        return ip_config.private_ip_address
                        
        except Exception:
            pass
            
        return None
    
    def _detect_azure_ssh_user(self, vm):
        """Detecta automaticamente el usuario SSH para Azure"""
        # Intentar obtener del nombre de la imagen
        try:
            os_profile = vm.os_profile
            if os_profile and os_profile.admin_username:
                return os_profile.admin_username
        except Exception:
            pass
        
        # Detectar basado en el publisher de la imagen
        try:
            image_ref = vm.storage_profile.image_reference
            if image_ref:
                publisher = image_ref.publisher.lower() if image_ref.publisher else ""
                offer = image_ref.offer.lower() if image_ref.offer else ""
                
                if 'canonical' in publisher or 'ubuntu' in offer:
                    return 'azureuser'
                elif 'redhat' in publisher or 'centos' in offer:
                    return 'azureuser'
                elif 'suse' in publisher:
                    return 'azureuser'
        except Exception:
            pass
        
        return 'azureuser'  # Usuario por defecto de Azure
    
    def scan_physical_network(self):
        """Escanea la red local en busca de servidores fisicos"""
        physical_config = self.config.get('physical_servers', {})
        
        # Anadir servidores manuales
        manual_servers = physical_config.get('manual_servers', [])
        for server in manual_servers:
            server_info = {
                'provider': 'physical',
                'name': server.get('name', server['ip']),
                'ip': server['ip'],
                'ssh_user': 'admin'  # Se detectara automaticamente
            }
            self.discovered_instances.append(server_info)
        
        # Escaneo automatico de red (si esta habilitado)
        network_scan = physical_config.get('network_scan', {})
        if network_scan.get('enabled'):
            print("[INFO] Escaneando red local...")
            subnet = network_scan.get('subnet', '192.168.1.0/24')
            self._scan_subnet(subnet, network_scan.get('ssh_users', ['admin', 'ubuntu']))
    
    def _scan_subnet(self, subnet, common_users):
        """Escanea una subred en busca de servidores SSH"""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
            # Limitar escaneo a primeras 50 IPs para velocidad
            ips_to_scan = list(network.hosts())[:50]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for ip in ips_to_scan:
                    future = executor.submit(self._test_ssh_connectivity, str(ip), common_users)
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures, timeout=30):
                    result = future.result()
                    if result:
                        self.discovered_instances.append(result)
                        
        except Exception as e:
            print(f"  [WARN]  Error escaneando red: {e}")
    
    def _test_ssh_connectivity(self, ip, users):
        """Prueba conectividad SSH a una IP"""
        for user in users:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, 22))
                sock.close()
                
                if result == 0:  # Puerto SSH abierto
                    return {
                        'provider': 'physical',
                        'name': f'server-{ip.split(".")[-1]}',
                        'ip': ip,
                        'ssh_user': user
                    }
            except Exception:
                continue
                
        return None
    
    def install_node_exporter_auto(self):
        """Instala Node Exporter automaticamente en todas las instancias"""
        if not self.discovered_instances:
            print("[WARN]  No se encontraron instancias para configurar")
            return
        
        print(f"[OptiMon] Instalando Node Exporter automaticamente en {len(self.discovered_instances)} instancias...")
        
        # Instalacion paralela con deteccion automatica de credenciales
        max_workers = min(10, len(self.discovered_instances))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for instance in self.discovered_instances:
                future = executor.submit(self._auto_install_single, instance)
                futures.append((future, instance))
            
            # Procesar resultados
            for future, instance in futures:
                try:
                    result = future.result(timeout=180)  # 3 minutos por instancia
                    if result:
                        self.successful_installs += 1
                        print(f"  [OK] {instance['name']} ({instance['ip']})")
                    else:
                        self.failed_installs += 1
                        print(f"  [ERROR] {instance['name']} ({instance['ip']})")
                except Exception as e:
                    self.failed_installs += 1
                    print(f"  [ERROR] {instance['name']} ({instance['ip']}): {e}")
    
    def _auto_install_single(self, instance):
        """Instala Node Exporter en una instancia con deteccion automatica"""
        try:
            # Intentar multiples metodos de conexion
            connection_methods = self._get_connection_methods(instance)
            
            for method in connection_methods:
                if self._try_install_with_method(instance, method):
                    return True
            
            return False
            
        except Exception as e:
            print(f"    Error en {instance['name']}: {e}")
            return False
    
    def _get_connection_methods(self, instance):
        """Obtiene metodos de conexion a probar automaticamente"""
        methods = []
        
        # Configurar automáticamente las claves SSH para esta instancia
        print(f"[INFO] Configurando claves SSH automáticamente para {instance['name']}")
        ssh_keys = self.ssh_key_manager.setup_ssh_keys_for_vm(
            instance['name'], 
            instance['provider']
        )
        
        # Obtener todas las claves SSH disponibles en .ssh
        ssh_dir = Path.home() / ".ssh"
        available_keys = []
        
        if ssh_dir.exists():
            for key_file in ssh_dir.iterdir():
                if (key_file.is_file() and 
                    not key_file.name.endswith(('.pub', '.known_hosts', '.config')) and
                    self.ssh_key_manager._is_potential_ssh_key(key_file)):
                    available_keys.append(key_file)
        
        print(f"[INFO] Encontradas {len(available_keys)} claves SSH disponibles")
        
        # Crear métodos de conexión para cada clave encontrada
        for key_file in available_keys:
            methods.append({
                'type': 'key',
                'user': instance['ssh_user'],
                'key_file': str(key_file)
            })
        
        # También buscar claves en el proyecto actual
        project_keys = [
            "./1-CREAR-INFRAESTRUCTURA/Optimon2.pem",
            "./Optimon2.pem",
            f"./{instance['name']}_key.pem"
        ]
        
        for key_path in project_keys:
            if os.path.exists(key_path):
                methods.append({
                    'type': 'key',
                    'user': instance['ssh_user'],
                    'key_file': key_path
                })
        
        # Métodos específicos por proveedor como fallback
        if instance['provider'] == 'azure':
            # Para Azure, probar usuarios comunes
            azure_users = ['azureuser', 'ubuntu', 'admin']
            for user in azure_users:
                for key_file in available_keys:
                    methods.append({
                        'type': 'key',
                        'user': user,
                        'key_file': str(key_file)
                    })
            
        elif instance['provider'] == 'physical':
            # Para físicos, intentar métodos comunes
            common_users = ['admin', 'ubuntu', 'centos', 'user']
            for user in common_users:
                for key_file in available_keys:
                    methods.append({
                        'type': 'key',
                        'user': user,
                        'key_file': str(key_file)
                    })
        
        return methods
    
    def _try_install_with_method(self, instance, method):
        """Intenta instalar con un metodo especifico"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_params = {
                'hostname': instance['ip'],
                'username': method['user'],
                'port': 22,
                'timeout': 30
            }
            
            if method['type'] == 'key' and 'key_file' in method:
                if os.path.exists(method['key_file']):
                    connect_params['key_filename'] = method['key_file']
                else:
                    return False
            
            # Intentar conexion
            ssh.connect(**connect_params)
            
            # Verificar si Node Exporter ya esta instalado
            stdin, stdout, stderr = ssh.exec_command('systemctl is-active node_exporter')
            if stdout.read().decode().strip() == 'active':
                ssh.close()
                return True  # Ya esta instalado
            
            # Instalar Node Exporter
            install_script = self._get_install_script()
            stdin, stdout, stderr = ssh.exec_command(install_script)
            
            exit_status = stdout.channel.recv_exit_status()
            ssh.close()
            
            return exit_status == 0
            
        except Exception:
            return False
    
    def _get_install_script(self):
        """Script de instalacion optimizado"""
        return """#!/bin/bash
set -e

# Verificar si ya esta instalado
if systemctl is-active --quiet node_exporter; then
    echo "Node Exporter ya esta activo"
    exit 0
fi

echo "[INFO] Instalando Node Exporter..."

# Descargar y extraer
cd /tmp
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xzf node_exporter-1.6.1.linux-amd64.tar.gz

# Configurar usuario y directorios
sudo useradd --no-create-home --shell /bin/false node_exporter 2>/dev/null || true
sudo mkdir -p /opt/node_exporter

# Instalar binario
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /opt/node_exporter/
sudo chown node_exporter:node_exporter /opt/node_exporter/node_exporter
sudo chmod +x /opt/node_exporter/node_exporter

# Crear servicio systemd
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/opt/node_exporter/node_exporter --web.listen-address=:9100
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

echo "[OK] Node Exporter instalado y activo"
"""
    
    def update_prometheus_config(self):
        """Actualiza automaticamente la configuracion de Prometheus"""
        print("📝 Actualizando configuracion de Prometheus...")
        
        prometheus_dir = Path("config/prometheus")
        prometheus_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar configuracion completa
        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'rule_files': ['alert.rules.yml'],
            'alerting': {
                'alertmanagers': [{
                    'static_configs': [{'targets': ['alertmanager:9093']}]
                }]
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [{'targets': ['localhost:9090']}]
                }
            ]
        }
        
        # Anadir targets por proveedor
        if self.discovered_instances:
            static_configs = []
            
            for instance in self.discovered_instances:
                target = {
                    'targets': [f"{instance['ip']}:9100"],
                    'labels': {
                        'job': 'node-exporter',
                        'instance': instance['name'],
                        'provider': instance['provider'],
                        'ip': instance['ip']
                    }
                }
                
                # Anadir labels especificos por proveedor
                if instance['provider'] == 'aws':
                    target['labels'].update({
                        'instance_id': instance.get('instance_id', ''),
                        'instance_type': instance.get('instance_type', ''),
                        'region': instance.get('region', '')
                    })
                elif instance['provider'] == 'azure':
                    target['labels'].update({
                        'resource_group': instance.get('resource_group', ''),
                        'location': instance.get('location', ''),
                        'vm_size': instance.get('vm_size', '')
                    })
                
                static_configs.append(target)
            
            config['scrape_configs'].append({
                'job_name': 'node-exporter',
                'static_configs': static_configs,
                'scrape_interval': '15s'
            })
        
        # Guardar configuracion
        config_file = prometheus_dir / "prometheus.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Crear reglas de alertas basicas
        self._create_alert_rules()
        
        print("[OK] Configuracion de Prometheus actualizada")
    
    def _create_alert_rules(self):
        """Crea reglas de alertas basicas"""
        rules = {
            'groups': [{
                'name': 'optimon-alerts',
                'rules': [
                    {
                        'alert': 'InstanceDown',
                        'expr': 'up == 0',
                        'for': '2m',
                        'labels': {'severity': 'critical'},
                        'annotations': {
                            'summary': 'Instancia {{ $labels.instance }} no disponible',
                            'description': 'La instancia {{ $labels.instance }} esta caida'
                        }
                    },
                    {
                        'alert': 'HighCPU',
                        'expr': '100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80',
                        'for': '2m',
                        'labels': {'severity': 'warning'},
                        'annotations': {
                            'summary': 'Alto uso de CPU en {{ $labels.instance }}',
                            'description': 'CPU al {{ $value }}%'
                        }
                    },
                    {
                        'alert': 'HighMemory',
                        'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90',
                        'for': '2m',
                        'labels': {'severity': 'warning'},
                        'annotations': {
                            'summary': 'Alto uso de memoria en {{ $labels.instance }}',
                            'description': 'Memoria al {{ $value }}%'
                        }
                    }
                ]
            }]
        }
        
        rules_file = Path("config/prometheus/alert.rules.yml")
        with open(rules_file, 'w') as f:
            yaml.dump(rules, f, default_flow_style=False, indent=2)
    
    def setup_dashboards(self):
        """Configura automáticamente los dashboards de Grafana"""
        print("🎨 Configurando dashboards de Grafana...")
        
        try:
            import requests
            import time
            
            # Esperar a que Grafana esté disponible
            grafana_url = "http://localhost:3000"
            max_attempts = 30
            
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{grafana_url}/api/health", timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    else:
                        print("   [WARN] Grafana no está disponible, dashboards no configurados")
                        return
            
            session = requests.Session()
            session.auth = ('admin', 'admin')
            
            # Configurar datasource de Prometheus si no existe
            response = session.get(f"{grafana_url}/api/datasources/name/Prometheus")
            if response.status_code != 200:
                datasource_config = {
                    "name": "Prometheus",
                    "type": "prometheus", 
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True,
                    "basicAuth": False
                }
                session.post(f"{grafana_url}/api/datasources", json=datasource_config)
            
            # Importar dashboards
            dashboard_dir = Path("config/grafana/dashboards")
            if dashboard_dir.exists():
                dashboard_files = list(dashboard_dir.glob("*.json"))
                
                for dashboard_file in dashboard_files:
                    try:
                        with open(dashboard_file, 'r', encoding='utf-8') as f:
                            dashboard_json = json.load(f)
                        
                        import_payload = {
                            "dashboard": dashboard_json,
                            "overwrite": True,
                            "inputs": [],
                            "folderId": 0
                        }
                        
                        response = session.post(
                            f"{grafana_url}/api/dashboards/db",
                            json=import_payload
                        )
                        
                        if response.status_code in [200, 201]:
                            print(f"   ✅ Dashboard importado: {dashboard_file.stem}")
                        
                    except Exception as e:
                        print(f"   [WARN] Error importando {dashboard_file.stem}: {e}")
                
                print(f"[OK] Dashboards configurados en {grafana_url}")
            
        except ImportError:
            print("   [WARN] Módulo requests no disponible, dashboards no configurados")
        except Exception as e:
            print(f"   [WARN] Error configurando dashboards: {e}")
    
    def show_summary(self):
        """Muestra resumen final"""
        print("\n" + "="*60)
        print("[SUCCESS] CONFIGURACION AUTOMATICA COMPLETADA")
        print("="*60)
        
        print(f"\n[INFO] Resumen de descubrimiento:")
        providers = {}
        for instance in self.discovered_instances:
            provider = instance['provider']
            if provider not in providers:
                providers[provider] = 0
            providers[provider] += 1
        
        for provider, count in providers.items():
            print(f"  - {provider.upper()}: {count} instancias")
        
        print(f"\n[OptiMon] Resumen de instalacion:")
        print(f"  [OK] Exitosas: {self.successful_installs}")
        print(f"  [ERROR] Fallidas: {self.failed_installs}")
        
        if self.successful_installs > 0:
            print(f"\n[INFO] Acceso a servicios:")
            print("  - Grafana:      http://localhost:3000 (admin/admin)")
            print("  - Prometheus:   http://localhost:9090")
            print("  - AlertManager: http://localhost:9093")
            
            print(f"\n[OK] {self.successful_installs} servidores monitoreandose automaticamente!")
        else:
            print("\n[WARN]  No se pudo instalar Node Exporter en ninguna instancia")
            print("Verifica:")
            print("  - Conectividad SSH a las instancias")
            print("  - Claves SSH disponibles")
            print("  - Permisos de las instancias")
    
    def run(self):
        """Ejecuta el proceso completo automatico"""
        print("[INFO] OptiMon - Configuracion 100% Automatica")
        print("=" * 50)
        
        self.load_config()
        self.auto_discover_aws()
        self.auto_discover_azure()
        self.scan_physical_network()
        
        if self.discovered_instances:
            print(f"\n🎯 Total encontrado: {len(self.discovered_instances)} instancias")
            
            # Mostrar lo que se encontro
            for instance in self.discovered_instances:
                print(f"  - {instance['name']} ({instance['provider']}) - {instance['ip']}")
            
            print("\n[OptiMon] Iniciando instalacion automatica...")
            self.install_node_exporter_auto()
            self.update_prometheus_config()
            self.setup_dashboards()
            
        else:
            print("\n[WARN]  No se encontraron instancias para monitorear")
            print("Verifica las credenciales en config/credentials.simple.yml")
        
        self.show_summary()

if __name__ == "__main__":
    try:
        setup = IntelligentAutoSetup()
        setup.run()
    except KeyboardInterrupt:
        print("\n[ERROR] Configuracion interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)