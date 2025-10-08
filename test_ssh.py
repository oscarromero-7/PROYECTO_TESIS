#!/usr/bin/env python3
"""
Test SSH Connection to Azure VM
"""

import os
import paramiko
import socket
from pathlib import Path

def test_ssh_connection():
    """Prueba la conexión SSH a la VM de Azure"""
    
    vm_ip = "172.191.59.230"
    possible_users = ["azureuser", "ubuntu", "admin", "root"]
    ssh_port = 22
    
    print(f"🔍 Probando conexión SSH a {vm_ip}:{ssh_port}")
    
    # Buscar claves SSH
    ssh_dir = Path.home() / ".ssh"
    key_files = []
    
    if ssh_dir.exists():
        for key_file in ssh_dir.glob("*"):
            if key_file.is_file() and not key_file.name.endswith(('.pub', '.known_hosts', '.config')):
                key_files.append(key_file)
    
    print(f"📁 Claves SSH encontradas: {len(key_files)}")
    for key_file in key_files:
        print(f"  - {key_file}")
    
    # Probar conectividad de red primero
    print(f"\n🌐 Probando conectividad de red...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((vm_ip, ssh_port))
        sock.close()
        
        if result == 0:
            print("✅ Puerto SSH (22) está abierto")
        else:
            print("❌ Puerto SSH (22) no está accesible")
            print("   Verifica:")
            print("   1. La VM está encendida")
            print("   2. El NSG permite SSH desde tu IP")
            print("   3. La IP es correcta")
            return
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return
    
    # Probar cada combinación usuario/clave
    print(f"\n🔑 Probando autenticación SSH...")
    
    for user in possible_users:
        print(f"\n👤 Probando usuario: {user}")
        
        for key_file in key_files:
            print(f"  🔐 Probando clave: {key_file.name}")
            
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                client.connect(
                    hostname=vm_ip,
                    port=ssh_port,
                    username=user,
                    key_filename=str(key_file),
                    timeout=10,
                    auth_timeout=10
                )
                
                # Probar comando
                stdin, stdout, stderr = client.exec_command('whoami')
                whoami = stdout.read().decode().strip()
                
                print(f"    ✅ ¡ÉXITO! Conectado como {whoami}")
                print(f"    Usuario: {user}")
                print(f"    Clave: {key_file}")
                
                # Probar si puede ejecutar sudo
                stdin, stdout, stderr = client.exec_command('sudo -n whoami')
                sudo_result = stdout.read().decode().strip()
                if sudo_result == 'root':
                    print(f"    ✅ Sudo disponible sin contraseña")
                else:
                    print(f"    ⚠️ Sudo requiere contraseña")
                
                client.close()
                return
                
            except paramiko.AuthenticationException:
                print(f"    ❌ Autenticación fallida")
            except paramiko.SSHException as e:
                print(f"    ❌ Error SSH: {e}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    print(f"\n❌ No se pudo conectar con ninguna combinación")
    print(f"\nPara solucionarlo:")
    print(f"1. Verifica que tienes la clave SSH privada de la VM")
    print(f"2. Copia la clave SSH a ~/.ssh/ (ej: ~/.ssh/azure_key)")
    print(f"3. Ajusta permisos: chmod 600 ~/.ssh/azure_key")
    print(f"4. Verifica el usuario SSH correcto (normalmente 'azureuser')")

if __name__ == "__main__":
    test_ssh_connection()