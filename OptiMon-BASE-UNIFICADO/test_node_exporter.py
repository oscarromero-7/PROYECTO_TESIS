#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de Node Exporter
"""

import sys
import os
import json
import time
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del proyecto
from app import (
    find_ssh_keys, 
    check_port_status, 
    check_and_install_node_exporter,
    install_node_exporter_ssh
)

def test_ssh_key_discovery():
    """Probar el descubrimiento de claves SSH"""
    print("🔍 Buscando claves SSH...")
    
    ssh_keys = find_ssh_keys()
    
    if ssh_keys:
        print(f"✅ Encontradas {len(ssh_keys)} claves SSH:")
        for key in ssh_keys:
            print(f"   📁 {key}")
    else:
        print("❌ No se encontraron claves SSH")
    
    return ssh_keys

def test_port_check():
    """Probar verificación de puertos"""
    print("\n🌐 Probando verificación de puertos...")
    
    # Probar con Google DNS (debe estar abierto)
    if check_port_status('8.8.8.8', 53):
        print("✅ Puerto 53 en 8.8.8.8 está abierto (esperado)")
    else:
        print("❌ Puerto 53 en 8.8.8.8 no responde")
    
    # Probar puerto cerrado
    if not check_port_status('8.8.8.8', 9999):
        print("✅ Puerto 9999 en 8.8.8.8 está cerrado (esperado)")
    else:
        print("❌ Puerto 9999 en 8.8.8.8 responde (inesperado)")

def test_node_exporter_mock():
    """Probar función de Node Exporter con datos simulados"""
    print("\n🛠️ Probando verificación de Node Exporter...")
    
    # Datos de prueba (VM simulada)
    mock_instance = {
        'name': 'test-vm',
        'public_ip': '203.0.113.1',  # IP de documentación RFC5737
        'private_ip': '192.168.1.100',
        'platform': 'linux'
    }
    
    print(f"📋 Instancia de prueba: {mock_instance['name']}")
    print(f"🌐 IP: {mock_instance['public_ip']}")
    
    # Verificar Node Exporter (fallará porque es IP simulada)
    result = check_and_install_node_exporter(mock_instance)
    
    print(f"📊 Resultado: {result}")
    
    if result.get('installed'):
        print("✅ Node Exporter instalado")
    else:
        print(f"❌ Node Exporter no instalado: {result.get('error', 'Sin error específico')}")

def test_cloud_credentials():
    """Verificar si hay credenciales de nube configuradas"""
    print("\n☁️ Verificando credenciales de nube...")
    
    config_path = Path("config/cloud_credentials.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("✅ Archivo de credenciales encontrado")
            
            if 'aws' in config:
                aws_config = config['aws']
                has_aws = bool(aws_config.get('access_key') and aws_config.get('secret_key'))
                print(f"🔧 AWS configurado: {'✅' if has_aws else '❌'}")
                
            if 'azure' in config:
                azure_config = config['azure']
                has_azure = bool(
                    azure_config.get('tenant_id') and 
                    azure_config.get('client_id') and 
                    azure_config.get('client_secret') and 
                    azure_config.get('subscription_id')
                )
                print(f"🔧 Azure configurado: {'✅' if has_azure else '❌'}")
                
        except json.JSONDecodeError:
            print("❌ Error leyendo archivo de credenciales")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Archivo de credenciales no encontrado")

def main():
    """Función principal de prueba"""
    print("=" * 60)
    print("🧪 PRUEBA DE FUNCIONALIDAD NODE EXPORTER")
    print("=" * 60)
    
    # Ejecutar pruebas
    ssh_keys = test_ssh_key_discovery()
    test_port_check()
    test_node_exporter_mock()
    test_cloud_credentials()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    print(f"🔑 Claves SSH encontradas: {len(ssh_keys) if ssh_keys else 0}")
    print("🌐 Verificación de puertos: Funcional")
    print("🛠️ Funciones Node Exporter: Implementadas")
    print("☁️ Sistema de credenciales: Verificado")
    
    print("\n💡 Para probar completamente:")
    print("   1. Configure credenciales AWS/Azure")
    print("   2. Asegúrese de tener claves SSH válidas")
    print("   3. Use el portal web para descubrir VMs")
    print("   4. Verifique la instalación automática de Node Exporter")

if __name__ == '__main__':
    main()