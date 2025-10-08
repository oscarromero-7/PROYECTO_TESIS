#!/usr/bin/env python3
"""
OptiMon - Configurador de Prometheus
Genera configuracion de Prometheus basada en infraestructura detectada
"""

import os
import sys
import yaml
import json
from datetime import datetime
from pathlib import Path

class PrometheusConfigGenerator:
    def __init__(self):
        self.config_dir = Path("config")
        self.prometheus_dir = self.config_dir / "prometheus"
        self.prometheus_dir.mkdir(parents=True, exist_ok=True)
        
        self.targets = []
        self.static_configs = []
        
    def load_credentials(self):
        """Carga las credenciales configuradas"""
        aws_creds = self.config_dir / "aws-credentials.yml"
        azure_creds = self.config_dir / "azure-credentials.yml"
        
        self.aws_config = None
        self.azure_config = None
        
        if aws_creds.exists():
            with open(aws_creds, 'r') as f:
                self.aws_config = yaml.safe_load(f)
                print("[OK] Configuracion AWS cargada")
        
        if azure_creds.exists():
            with open(azure_creds, 'r') as f:
                self.azure_config = yaml.safe_load(f)
                print("[OK] Configuracion Azure cargada")
                
        if not self.aws_config and not self.azure_config:
            print("[WARN]  No se encontraron credenciales de nube configuradas")
    
    def discover_aws_instances(self):
        """Descubre instancias AWS para monitorear"""
        if not self.aws_config:
            return
            
        print("[INFO] Descubriendo instancias AWS...")
        
        try:
            import boto3
            
            ec2 = boto3.client(
                'ec2',
                aws_access_key_id=self.aws_config['aws']['access_key_id'],
                aws_secret_access_key=self.aws_config['aws']['secret_access_key'],
                region_name=self.aws_config['aws']['region']
            )
            
            # Obtener instancias en ejecucion
            response = ec2.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']}
                ]
            )
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    private_ip = instance.get('PrivateIpAddress', '')
                    public_ip = instance.get('PublicIpAddress', '')
                    instance_id = instance['InstanceId']
                    
                    # Obtener tags
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    name = tags.get('Name', instance_id)
                    
                    # Decidir que IP usar
                    target_ip = public_ip if public_ip else private_ip
                    
                    if target_ip:
                        target = {
                            'targets': [f"{target_ip}:9100"],
                            'labels': {
                                'job': 'node-exporter',
                                'instance': name,
                                'provider': 'aws',
                                'instance_id': instance_id,
                                'region': self.aws_config['aws']['region'],
                                'instance_type': instance['InstanceType']
                            }
                        }
                        
                        # Anadir tags como labels
                        for key, value in tags.items():
                            if key.lower() not in ['name']:
                                target['labels'][f'tag_{key.lower()}'] = value
                        
                        self.static_configs.append(target)
                        print(f"  [OK] {name} ({target_ip})")
            
            print(f"[INFO] {len([c for c in self.static_configs if c['labels'].get('provider') == 'aws'])} instancias AWS encontradas")
            
        except Exception as e:
            print(f"[ERROR] Error descubriendo instancias AWS: {e}")
    
    def discover_azure_vms(self):
        """Descubre VMs Azure para monitorear"""
        if not self.azure_config:
            return
            
        print("[INFO] Descubriendo VMs Azure...")
        
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.network import NetworkManagementClient
            
            # Autenticacion
            credential = ClientSecretCredential(
                tenant_id=self.azure_config['azure']['tenant_id'],
                client_id=self.azure_config['azure']['client_id'],
                client_secret=self.azure_config['azure']['client_secret']
            )
            
            compute_client = ComputeManagementClient(
                credential, 
                self.azure_config['azure']['subscription_id']
            )
            
            network_client = NetworkManagementClient(
                credential,
                self.azure_config['azure']['subscription_id']
            )
            
            # Obtener VMs
            vms = list(compute_client.virtual_machines.list_all())
            
            for vm in vms:
                if vm.provisioning_state != 'Succeeded':
                    continue
                    
                # Obtener IP de la VM
                vm_ip = self._get_azure_vm_ip(network_client, vm)
                
                if vm_ip:
                    target = {
                        'targets': [f"{vm_ip}:9100"],
                        'labels': {
                            'job': 'node-exporter',
                            'instance': vm.name,
                            'provider': 'azure',
                            'resource_group': vm.id.split('/')[4],
                            'location': vm.location,
                            'vm_size': vm.hardware_profile.vm_size
                        }
                    }
                    
                    # Anadir tags si existen
                    if vm.tags:
                        for key, value in vm.tags.items():
                            target['labels'][f'tag_{key.lower()}'] = value
                    
                    self.static_configs.append(target)
                    print(f"  [OK] {vm.name} ({vm_ip})")
            
            print(f"[INFO] {len([c for c in self.static_configs if c['labels'].get('provider') == 'azure'])} VMs Azure encontradas")
            
        except Exception as e:
            print(f"[ERROR] Error descubriendo VMs Azure: {e}")
    
    def _get_azure_vm_ip(self, network_client, vm):
        """Obtiene la IP de una VM Azure"""
        try:
            # Obtener interfaces de red
            for nic_ref in vm.network_profile.network_interfaces:
                nic_name = nic_ref.id.split('/')[-1]
                rg_name = nic_ref.id.split('/')[4]
                
                nic = network_client.network_interfaces.get(rg_name, nic_name)
                
                for ip_config in nic.ip_configurations:
                    if ip_config.private_ip_address:
                        return ip_config.private_ip_address
                        
        except Exception as e:
            print(f"  [WARN]  Error obteniendo IP para {vm.name}: {e}")
            
        return None
    
    def add_physical_servers(self):
        """Anade servidores fisicos configurados"""
        creds_file = self.config_dir / "credentials.example.yml"
        if not creds_file.exists():
            return
            
        try:
            with open(creds_file, 'r') as f:
                config = yaml.safe_load(f)
                
            physical = config.get('physical_servers', {})
            servers = physical.get('servers', [])
            
            if not servers:
                return
                
            print("[INFO] Anadiendo servidores fisicos...")
            
            for server in servers:
                target = {
                    'targets': [f"{server['ip']}:9100"],
                    'labels': {
                        'job': 'node-exporter',
                        'instance': server['name'],
                        'provider': 'physical',
                        'ip': server['ip'],
                        'os': server.get('os', 'linux')
                    }
                }
                
                self.static_configs.append(target)
                print(f"  [OK] {server['name']} ({server['ip']})")
            
            print(f"[INFO] {len(servers)} servidores fisicos anadidos")
            
        except Exception as e:
            print(f"[ERROR] Error anadiendo servidores fisicos: {e}")
    
    def generate_prometheus_config(self):
        """Genera la configuracion de Prometheus"""
        print("📝 Generando configuracion de Prometheus...")
        
        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'rule_files': [
                'alert.rules.yml'
            ],
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {
                                'targets': ['alertmanager:9093']
                            }
                        ]
                    }
                ]
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {
                            'targets': ['localhost:9090']
                        }
                    ]
                }
            ]
        }
        
        # Anadir configuracion para node-exporter si hay targets
        if self.static_configs:
            config['scrape_configs'].append({
                'job_name': 'node-exporter',
                'static_configs': self.static_configs,
                'scrape_interval': '15s',
                'metrics_path': '/metrics'
            })
        
        # Guardar configuracion
        config_file = self.prometheus_dir / "prometheus.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"[OK] Configuracion guardada en {config_file}")
        
        # Generar archivo de targets para debugging
        targets_file = self.prometheus_dir / "targets.json"
        with open(targets_file, 'w') as f:
            json.dump(self.static_configs, f, indent=2)
        
        print(f"[OK] Targets guardados en {targets_file}")
    
    def generate_alert_rules(self):
        """Genera reglas de alertas"""
        print("[ALERT] Generando reglas de alertas...")
        
        alerts = {
            'groups': [
                {
                    'name': 'node-exporter',
                    'rules': [
                        {
                            'alert': 'InstanceDown',
                            'expr': 'up == 0',
                            'for': '5m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'Instancia {{ $labels.instance }} no disponible',
                                'description': 'La instancia {{ $labels.instance }} ha estado no disponible por mas de 5 minutos.'
                            }
                        },
                        {
                            'alert': 'HighCPUUsage',
                            'expr': '100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80',
                            'for': '2m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'Alto uso de CPU en {{ $labels.instance }}',
                                'description': 'CPU en {{ $labels.instance }} esta al {{ $value }}% durante mas de 2 minutos.'
                            }
                        },
                        {
                            'alert': 'HighMemoryUsage',
                            'expr': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90',
                            'for': '2m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'Alto uso de memoria en {{ $labels.instance }}',
                                'description': 'Memoria en {{ $labels.instance }} esta al {{ $value }}% durante mas de 2 minutos.'
                            }
                        },
                        {
                            'alert': 'HighDiskUsage',
                            'expr': '(1 - node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100 > 85',
                            'for': '5m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'Alto uso de disco en {{ $labels.instance }}',
                                'description': 'Disco {{ $labels.mountpoint }} en {{ $labels.instance }} esta al {{ $value }}%.'
                            }
                        }
                    ]
                }
            ]
        }
        
        alerts_file = self.prometheus_dir / "alert.rules.yml"
        with open(alerts_file, 'w') as f:
            yaml.dump(alerts, f, default_flow_style=False, indent=2)
        
        print(f"[OK] Reglas de alertas guardadas en {alerts_file}")
    
    def generate_summary(self):
        """Genera un resumen de la configuracion"""
        print("\n[INFO] Resumen de configuracion:")
        print("=" * 50)
        
        providers = {}
        for config in self.static_configs:
            provider = config['labels'].get('provider', 'unknown')
            if provider not in providers:
                providers[provider] = 0
            providers[provider] += 1
        
        total_targets = len(self.static_configs)
        print(f"Total de targets: {total_targets}")
        
        for provider, count in providers.items():
            print(f"  - {provider.upper()}: {count} instancias")
        
        if total_targets == 0:
            print("\n[WARN]  No se encontraron targets para monitorear")
            print("   Verifica que:")
            print("   - Las credenciales esten configuradas correctamente")
            print("   - Las instancias/VMs esten en ejecucion")
            print("   - Los filtros de configuracion sean correctos")
        else:
            print(f"\n[OK] Configuracion lista para {total_targets} targets")
    
    def run(self):
        """Ejecuta la configuracion completa"""
        print("[OptiMon] OptiMon - Configurador de Prometheus")
        print("=" * 50)
        
        self.load_credentials()
        self.discover_aws_instances()
        self.discover_azure_vms()
        self.add_physical_servers()
        self.generate_prometheus_config()
        self.generate_alert_rules()
        self.generate_summary()

if __name__ == "__main__":
    try:
        generator = PrometheusConfigGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n[ERROR] Configuracion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error durante la configuracion: {e}")
        sys.exit(1)