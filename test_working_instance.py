#!/usr/bin/env python3
"""
Verificar cuál instancia AWS funciona para comparar
"""

import paramiko
from paramiko import RSAKey

def test_working_instance():
    """Test connection to working AWS instance"""
    
    # Working instance
    working_ip = "3.85.203.242"  # OptiMon-EC2
    key_file = "c:/Users/oagr2/Documents/GitHub/PROYECTO_TESIS/1-CREAR-INFRAESTRUCTURA/Optimon2.pem"
    users = ['ec2-user', 'ubuntu', 'admin', 'centos']
    
    print(f"=== PROBANDO INSTANCIA QUE FUNCIONA: {working_ip} ===")
    
    for user in users:
        try:
            print(f"\n--- Probando {user} ---")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            key = RSAKey.from_private_key_file(key_file)
            
            client.connect(
                hostname=working_ip,
                username=user,
                pkey=key,
                timeout=10
            )
            
            stdin, stdout, stderr = client.exec_command('whoami && cat /etc/os-release | head -3')
            output = stdout.read().decode()
            
            print(f"✅ FUNCIONA con {user}: {output}")
            client.close()
            return user
            
        except Exception as e:
            print(f"❌ {user}: {e}")
    
    return None

def check_problematic_instance_with_working_user(working_user):
    """Try problematic instance with working user"""
    problem_ip = "13.218.228.165"  # Proyecto-tesis
    key_file = "c:/Users/oagr2/Documents/GitHub/PROYECTO_TESIS/1-CREAR-INFRAESTRUCTURA/Optimon2.pem"
    
    print(f"\n=== PROBANDO INSTANCIA PROBLEMÁTICA CON USER CORRECTO ===")
    print(f"Usando usuario que funciona: {working_user}")
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key = RSAKey.from_private_key_file(key_file)
        
        client.connect(
            hostname=problem_ip,
            username=working_user,
            pkey=key,
            timeout=10
        )
        
        stdin, stdout, stderr = client.exec_command('whoami && cat /etc/os-release | head -3')
        output = stdout.read().decode()
        
        print(f"✅ FUNCIONA: {output}")
        
        # Check node_exporter status
        stdin, stdout, stderr = client.exec_command('ps aux | grep node_exporter | grep -v grep')
        ps_output = stdout.read().decode()
        print(f"Node Exporter running: {ps_output}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

if __name__ == "__main__":
    working_user = test_working_instance()
    if working_user:
        check_problematic_instance_with_working_user(working_user)
    else:
        print("❌ No se pudo encontrar usuario que funcione")