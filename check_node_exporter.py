#!/usr/bin/env python3
"""
Verificar Node Exporter en VM remota
"""

import paramiko
from pathlib import Path

def check_node_exporter():
    """Verifica si Node Exporter está funcionando en la VM"""
    
    vm_ip = "172.191.59.230"
    ssh_user = "azureuser"
    key_file = Path.home() / ".ssh" / "vmPruebas01_key.pem"
    
    print(f"🔍 Verificando Node Exporter en {vm_ip}")
    
    try:
        # Conectar por SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        client.connect(
            hostname=vm_ip,
            username=ssh_user,
            key_filename=str(key_file),
            timeout=10
        )
        
        print("✅ Conectado por SSH")
        
        # Verificar si Node Exporter está funcionando
        commands = [
            "sudo systemctl status node_exporter --no-pager",
            "sudo netstat -tlnp | grep 9100",
            "curl -s http://localhost:9100/metrics | head -5"
        ]
        
        for cmd in commands:
            print(f"\n📋 Ejecutando: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if output:
                print(f"✅ Salida:")
                print(output)
            if error:
                print(f"⚠️ Error:")
                print(error)
        
        # Verificar firewall
        print(f"\n🔥 Verificando firewall:")
        stdin, stdout, stderr = client.exec_command("sudo ufw status")
        firewall_status = stdout.read().decode().strip()
        print(firewall_status)
        
        # Intentar abrir puerto si está cerrado
        if "inactive" not in firewall_status.lower():
            print(f"\n🔓 Abriendo puerto 9100 en firewall...")
            stdin, stdout, stderr = client.exec_command("sudo ufw allow 9100")
            result = stdout.read().decode().strip()
            print(result)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_node_exporter()