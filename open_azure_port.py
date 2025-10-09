#!/usr/bin/env python3
"""
Abrir puerto 9100 en NSG de Azure automáticamente
"""

import yaml
from pathlib import Path
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient

def open_node_exporter_port():
    """Abre el puerto 9100 en el NSG de Azure automáticamente"""
    
    print("🔓 Abriendo puerto 9100 en Azure NSG...")
    
    # Cargar configuración
    config_file = Path("config/credentials.simple.yml")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    azure_config = config['azure']
    
    try:
        # Autenticación
        credential = ClientSecretCredential(
            tenant_id=azure_config['tenant_id'],
            client_id=azure_config['client_id'],
            client_secret=azure_config['client_secret']
        )
        
        network_client = NetworkManagementClient(
            credential,
            azure_config['subscription_id']
        )
        
        # Buscar NSG del resource group
        resource_group = "RECURSOS_PRUEBAS"  # Del script anterior
        
        print(f"📋 Buscando NSGs en {resource_group}...")
        
        nsgs = list(network_client.network_security_groups.list(resource_group))
        
        for nsg in nsgs:
            print(f"🔍 Procesando NSG: {nsg.name}")
            
            # Verificar si ya existe regla para puerto 9100
            has_rule = False
            for rule in nsg.security_rules:
                if (rule.destination_port_range == "9100" or 
                    (rule.destination_port_ranges and "9100" in rule.destination_port_ranges)):
                    print(f"  ✅ Puerto 9100 ya está abierto en regla: {rule.name}")
                    has_rule = True
                    break
            
            if not has_rule:
                print(f"  🔓 Agregando regla para puerto 9100...")
                
                # Crear regla de seguridad
                rule_parameters = {
                    'name': 'AllowNodeExporter',
                    'protocol': 'Tcp',
                    'source_address_prefix': '*',
                    'source_port_range': '*',
                    'destination_address_prefix': '*',
                    'destination_port_range': '9100',
                    'access': 'Allow',
                    'direction': 'Inbound',
                    'priority': 1010,
                    'description': 'Allow Node Exporter metrics'
                }
                
                # Aplicar regla
                operation = network_client.security_rules.begin_create_or_update(
                    resource_group,
                    nsg.name,
                    'AllowNodeExporter',
                    rule_parameters
                )
                
                # Esperar a que se complete
                result = operation.result()
                print(f"  ✅ Regla creada: {result.name}")
                
        print(f"\n✅ Puerto 9100 configurado correctamente en Azure")
        print(f"   Espera 1-2 minutos para que los cambios se apliquen")
        
    except Exception as e:
        print(f"❌ Error configurando NSG: {e}")
        print(f"\n📋 Configuración manual necesaria:")
        print(f"   1. Ve al portal de Azure")
        print(f"   2. Busca el Network Security Group de tu VM")
        print(f"   3. Agrega regla de entrada:")
        print(f"      - Puerto: 9100")
        print(f"      - Protocolo: TCP") 
        print(f"      - Acción: Permitir")

if __name__ == "__main__":
    open_node_exporter_port()