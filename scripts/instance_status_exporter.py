#!/usr/bin/env python3
"""
Exportador de estado de instancias para Prometheus
Genera métricas sobre todas las instancias detectadas vs funcionando
"""

import yaml
import json
import time
import boto3
from pathlib import Path
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class InstanceStatusExporter:
    def __init__(self):
        self.config_file = Path("config/credentials.simple.yml")
        self.discovered_instances = []
        self.metrics_data = {}
        
    def load_config(self):
        """Carga configuración"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
    
    def discover_all_instances(self):
        """Descubre todas las instancias como lo hace auto_setup.py"""
        self.discovered_instances = []
        
        # AWS
        if 'aws' in self.config and self.config['aws'].get('access_key_id'):
            try:
                ec2 = boto3.client(
                    'ec2',
                    aws_access_key_id=self.config['aws']['access_key_id'],
                    aws_secret_access_key=self.config['aws']['secret_access_key'],
                    region_name=self.config['aws'].get('region', 'us-east-1')
                )
                
                response = ec2.describe_instances(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
                )
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), instance['InstanceId'])
                        
                        self.discovered_instances.append({
                            'name': name,
                            'ip': instance.get('PublicIpAddress', instance.get('PrivateIpAddress', 'Unknown')),
                            'provider': 'aws',
                            'instance_id': instance['InstanceId'],
                            'instance_type': instance['InstanceType'],
                            'region': instance['Placement']['AvailabilityZone'][:-1]
                        })
            except Exception as e:
                print(f"Error discovering AWS: {e}")
        
        # Azure
        if 'azure' in self.config and self.config['azure'].get('subscription_id'):
            try:
                from azure.identity import ClientSecretCredential
                from azure.mgmt.compute import ComputeManagementClient
                from azure.mgmt.network import NetworkManagementClient
                
                credential = ClientSecretCredential(
                    tenant_id=self.config['azure']['tenant_id'],
                    client_id=self.config['azure']['client_id'],
                    client_secret=self.config['azure']['client_secret']
                )
                
                compute_client = ComputeManagementClient(credential, self.config['azure']['subscription_id'])
                network_client = NetworkManagementClient(credential, self.config['azure']['subscription_id'])
                
                for vm in compute_client.virtual_machines.list_all():
                    if vm.provisioning_state == 'Succeeded':
                        # Obtener IP pública
                        try:
                            nic_id = vm.network_profile.network_interfaces[0].id
                            nic_name = nic_id.split('/')[-1]
                            resource_group = nic_id.split('/')[4]
                            
                            nic = network_client.network_interfaces.get(resource_group, nic_name)
                            public_ip = 'No Public IP'
                            
                            if nic.ip_configurations[0].public_ip_address:
                                pip_id = nic.ip_configurations[0].public_ip_address.id
                                pip_name = pip_id.split('/')[-1]
                                pip_resource_group = pip_id.split('/')[4]
                                
                                pip = network_client.public_ip_addresses.get(pip_resource_group, pip_name)
                                public_ip = pip.ip_address or nic.ip_configurations[0].private_ip_address
                            else:
                                public_ip = nic.ip_configurations[0].private_ip_address
                                
                        except Exception:
                            public_ip = 'Unknown IP'
                        
                        self.discovered_instances.append({
                            'name': vm.name,
                            'ip': public_ip,
                            'provider': 'azure',
                            'resource_group': vm.id.split('/')[4],
                            'vm_size': vm.hardware_profile.vm_size,
                            'location': vm.location
                        })
                        
            except ImportError:
                print("Azure SDK not available")
            except Exception as e:
                print(f"Error discovering Azure: {e}")
    
    def generate_metrics(self):
        """Genera métricas de Prometheus"""
        metrics = []
        
        # Métrica: Total de instancias descubiertas por proveedor
        metrics.append("# HELP optimon_discovered_instances_total Total instances discovered by provider")
        metrics.append("# TYPE optimon_discovered_instances_total gauge")
        
        providers = {}
        for instance in self.discovered_instances:
            provider = instance['provider']
            providers[provider] = providers.get(provider, 0) + 1
        
        for provider, count in providers.items():
            metrics.append(f'optimon_discovered_instances_total{{provider="{provider}"}} {count}')
        
        # Métrica: Estado esperado de cada instancia (1 = debería estar UP)
        metrics.append("\n# HELP optimon_instance_expected Expected state of each discovered instance")
        metrics.append("# TYPE optimon_instance_expected gauge")
        
        for instance in self.discovered_instances:
            labels = f'instance="{instance["name"]}",ip="{instance["ip"]}",provider="{instance["provider"]}"'
            if instance['provider'] == 'aws':
                labels += f',instance_id="{instance.get("instance_id", "")}",instance_type="{instance.get("instance_type", "")}",region="{instance.get("region", "")}"'
            elif instance['provider'] == 'azure':
                labels += f',resource_group="{instance.get("resource_group", "")}",vm_size="{instance.get("vm_size", "")}",location="{instance.get("location", "")}"'
            
            metrics.append(f'optimon_instance_expected{{{labels}}} 1')
        
        # Métrica: Problemas de SSH detectados
        metrics.append("\n# HELP optimon_ssh_issues SSH connectivity issues by instance")
        metrics.append("# TYPE optimon_ssh_issues gauge")
        
        # Esto lo actualizaremos cuando tengamos datos de SSH
        for instance in self.discovered_instances:
            labels = f'instance="{instance["name"]}",ip="{instance["ip"]}",provider="{instance["provider"]}"'
            # Por defecto, asumir que puede tener problemas si no está en up{}
            metrics.append(f'optimon_ssh_issues{{{labels}}} 0')
        
        return '\n'.join(metrics)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, exporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            metrics = self.exporter.generate_metrics()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suprimir logs del servidor HTTP
        pass

def run_exporter():
    """Ejecuta el exportador de métricas"""
    exporter = InstanceStatusExporter()
    exporter.load_config()
    
    def update_metrics():
        while True:
            exporter.discover_all_instances()
            time.sleep(60)  # Actualizar cada minuto
    
    # Ejecutar descubrimiento inicial
    exporter.discover_all_instances()
    print(f"🔍 Exportador iniciado: {len(exporter.discovered_instances)} instancias detectadas")
    
    # Iniciar hilo de actualización
    update_thread = threading.Thread(target=update_metrics, daemon=True)
    update_thread.start()
    
    # Crear handler con referencia al exporter
    handler = lambda *args, **kwargs: MetricsHandler(exporter, *args, **kwargs)
    
    # Iniciar servidor HTTP
    server = HTTPServer(('localhost', 9101), handler)
    print("📊 Métricas disponibles en http://localhost:9101/metrics")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo exportador...")
        server.shutdown()

if __name__ == "__main__":
    run_exporter()