#!/usr/bin/env python3
"""
Instalador automático de Node Exporter para servidores Linux
Parte del sistema OptiMon Multi-Servidor
"""

import subprocess
import socket
import json
import os
from concurrent.futures import ThreadPoolExecutor
import paramiko
import time

class NodeExporterInstaller:
    def __init__(self):
        self.node_exporter_version = "1.6.1"
        self.node_exporter_url = f"https://github.com/prometheus/node_exporter/releases/download/v{self.node_exporter_version}/node_exporter-{self.node_exporter_version}.linux-amd64.tar.gz"
        
    def install_on_server(self, server_ip, username, password=None, key_file=None, port=22):
        """Instala Node Exporter en un servidor Linux remoto"""
        
        print(f"[INFO] Instalando Node Exporter en {server_ip}")
        
        try:
            # Conectar vía SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_file:
                ssh.connect(server_ip, port=port, username=username, key_filename=key_file)
            else:
                ssh.connect(server_ip, port=port, username=username, password=password)
            
            # Script de instalación
            install_script = f"""
#!/bin/bash
set -e

echo "[INFO] Descargando Node Exporter..."
cd /tmp
wget -q {self.node_exporter_url} -O node_exporter.tar.gz

echo "[INFO] Extrayendo archivos..."
tar xzf node_exporter.tar.gz

echo "[INFO] Copiando binario..."
sudo cp node_exporter-{self.node_exporter_version}.linux-amd64/node_exporter /usr/local/bin/
sudo chmod +x /usr/local/bin/node_exporter

echo "[INFO] Creando usuario node_exporter..."
sudo useradd -rs /bin/false node_exporter 2>/dev/null || true

echo "[INFO] Creando servicio systemd..."
sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[INFO] Habilitando y iniciando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

echo "[INFO] Verificando estado..."
sudo systemctl status node_exporter --no-pager -l

echo "[INFO] Configurando firewall..."
if command -v ufw >/dev/null; then
    sudo ufw allow 9100/tcp 2>/dev/null || true
elif command -v firewall-cmd >/dev/null; then
    sudo firewall-cmd --permanent --add-port=9100/tcp 2>/dev/null || true
    sudo firewall-cmd --reload 2>/dev/null || true
fi

echo "[INFO] Limpiando archivos temporales..."
rm -rf /tmp/node_exporter*

echo "[SUCCESS] Node Exporter instalado exitosamente"
echo "Endpoint disponible en: http://{server_ip}:9100/metrics"
"""
            
            # Ejecutar script de instalación
            stdin, stdout, stderr = ssh.exec_command(install_script)
            
            # Leer salida
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            print(f"[OK] Node Exporter instalado en {server_ip}")
            
            # Verificar que está funcionando
            time.sleep(5)  # Esperar a que inicie
            if self._verify_node_exporter(server_ip, 9100):
                print(f"[OK] Node Exporter verificado en {server_ip}:9100")
                return True
            else:
                print(f"[WARNING] Node Exporter instalado pero no responde en {server_ip}:9100")
                return False
            
            ssh.close()
            
        except Exception as e:
            print(f"[ERROR] Error instalando en {server_ip}: {e}")
            return False
    
    def _verify_node_exporter(self, ip, port, timeout=10):
        """Verifica que Node Exporter esté respondiendo"""
        try:
            import requests
            response = requests.get(f"http://{ip}:{port}/metrics", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def install_multiple_servers(self, servers_config):
        """Instala Node Exporter en múltiples servidores en paralelo"""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            
            for server_id, config in servers_config.items():
                if config.get('type') == 'linux' and config.get('auto_install', False):
                    future = executor.submit(
                        self.install_on_server,
                        config['ip'],
                        config.get('username', 'root'),
                        config.get('password'),
                        config.get('key_file'),
                        config.get('ssh_port', 22)
                    )
                    futures[future] = server_id
            
            for future in futures:
                server_id = futures[future]
                try:
                    success = future.result()
                    results[server_id] = success
                except Exception as e:
                    results[server_id] = False
                    print(f"[ERROR] Error procesando {server_id}: {e}")
        
        return results

def generate_install_commands():
    """Genera comandos de instalación para copiar/pegar"""
    
    install_commands = {
        "ubuntu_debian": """
# Instalación automática Node Exporter - Ubuntu/Debian
sudo apt update
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
sudo ufw allow 9100/tcp
""",

        "centos_rhel": """
# Instalación automática Node Exporter - CentOS/RHEL
sudo yum update -y
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
sudo firewall-cmd --permanent --add-port=9100/tcp
sudo firewall-cmd --reload
""",

        "docker": """
# Node Exporter con Docker
docker run -d \\
  --name=node_exporter \\
  --restart=unless-stopped \\
  --net="host" \\
  --pid="host" \\
  -v "/:/host:ro,rslave" \\
  prom/node-exporter:latest \\
  --path.rootfs=/host
"""
    }
    
    return install_commands

def create_deployment_guide():
    """Crea guía de despliegue para diferentes escenarios"""
    
    guide = """
# OptiMon - Guía de Instalación de Exporters

## Prerrequisitos por Servidor

### Servidores Windows
- **Windows Exporter ya instalado** (puerto 9182)
- Descargar desde: https://github.com/prometheus-community/windows_exporter/releases
- Ejecutar como servicio

### Servidores Linux
- Acceso SSH con privilegios sudo
- Puerto 9100 abierto en firewall
- Node Exporter se instala automáticamente

### Docker Hosts
- Docker instalado y ejecutándose
- Acceso a Docker daemon
- Puerto 9100 disponible

## Configuración de Red

Para que OptiMon pueda monitorear los servidores:

1. **Firewall**: Abrir puertos de exporters
   - Windows: Puerto 9182
   - Linux: Puerto 9100
   - Docker: Puerto 9100

2. **Conectividad**: Desde el servidor OptiMon debe poder acceder a:
   - IP_SERVIDOR:PUERTO_EXPORTER

3. **DNS/Hosts**: Configurar resolución de nombres si es necesario

## Proceso de Configuración Recomendado

1. **Instalar exporters en servidores objetivo**
2. **Ejecutar OptiMon setup.bat**
3. **Usar opción 1 para configurar inventario**
4. **Usar opción 5 para escaneo multi-servidor**

## Verificación Manual

Para verificar que un exporter funciona:
```bash
curl http://IP_SERVIDOR:PUERTO/metrics
```

Debe devolver métricas en formato Prometheus.
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("[OK] Guía de despliegue creada: DEPLOYMENT_GUIDE.md")

def main():
    """Función principal del instalador"""
    installer = NodeExporterInstaller()
    
    print("OptiMon - Instalador Node Exporter")
    print("==================================")
    print()
    print("[1] Instalar en servidor individual")
    print("[2] Instalar desde inventario de servidores") 
    print("[3] Generar comandos de instalación")
    print("[4] Crear guía de despliegue")
    print("[0] Salir")
    
    option = input("\nSelecciona opción: ").strip()
    
    if option == "1":
        # Instalación individual
        ip = input("IP del servidor: ").strip()
        username = input("Usuario SSH [root]: ").strip() or "root"
        
        use_key = input("¿Usar clave SSH? (y/N): ").lower() == 'y'
        if use_key:
            key_file = input("Ruta a la clave privada: ").strip()
            password = None
        else:
            import getpass
            password = getpass.getpass("Contraseña SSH: ")
            key_file = None
        
        success = installer.install_on_server(ip, username, password, key_file)
        if success:
            print(f"\n[OK] Instalación completada en {ip}")
        else:
            print(f"\n[ERROR] Falló la instalación en {ip}")
    
    elif option == "2":
        # Instalación desde inventario
        if not os.path.exists("server_inventory.json"):
            print("[ERROR] No se encuentra server_inventory.json")
            print("Ejecuta primero la configuración de inventario")
            return
        
        with open("server_inventory.json", 'r') as f:
            servers = json.load(f)
        
        linux_servers = {k: v for k, v in servers.items() if v.get('type') == 'linux'}
        
        if not linux_servers:
            print("[INFO] No hay servidores Linux configurados para instalación automática")
            return
        
        print(f"[INFO] Instalando en {len(linux_servers)} servidores Linux...")
        results = installer.install_multiple_servers(linux_servers)
        
        print("\n=== Resultados ===")
        for server_id, success in results.items():
            status = "✓ OK" if success else "✗ ERROR"
            print(f"{server_id}: {status}")
    
    elif option == "3":
        # Generar comandos
        commands = generate_install_commands()
        
        print("\n=== COMANDOS DE INSTALACIÓN ===")
        for system, command in commands.items():
            print(f"\n--- {system.upper().replace('_', '/')} ---")
            print(command)
    
    elif option == "4":
        # Crear guía
        create_deployment_guide()
    
    elif option == "0":
        return
    
    else:
        print("Opción inválida")

if __name__ == "__main__":
    main()