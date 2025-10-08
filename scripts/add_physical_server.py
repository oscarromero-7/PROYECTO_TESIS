#!/usr/bin/env python3
"""
OptiMon - Añadir Servidor Físico
Script para añadir servidores físicos al monitoreo
"""

import argparse
import yaml
import sys
import os
import json
import paramiko
from pathlib import Path
from datetime import datetime

class PhysicalServerManager:
    def __init__(self):
        self.config_file = Path("config/physical-servers.yml")
        self.prometheus_dir = Path("config/prometheus")
        self.servers = []
        
    def load_existing_servers(self):
        """Carga servidores existentes"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.servers = data.get('servers', [])
        
    def add_server(self, name, ip, user, port=22, password=None, key_file=None):
        """Añade un nuevo servidor"""
        # Verificar que el servidor no exista ya
        for server in self.servers:
            if server['name'] == name or server['ip'] == ip:
                print(f"❌ Servidor {name} ({ip}) ya existe")
                return False
        
        # Configurar método de autenticación
        auth_method = "password" if password else "key"
        
        server_config = {
            'name': name,
            'ip': ip,
            'user': user,
            'port': port,
            'auth_method': auth_method,
            'os': 'linux',  # Por defecto
            'added_date': datetime.now().isoformat()
        }
        
        if password:
            server_config['password'] = password
        if key_file:
            server_config['key_file'] = key_file
        
        # Probar conexión
        if self.test_connection(server_config):
            self.servers.append(server_config)
            self.save_servers()
            print(f"✅ Servidor {name} añadido exitosamente")
            return True
        else:
            print(f"❌ No se pudo conectar al servidor {name}")
            return False
    
    def test_connection(self, server_config):
        """Prueba la conexión SSH al servidor"""
        print(f"🔍 Probando conexión a {server_config['name']} ({server_config['ip']})...")
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_params = {
                'hostname': server_config['ip'],
                'username': server_config['user'],
                'port': server_config['port'],
                'timeout': 10
            }
            
            if server_config['auth_method'] == 'password':
                connect_params['password'] = server_config['password']
            else:
                connect_params['key_filename'] = server_config['key_file']
            
            ssh.connect(**connect_params)
            
            # Probar un comando simple
            stdin, stdout, stderr = ssh.exec_command('echo "test"')
            if stdout.read().decode().strip() == "test":
                ssh.close()
                return True
            else:
                ssh.close()
                return False
                
        except Exception as e:
            print(f"  Error de conexión: {e}")
            return False
    
    def install_node_exporter(self, server_config):
        """Instala Node Exporter en el servidor"""
        print(f"🚀 Instalando Node Exporter en {server_config['name']}...")
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_params = {
                'hostname': server_config['ip'],
                'username': server_config['user'],
                'port': server_config['port'],
                'timeout': 30
            }
            
            if server_config['auth_method'] == 'password':
                connect_params['password'] = server_config['password']
            else:
                connect_params['key_filename'] = server_config['key_file']
            
            ssh.connect(**connect_params)
            
            # Script de instalación
            install_script = """#!/bin/bash
set -e

echo "[INFO] Instalando Node Exporter..."

# Descargar Node Exporter
cd /tmp
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz

# Extraer
tar xzf node_exporter-1.6.1.linux-amd64.tar.gz

# Crear usuario del servicio
sudo useradd --no-create-home --shell /bin/false node_exporter 2>/dev/null || true

# Crear directorios
sudo mkdir -p /opt/node_exporter

# Copiar binario
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

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

# Verificar estado
sudo systemctl is-active node_exporter

echo "[OK] Node Exporter instalado y ejecutándose"
"""
            
            # Ejecutar instalación
            stdin, stdout, stderr = ssh.exec_command(install_script)
            
            # Esperar a que termine
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                print(f"  ✅ Node Exporter instalado en {server_config['name']}")
                ssh.close()
                return True
            else:
                error_output = stderr.read().decode()
                print(f"  ❌ Error instalando: {error_output}")
                ssh.close()
                return False
                
        except Exception as e:
            print(f"  ❌ Error de conexión: {e}")
            return False
    
    def save_servers(self):
        """Guarda la configuración de servidores"""
        config_data = {
            'servers': self.servers,
            'updated_at': datetime.now().isoformat()
        }
        
        # Crear directorio si no existe
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def update_prometheus_config(self):
        """Actualiza la configuración de Prometheus"""
        print("📝 Actualizando configuración de Prometheus...")
        
        # Generar targets para servidores físicos
        targets = []
        for server in self.servers:
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
            targets.append(target)
        
        # Guardar targets
        self.prometheus_dir.mkdir(parents=True, exist_ok=True)
        targets_file = self.prometheus_dir / "physical_targets.json"
        
        with open(targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
        
        print(f"✅ Targets físicos guardados en {targets_file}")
        
        # Regenerar configuración completa de Prometheus
        if Path("scripts/setup_prometheus.py").exists():
            os.system("python scripts/setup_prometheus.py")
    
    def list_servers(self):
        """Lista todos los servidores configurados"""
        if not self.servers:
            print("📋 No hay servidores físicos configurados")
            return
        
        print("📋 Servidores físicos configurados:")
        print("-" * 50)
        
        for i, server in enumerate(self.servers, 1):
            print(f"{i}. {server['name']}")
            print(f"   IP: {server['ip']}")
            print(f"   Usuario: {server['user']}")
            print(f"   Puerto: {server['port']}")
            print(f"   Autenticación: {server['auth_method']}")
            print(f"   Añadido: {server.get('added_date', 'Desconocido')}")
            print()
    
    def remove_server(self, name):
        """Elimina un servidor"""
        for i, server in enumerate(self.servers):
            if server['name'] == name:
                removed = self.servers.pop(i)
                self.save_servers()
                self.update_prometheus_config()
                print(f"✅ Servidor {name} eliminado")
                return True
        
        print(f"❌ Servidor {name} no encontrado")
        return False

def main():
    parser = argparse.ArgumentParser(description='OptiMon - Gestor de Servidores Físicos')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Añadir servidor')
    add_parser.add_argument('--name', required=True, help='Nombre del servidor')
    add_parser.add_argument('--ip', required=True, help='Dirección IP')
    add_parser.add_argument('--user', required=True, help='Usuario SSH')
    add_parser.add_argument('--port', type=int, default=22, help='Puerto SSH (por defecto: 22)')
    add_parser.add_argument('--password', help='Contraseña SSH')
    add_parser.add_argument('--key', help='Archivo de clave privada SSH')
    add_parser.add_argument('--install', action='store_true', help='Instalar Node Exporter automáticamente')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar servidores')
    
    # Comando remove
    remove_parser = subparsers.add_parser('remove', help='Eliminar servidor')
    remove_parser.add_argument('--name', required=True, help='Nombre del servidor a eliminar')
    
    # Comando install
    install_parser = subparsers.add_parser('install', help='Instalar Node Exporter en servidor existente')
    install_parser.add_argument('--name', required=True, help='Nombre del servidor')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PhysicalServerManager()
    manager.load_existing_servers()
    
    if args.command == 'add':
        if not args.password and not args.key:
            print("❌ Debes especificar --password o --key para autenticación")
            return
        
        success = manager.add_server(
            name=args.name,
            ip=args.ip,
            user=args.user,
            port=args.port,
            password=args.password,
            key_file=args.key
        )
        
        if success:
            manager.update_prometheus_config()
            
            if args.install:
                # Buscar el servidor recién añadido
                server_config = next((s for s in manager.servers if s['name'] == args.name), None)
                if server_config:
                    manager.install_node_exporter(server_config)
    
    elif args.command == 'list':
        manager.list_servers()
    
    elif args.command == 'remove':
        manager.remove_server(args.name)
    
    elif args.command == 'install':
        server_config = next((s for s in manager.servers if s['name'] == args.name), None)
        if server_config:
            manager.install_node_exporter(server_config)
        else:
            print(f"❌ Servidor {args.name} no encontrado")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)