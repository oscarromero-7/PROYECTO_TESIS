#!/usr/bin/env python3
"""
Módulo helper para Azure SDK que maneja la compatibilidad con Python 3.13
Ejecutado como proceso separado para evitar conflictos de typing
"""

import sys
import json
import logging
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def suppress_azure_warnings():
    """Suprimir warnings específicos de Azure/typing"""
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', message='.*ParamSpec.*')
    warnings.filterwarnings('ignore', module='typing')

def discover_azure_vms(config):
    """
    Descubrir VMs Azure de forma aislada
    Args:
        config: dict con credenciales Azure
    Returns:
        dict con resultado del descubrimiento
    """
    try:
        # Suprimir warnings antes de importar Azure
        suppress_azure_warnings()
        
        # Parche para Python 3.13 compatibility
        import sys
        if sys.version_info >= (3, 13):
            # Aplicar parche específico para typing.ParamSpec
            import typing
            if hasattr(typing, 'ParamSpec'):
                # Crear un wrapper que ignore el atributo problemático
                original_setattr = getattr(typing.ParamSpec, '__setattr__', None)
                def safe_setattr(self, name, value):
                    if name == '__default__':
                        return  # Ignorar este atributo específico
                    if original_setattr:
                        return original_setattr(self, name, value)
                    else:
                        return object.__setattr__(self, name, value)
                
                # Solo aplicar si es necesario
                try:
                    typing.ParamSpec.__setattr__ = safe_setattr
                except (AttributeError, TypeError):
                    # Si no se puede modificar, continuar sin el parche
                    pass
        
        # Importar Azure SDK
        from azure.identity import ClientSecretCredential
        from azure.mgmt.compute import ComputeManagementClient
        from azure.mgmt.network import NetworkManagementClient
        
        # Crear credenciales
        credential = ClientSecretCredential(
            tenant_id=config['tenant_id'],
            client_id=config['client_id'],
            client_secret=config['client_secret']
        )
        
        # Crear clientes
        compute_client = ComputeManagementClient(
            credential, 
            config['subscription_id']
        )
        
        network_client = NetworkManagementClient(
            credential,
            config['subscription_id']
        )
        
        # Listar VMs
        vms = list(compute_client.virtual_machines.list_all())
        
        instances = []
        for vm in vms:
            try:
                # Obtener resource group
                rg_name = vm.id.split('/')[4]
                
                # Obtener detalles de la VM
                vm_detail = compute_client.virtual_machines.get(
                    rg_name, vm.name, expand='instanceView'
                )
                
                # Obtener IPs
                vm_ip = get_vm_ip(network_client, vm, rg_name)
                
                # Obtener estado
                vm_status = 'Unknown'
                if vm_detail.instance_view and vm_detail.instance_view.statuses:
                    for status in vm_detail.instance_view.statuses:
                        if status.code and status.code.startswith('PowerState'):
                            vm_status = status.display_status
                            break
                
                instance_info = {
                    'id': vm.id,
                    'name': vm.name,
                    'type': vm_detail.hardware_profile.vm_size if vm_detail.hardware_profile else 'Unknown',
                    'resource_group': rg_name,
                    'public_ip': vm_ip.get('public'),
                    'private_ip': vm_ip.get('private'),
                    'platform': vm_detail.storage_profile.os_disk.os_type.value.lower() if vm_detail.storage_profile and vm_detail.storage_profile.os_disk.os_type else 'linux',
                    'state': vm_status
                }
                
                instances.append(instance_info)
                
            except Exception as e:
                logger.error(f"Error procesando VM {vm.name}: {e}")
                continue
        
        return {
            'success': True,
            'instances': instances,
            'count': len(instances),
            'message': f'Descubiertas {len(instances)} VMs Azure'
        }
        
    except Exception as e:
        logger.error(f"Error en descubrimiento Azure: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_vm_ip(network_client, vm, rg_name):
    """Obtener IPs de una VM Azure"""
    public_ip = None
    private_ip = None
    
    try:
        # Obtener interfaces de red
        for nic_ref in vm.network_profile.network_interfaces:
            nic_name = nic_ref.id.split('/')[-1]
            nic = network_client.network_interfaces.get(rg_name, nic_name)
            
            for ip_config in nic.ip_configurations:
                # IP privada
                if ip_config.private_ip_address:
                    private_ip = ip_config.private_ip_address
                
                # IP pública
                if ip_config.public_ip_address:
                    public_ip_name = ip_config.public_ip_address.id.split('/')[-1]
                    public_ip_obj = network_client.public_ip_addresses.get(rg_name, public_ip_name)
                    if public_ip_obj.ip_address:
                        public_ip = public_ip_obj.ip_address
                
    except Exception as e:
        logger.warning(f"Error obteniendo IP para VM {vm.name}: {e}")
    
    return {'public': public_ip, 'private': private_ip}

def main():
    """Función principal cuando se ejecuta como script independiente"""
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'Configuración Azure requerida'}))
        sys.exit(1)
    
    try:
        # Leer configuración desde argumentos
        config_json = sys.argv[1]
        config = json.loads(config_json)
        
        # Ejecutar descubrimiento
        result = discover_azure_vms(config)
        
        # Retornar resultado como JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()