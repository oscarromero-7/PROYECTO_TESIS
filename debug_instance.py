#!/usr/bin/env python3
"""
Diagnóstico específico para instancia problemática
"""

import paramiko
import os
from pathlib import Path

def test_ssh_connection(ip, key_file, username):
    """Test SSH connection with specific parameters"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Probando SSH: {username}@{ip} con clave {key_file}")
        
        client.connect(
            hostname=ip,
            username=username,
            key_filename=key_file,
            timeout=10
        )
        
        # Test simple command
        stdin, stdout, stderr = client.exec_command('whoami && uname -a')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print(f"✅ CONEXIÓN EXITOSA")
        print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
            
        # Check if node_exporter exists
        stdin, stdout, stderr = client.exec_command('ps aux | grep node_exporter')
        ps_output = stdout.read().decode()
        print(f"Procesos node_exporter: {ps_output}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error SSH: {e}")
        return False

def main():
    target_ip = "13.218.228.165"
    
    # SSH keys to try
    potential_keys = [
        "c:/Users/oagr2/Documents/GitHub/PROYECTO_TESIS/1-CREAR-INFRAESTRUCTURA/Optimon2.pem",
        "c:/Users/oagr2/.ssh/id_rsa",
        "c:/Users/oagr2/Downloads/*.pem"
    ]
    
    # Users to try
    users = ['ec2-user', 'ubuntu', 'admin', 'centos']
    
    print(f"=== DIAGNÓSTICO PARA {target_ip} ===")
    
    # Find actual key files
    key_files = []
    for pattern in potential_keys:
        if '*' in pattern:
            import glob
            key_files.extend(glob.glob(pattern))
        elif os.path.exists(pattern):
            key_files.append(pattern)
    
    print(f"Claves encontradas: {key_files}")
    
    # Test combinations
    for key_file in key_files:
        for user in users:
            print(f"\n--- Probando {user} con {key_file} ---")
            if test_ssh_connection(target_ip, key_file, user):
                print(f"🎯 COMBINACIÓN EXITOSA: {user}@{target_ip} con {key_file}")
                break

if __name__ == "__main__":
    main()