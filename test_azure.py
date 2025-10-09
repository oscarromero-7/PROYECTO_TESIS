#!/usr/bin/env python3
"""
OptiMon - Test Azure Detection
Detecta VMs de Azure para probar las credenciales
"""

import os
import sys
import yaml
import json
from pathlib import Path
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient

def test_azure_connection():
    """Prueba la conexión con Azure y lista las VMs"""
    
    # Cargar configuración
    config_file = Path("config/credentials.simple.yml")
    if not config_file.exists():
        print("❌ Archivo de configuración no encontrado")
        return
        
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'azure' not in config or not config['azure'].get('subscription_id'):
        print("❌ Credenciales de Azure no configuradas")
        return
    
    azure_config = config['azure']
    
    try:
        print("🔐 Autenticando con Azure...")
        
        # Crear credenciales
        credential = ClientSecretCredential(
            tenant_id=azure_config['tenant_id'],
            client_id=azure_config['client_id'],
            client_secret=azure_config['client_secret']
        )
        
        # Cliente de compute
        compute_client = ComputeManagementClient(
            credential, 
            azure_config['subscription_id']
        )
        
        # Cliente de recursos
        resource_client = ResourceManagementClient(
            credential,
            azure_config['subscription_id']
        )
        
        print("✅ Autenticación exitosa")
        
        # Listar grupos de recursos
        print("\n📁 Grupos de recursos encontrados:")
        resource_groups = list(resource_client.resource_groups.list())
        for rg in resource_groups:
            print(f"  - {rg.name} ({rg.location})")
        
        # Listar VMs
        print("\n🖥️ VMs encontradas:")
        vm_count = 0
        
        for vm in compute_client.virtual_machines.list_all():
            vm_count += 1
            
            # Obtener detalles
            rg_name = vm.id.split('/')[4]  # Extraer resource group del ID
            vm_detail = compute_client.virtual_machines.get(
                rg_name, 
                vm.name, 
                expand='instanceView'
            )
            
            # Estado
            power_state = "unknown"
            if vm_detail.instance_view and vm_detail.instance_view.statuses:
                for status in vm_detail.instance_view.statuses:
                    if status.code.startswith('PowerState/'):
                        power_state = status.code.split('/')[-1]
                        break
            
            # Información del SO
            os_type = "Unknown"
            if vm_detail.storage_profile and vm_detail.storage_profile.os_disk:
                os_type = vm_detail.storage_profile.os_disk.os_type
            
            print(f"  VM: {vm.name}")
            print(f"    Grupo: {rg_name}")
            print(f"    Ubicación: {vm.location}")
            print(f"    Tamaño: {vm.hardware_profile.vm_size}")
            print(f"    SO: {os_type}")
            print(f"    Estado: {power_state}")
            
            # Obtener IPs
            try:
                # Obtener interfaces de red
                network_client = None  # Podríamos importar NetworkManagementClient
                print(f"    ID: {vm.id}")
                print(f"    Tags: {vm.tags if vm.tags else 'Ninguno'}")
            except Exception as e:
                print(f"    Error obteniendo red: {e}")
            
            print()
        
        print(f"📊 Total de VMs encontradas: {vm_count}")
        
        if vm_count == 0:
            print("\n⚠️ No se encontraron VMs en tu suscripción")
            print("   Verifica que:")
            print("   1. Las credenciales sean correctas")
            print("   2. Tengas VMs creadas en Azure")
            print("   3. El service principal tenga permisos de lectura")
        else:
            print("\n✅ Detección de Azure funcionando correctamente!")
            print("   El sistema puede instalar Node Exporter en estas VMs")
            
    except Exception as e:
        print(f"❌ Error conectando con Azure: {e}")
        print("\nVerifica:")
        print("1. Subscription ID correcto")
        print("2. Tenant ID correcto") 
        print("3. Client ID correcto")
        print("4. Client Secret correcto")
        print("5. Service Principal tiene permisos")

if __name__ == "__main__":
    print("🧪 OptiMon - Test de Detección Azure")
    print("=" * 50)
    test_azure_connection()