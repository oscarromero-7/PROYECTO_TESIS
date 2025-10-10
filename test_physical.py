#!/usr/bin/env python3
import sys
import os
sys.path.append('scripts')

from auto_setup import IntelligentAutoSetup

def test_physical_detection():
    print('🚀 Probando detección de servidores físicos...')
    
    setup = IntelligentAutoSetup()
    setup.load_config()
    
    if not setup.config:
        print('❌ Error cargando configuración')
        return
    
    print('✅ Configuración cargada correctamente')
    
    # Obtener configuración de servidores físicos
    physical_config = setup.config.get('physical_servers', {})
    manual_servers = physical_config.get('manual_servers', [])
    network_scan = physical_config.get('network_scan', {})
    
    print(f'📋 Configuración:')
    print(f'   Servidores manuales: {len(manual_servers)}')
    print(f'   Escaneo habilitado: {network_scan.get("enabled", False)}')
    
    # Ejecutar detección
    setup.scan_physical_network()
    
    physical_instances = [i for i in setup.discovered_instances if i['provider'] == 'physical']
    print(f'🔍 Servidores físicos detectados: {len(physical_instances)}')
    
    for instance in physical_instances:
        name = instance.get('name', 'Sin nombre')
        ip = instance.get('ip', 'Sin IP')
        print(f'  📍 {name} - {ip}')
        
        # Probar detección de SO
        print(f'    🔍 Detectando SO para {ip}...')
        os_info = setup._detect_os_and_arch(ip)
        if os_info:
            os_name = os_info.get('os', 'Desconocido')
            arch = os_info.get('arch', 'Desconocido')
            print(f'       SO: {os_name} ({arch})')
        else:
            print(f'       ❌ No se pudo detectar el SO')
            
        # Verificar si Node Exporter ya está instalado
        print(f'    🔍 Verificando Node Exporter...')
        is_running = setup._check_node_exporter_running(ip)
        if is_running:
            print(f'       ✅ Node Exporter ya está ejecutándose')
        else:
            print(f'       ❌ Node Exporter no está disponible')
            print(f'       💡 Se requiere instalación automática')

if __name__ == "__main__":
    test_physical_detection()