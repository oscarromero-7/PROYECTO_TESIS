#!/usr/bin/env python3
"""
Azure API Helper usando REST API directo para evitar problemas con SDK
"""

import sys
import json
import logging
import requests
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_azure_access_token(tenant_id, client_id, client_secret):
    """Obtener token de acceso usando REST API"""
    try:
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://management.azure.com/.default'
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                'success': True,
                'access_token': token_data['access_token']
            }
        else:
            return {
                'success': False,
                'error': f'Error obteniendo token: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }

def list_azure_vms_rest(subscription_id, access_token):
    """Listar VMs usando Azure REST API"""
    try:
        url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Compute/virtualMachines"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'api-version': '2023-03-01'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=60)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f'Error listando VMs: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }

def get_vm_instance_view(subscription_id, resource_group, vm_name, access_token):
    """Obtener vista de instancia de VM"""
    try:
        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}/instanceView"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'api-version': '2023-03-01'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Error obteniendo instance view para {vm_name}: {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"Error obteniendo instance view para {vm_name}: {e}")
        return None

def get_vm_network_interfaces(subscription_id, resource_group, vm_data, access_token):
    """Obtener interfaces de red de una VM"""
    try:
        public_ip = None
        private_ip = None
        
        # Obtener interfaces de red de la VM
        if 'networkProfile' in vm_data['properties'] and 'networkInterfaces' in vm_data['properties']['networkProfile']:
            for nic_ref in vm_data['properties']['networkProfile']['networkInterfaces']:
                nic_id = nic_ref['id']
                nic_name = nic_id.split('/')[-1]
                
                # Obtener detalles de la interfaz de red
                nic_url = f"https://management.azure.com{nic_id}"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                params = {'api-version': '2023-05-01'}
                
                nic_response = requests.get(nic_url, headers=headers, params=params, timeout=30)
                
                if nic_response.status_code == 200:
                    nic_data = nic_response.json()
                    
                    # Obtener IP privada
                    if 'ipConfigurations' in nic_data['properties']:
                        for ip_config in nic_data['properties']['ipConfigurations']:
                            if 'privateIPAddress' in ip_config['properties']:
                                private_ip = ip_config['properties']['privateIPAddress']
                            
                            # Verificar IP pública
                            if 'publicIPAddress' in ip_config['properties']:
                                public_ip_id = ip_config['properties']['publicIPAddress']['id']
                                public_ip_url = f"https://management.azure.com{public_ip_id}"
                                
                                pip_response = requests.get(public_ip_url, headers=headers, params=params, timeout=30)
                                if pip_response.status_code == 200:
                                    pip_data = pip_response.json()
                                    if 'ipAddress' in pip_data['properties']:
                                        public_ip = pip_data['properties']['ipAddress']
        
        return {'public': public_ip, 'private': private_ip}
        
    except Exception as e:
        logger.warning(f"Error obteniendo IPs para VM: {e}")
        return {'public': None, 'private': None}

def discover_azure_vms_rest(config):
    """
    Descubrir VMs Azure usando REST API directo
    """
    try:
        # Obtener token de acceso
        token_result = get_azure_access_token(
            config['tenant_id'],
            config['client_id'],
            config['client_secret']
        )
        
        if not token_result['success']:
            return token_result
        
        access_token = token_result['access_token']
        
        # Listar VMs
        vms_result = list_azure_vms_rest(config['subscription_id'], access_token)
        
        if not vms_result['success']:
            return vms_result
        
        vms_data = vms_result['data']
        instances = []
        
        for vm in vms_data.get('value', []):
            try:
                vm_name = vm['name']
                resource_group = vm['id'].split('/')[4]
                
                # Obtener estado de la VM
                instance_view = get_vm_instance_view(
                    config['subscription_id'],
                    resource_group,
                    vm_name,
                    access_token
                )
                
                vm_status = 'Unknown'
                if instance_view and 'statuses' in instance_view:
                    for status in instance_view['statuses']:
                        if status['code'].startswith('PowerState'):
                            vm_status = status['displayStatus']
                            break
                
                # Obtener IPs
                vm_ips = get_vm_network_interfaces(
                    config['subscription_id'],
                    resource_group,
                    vm,
                    access_token
                )
                
                # Determinar plataforma
                platform = 'linux'
                if 'storageProfile' in vm['properties'] and 'osDisk' in vm['properties']['storageProfile']:
                    if 'osType' in vm['properties']['storageProfile']['osDisk']:
                        platform = vm['properties']['storageProfile']['osDisk']['osType'].lower()
                
                instance_info = {
                    'id': vm['id'],
                    'name': vm_name,
                    'type': vm['properties']['hardwareProfile']['vmSize'] if 'hardwareProfile' in vm['properties'] else 'Unknown',
                    'resource_group': resource_group,
                    'public_ip': vm_ips['public'],
                    'private_ip': vm_ips['private'],
                    'platform': platform,
                    'state': vm_status,
                    'location': vm['location']
                }
                
                instances.append(instance_info)
                logger.info(f"VM procesada: {vm_name} - Estado: {vm_status}")
                
            except Exception as e:
                logger.error(f"Error procesando VM {vm.get('name', 'Unknown')}: {e}")
                continue
        
        return {
            'success': True,
            'instances': instances,
            'count': len(instances),
            'message': f'Descubiertas {len(instances)} VMs Azure usando REST API'
        }
        
    except Exception as e:
        logger.error(f"Error en descubrimiento Azure REST: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'Configuración Azure requerida'}))
        sys.exit(1)
    
    try:
        # Leer configuración desde argumentos
        config_json = sys.argv[1]
        config = json.loads(config_json)
        
        # Ejecutar descubrimiento usando REST API
        result = discover_azure_vms_rest(config)
        
        # Retornar resultado como JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()