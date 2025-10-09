#!/usr/bin/env python3
"""
Corrección del problema de formato de clave SSH
"""

import paramiko
import os
from pathlib import Path

def test_ssh_with_rsa_fix(ip, key_file, username):
    """Test SSH with RSA key format fix"""
    try:
        # Try different key loading methods
        from paramiko import RSAKey, Ed25519Key, ECDSAKey
        
        print(f"Probando SSH: {username}@{ip} con clave {key_file}")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try to load the key explicitly as RSA
        try:
            key = RSAKey.from_private_key_file(key_file)
            print("✅ Clave RSA cargada exitosamente")
        except Exception as e:
            print(f"❌ Error cargando RSA key: {e}")
            return False
        
        client.connect(
            hostname=ip,
            username=username,
            pkey=key,
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
            
        # Check if node_exporter exists or is running
        stdin, stdout, stderr = client.exec_command('ps aux | grep node_exporter | grep -v grep')
        ps_output = stdout.read().decode()
        print(f"Procesos node_exporter: {ps_output}")
        
        # Check if node_exporter binary exists
        stdin, stdout, stderr = client.exec_command('which node_exporter || find /usr/local/bin /opt -name "*node_exporter*" 2>/dev/null')
        binary_output = stdout.read().decode()
        print(f"Binario node_exporter: {binary_output}")
        
        # Check systemd service
        stdin, stdout, stderr = client.exec_command('systemctl status node_exporter 2>/dev/null || echo "No systemd service"')
        service_output = stdout.read().decode()
        print(f"Servicio node_exporter: {service_output}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error SSH: {e}")
        return False

def main():
    target_ip = "13.218.228.165"
    key_file = "c:/Users/oagr2/Documents/GitHub/PROYECTO_TESIS/1-CREAR-INFRAESTRUCTURA/Optimon2.pem"
    users = ['ec2-user', 'ubuntu', 'admin', 'centos']
    
    print(f"=== DIAGNÓSTICO CORREGIDO PARA {target_ip} ===")
    
    # Test combinations with RSA fix
    for user in users:
        print(f"\n--- Probando {user} con RSA key fix ---")
        if test_ssh_with_rsa_fix(target_ip, key_file, user):
            print(f"🎯 COMBINACIÓN EXITOSA: {user}@{target_ip}")
            break

if __name__ == "__main__":
    main()