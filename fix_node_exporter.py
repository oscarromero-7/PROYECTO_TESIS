#!/usr/bin/env python3
"""
Script manual para instalar Node Exporter en instancia problemática
"""

import paramiko
import time
import os

def install_node_exporter_manual():
    """Instala Node Exporter manualmente en la instancia problema"""
    
    # Configuración de la instancia
    HOST = "13.218.228.165"
    USER = "ec2-user"
    KEY_PATH = r"C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\1-CREAR-INFRAESTRUCTURA\Optimon2.pem"
    
    print(f"Conectando a {HOST} como {USER}...")
    
    try:
        # Crear cliente SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar usando la llave privada
        ssh.connect(
            hostname=HOST,
            username=USER,
            key_filename=KEY_PATH,
            timeout=30
        )
        
        print("✅ Conexión SSH exitosa!")
        
        # Comandos para instalar Node Exporter
        commands = [
            # Verificar si ya existe
            "sudo systemctl status node_exporter || echo 'Node Exporter no instalado'",
            
            # Descargar Node Exporter
            "cd /tmp",
            "wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz",
            
            # Extraer y mover
            "tar xzf node_exporter-1.6.1.linux-amd64.tar.gz",
            "sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/",
            "sudo chmod +x /usr/local/bin/node_exporter",
            
            # Crear usuario para node_exporter
            "sudo useradd -rs /bin/false node_exporter || echo 'Usuario ya existe'",
            
            # Crear archivo de servicio systemd
            """sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
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
EOF""",
            
            # Recargar systemd y iniciar servicio
            "sudo systemctl daemon-reload",
            "sudo systemctl enable node_exporter",
            "sudo systemctl restart node_exporter",
            
            # Verificar estado
            "sudo systemctl status node_exporter --no-pager",
            
            # Verificar que esté escuchando en el puerto 9100
            "sleep 5",
            "ss -tulpn | grep :9100 || echo 'Puerto 9100 no encontrado'",
            "curl -s http://localhost:9100/metrics | head -5 || echo 'Node Exporter no responde'"
        ]
        
        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Ejecutando: {cmd[:50]}...")
            
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if output:
                print(f"Output: {output[:200]}...")
            if error and "already exists" not in error.lower():
                print(f"Error: {error[:200]}...")
            
            # Pausa breve entre comandos
            time.sleep(1)
        
        # Verificación final
        print("\n🔍 Verificación final...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9100/metrics | head -3")
        output = stdout.read().decode().strip()
        
        if "node_" in output:
            print("✅ Node Exporter instalado y funcionando correctamente!")
            print("🔗 Métricas disponibles en http://13.218.228.165:9100/metrics")
        else:
            print("❌ Node Exporter no responde correctamente")
            
    except Exception as e:
        print(f"❌ Error durante la instalación: {e}")
        
    finally:
        try:
            ssh.close()
        except:
            pass

if __name__ == "__main__":
    install_node_exporter_manual()