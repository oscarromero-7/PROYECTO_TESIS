#!/usr/bin/env python3
"""
OptiMon - Configurador de Monitoreo Azure
Instala Node Exporter en VMs Azure detectadas
"""

import os
import sys
import yaml
import json
import concurrent.futures
import paramiko
from pathlib import Path
from datetime import datetime

class AzureMonitoringSetup:
    def __init__(self):
        self.config_file = Path("config/azure-credentials.yml")
        self.config = None
        self.compute_client = None
        self.network_client = None
        self.vms = []
        
    def load_config(self):
        """Carga la configuracion Azure"""
        if not self.config_file.exists():
            print("[ERROR] Archivo de configuracion Azure no encontrado")
            print("   Crea config/azure-credentials.yml usando el ejemplo")
            sys.exit(1)
            
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
        print("[OK] Configuracion Azure cargada")
    
    def setup_azure_clients(self):
        """Configura los clientes Azure"""
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
            
            # Clientes
            self.compute_client = ComputeManagementClient(
                credential, 
                self.config['azure']['subscription_id']
            )
            
            self.network_client = NetworkManagementClient(
                credential,
                self.config['azure']['subscription_id']
            )
            
            # Verificar conexion
            list(self.compute_client.resource_skus.list())
            print("[OK] Conexion Azure establecida")
            
        except Exception as e:
            print(f"[ERROR] Error conectando a Azure: {e}")
            sys.exit(1)
    
    def discover_vms(self):
        """Descubre VMs Azure para monitorear"""
        print("[INFO] Descubriendo VMs Azure...")
        
        try:
            # Obtener VMs segun configuracion
            monitoring_config = self.config['azure'].get('monitoring', {})
            resource_groups = monitoring_config.get('resource_groups', [])
            
            if resource_groups:
                # Buscar en grupos especificos
                for rg in resource_groups:
                    vms = list(self.compute_client.virtual_machines.list(rg))
                    for vm in vms:
                        vm_info = self._process_vm(vm, rg)
                        if vm_info:
                            self.vms.append(vm_info)
            else:
                # Buscar en todas las VMs
                vms = list(self.compute_client.virtual_machines.list_all())
                for vm in vms:
                    rg = vm.id.split('/')[4]
                    vm_info = self._process_vm(vm, rg)
                    if vm_info:
                        self.vms.append(vm_info)
            
            print(f"[INFO] {len(self.vms)} VMs encontradas para monitorear")
            
        except Exception as e:
            print(f"[ERROR] Error descubriendo VMs: {e}")
    
    def _process_vm(self, vm, resource_group):
        """Procesa informacion de una VM"""
        if vm.provisioning_state != 'Succeeded':
            return None
        
        # Verificar si debe ser incluida
        if not self._should_monitor_vm(vm):
            return None
        
        # Obtener IP de la VM
        vm_ip = self._get_vm_ip(vm, resource_group)
        if not vm_ip:
            print(f"  [WARN]  {vm.name}: No se pudo obtener IP")
            return None
        
        # Verificar si es Linux (Windows no soportado aun)
        if vm.storage_profile.os_disk.os_type.value.lower() == 'windows':
            print(f"  [WARN]  {vm.name}: VM Windows, saltando (no soportado aun)")
            return None
        
        return {
            'name': vm.name,
            'ip': vm_ip,
            'resource_group': resource_group,
            'location': vm.location,
            'vm_size': vm.hardware_profile.vm_size,
            'os_type': vm.storage_profile.os_disk.os_type.value,
            'tags': vm.tags or {},
            'vm_id': vm.vm_id
        }
    
    def _should_monitor_vm(self, vm):
        """Verifica si una VM debe ser monitorizada"""
        monitoring_config = self.config['azure'].get('monitoring', {})
        
        # Verificar tamanos excluidos
        exclude_sizes = monitoring_config.get('exclude_vm_sizes', [])
        if vm.hardware_profile.vm_size in exclude_sizes:
            return False
        
        # Verificar regiones
        regions = monitoring_config.get('regions', [])
        if regions and vm.location not in regions:
            return False
        
        # Verificar tags de inclusion
        include_tags = monitoring_config.get('include_tags', {})
        if include_tags:
            vm_tags = vm.tags or {}
            for key, value in include_tags.items():
                if vm_tags.get(key) != value:
                    return False
        
        return True
    
    def _get_vm_ip(self, vm, resource_group):
        """Obtiene la IP de una VM Azure"""
        try:
            # Obtener interfaces de red
            for nic_ref in vm.network_profile.network_interfaces:
                nic_name = nic_ref.id.split('/')[-1]
                
                nic = self.network_client.network_interfaces.get(resource_group, nic_name)
                
                for ip_config in nic.ip_configurations:
                    if ip_config.private_ip_address:
                        return ip_config.private_ip_address
                        
        except Exception as e:
            print(f"    Error obteniendo IP para {vm.name}: {e}")
            
        return None
    
    def install_node_exporter_batch(self):
        """Instala Node Exporter en todas las VMs en paralelo"""
        if not self.vms:
            print("[WARN]  No hay VMs para configurar")
            return
        
        print(f"[OptiMon] Instalando Node Exporter en {len(self.vms)} VMs...")
        
        # Usar ThreadPoolExecutor para instalacion paralela
        max_workers = min(5, len(self.vms))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for vm in self.vms:
                future = executor.submit(self._install_node_exporter_single, vm)
                futures.append((future, vm))
            
            # Procesar resultados
            successful = 0
            failed = 0
            
            for future, vm in futures:
                try:
                    result = future.result(timeout=300)  # 5 minutos timeout
                    if result:
                        successful += 1
                        print(f"  [OK] {vm['name']} ({vm['ip']})")
                    else:
                        failed += 1
                        print(f"  [ERROR] {vm['name']} ({vm['ip']})")
                except Exception as e:
                    failed += 1
                    print(f"  [ERROR] {vm['name']} ({vm['ip']}): {e}")
        
        print(f"\n[INFO] Resumen de instalacion:")
        print(f"  [OK] Exitosas: {successful}")
        print(f"  [ERROR] Fallidas: {failed}")
    
    def _install_node_exporter_single(self, vm):
        """Instala Node Exporter en una VM especifica"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Configurar conexion SSH
            ssh_config = self.config['azure']['ssh']
            ssh_user = self._get_ssh_user(vm)
            
            connect_params = {
                'hostname': vm['ip'],
                'username': ssh_user,
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
                print(f"    Error en {vm['name']}: {error_output}")
                return False
                
        except Exception as e:
            print(f"    Error conectando a {vm['name']}: {e}")
            return False
        finally:
            try:
                ssh.close()
            except:
                pass
    
    def _get_ssh_user(self, vm):
        """Determina el usuario SSH apropiado"""
        ssh_config = self.config['azure']['ssh']
        
        # Verificar si hay un usuario especifico en tags
        if 'ssh_user' in vm['tags']:
            return vm['tags']['ssh_user']
        
        # Usar configuracion por OS
        users_by_os = ssh_config.get('users_by_os', {})
        os_type = vm['os_type'].lower()
        
        if os_type == 'linux':
            return users_by_os.get('linux', ssh_config.get('default_user', 'azureuser'))
        
        # Por defecto
        return ssh_config.get('default_user', 'azureuser')
    
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
        """Actualiza la configuracion de Prometheus con las nuevas VMs"""
        print("📝 Actualizando configuracion de Prometheus...")
        
        prometheus_dir = Path("config/prometheus")
        prometheus_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar targets para Prometheus
        targets = []
        for vm in self.vms:
            target = {
                'targets': [f"{vm['ip']}:9100"],
                'labels': {
                    'job': 'node-exporter',
                    'instance': vm['name'],
                    'provider': 'azure',
                    'resource_group': vm['resource_group'],
                    'location': vm['location'],
                    'vm_size': vm['vm_size'],
                    'vm_id': vm['vm_id']
                }
            }
            
            # Anadir tags como labels
            for key, value in vm['tags'].items():
                if key.lower() not in ['name']:
                    target['labels'][f'tag_{key.lower()}'] = value
            
            targets.append(target)
        
        # Guardar targets
        targets_file = prometheus_dir / "azure_targets.json"
        with open(targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
        
        print(f"[OK] Targets Azure guardados en {targets_file}")
        
        # Regenerar configuracion completa de Prometheus
        os.system("python scripts/setup_prometheus.py")
    
    def run(self):
        """Ejecuta la configuracion completa de Azure"""
        print("[OptiMon] OptiMon - Configurador de Monitoreo Azure")
        print("=" * 50)
        
        self.load_config()
        self.setup_azure_clients()
        self.discover_vms()
        
        if self.vms:
            response = input(f"\nInstalar Node Exporter en {len(self.vms)} VMs? (y/N): ")
            if response.lower() in ['y', 'yes', 's', 'si']:
                self.install_node_exporter_batch()
                self.update_prometheus_config()
                print("\n[OK] Configuracion Azure completada")
            else:
                print("⏭️  Instalacion cancelada")
        else:
            print("\n[WARN]  No se encontraron VMs para monitorear")

if __name__ == "__main__":
    try:
        setup = AzureMonitoringSetup()
        setup.run()
    except KeyboardInterrupt:
        print("\n[ERROR] Configuracion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error durante la configuracion: {e}")
        sys.exit(1)