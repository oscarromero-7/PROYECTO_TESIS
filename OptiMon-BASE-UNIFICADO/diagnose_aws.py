#!/usr/bin/env python3
"""
Script para diagnosticar y resolver problemas de conectividad AWS
"""

import requests
import json
import subprocess
import socket
import time

def test_connectivity(host, port, timeout=5):
    """Probar conectividad a un host y puerto"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_aws_instances():
    """Verificar estado de instancias AWS"""
    try:
        print("🔍 Verificando instancias AWS...")
        
        # Obtener información de descubrimiento
        response = requests.post('http://localhost:5000/api/cloud/discover', 
                               json={'provider': 'aws'}, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error en descubrimiento: {response.status_code}")
            return False
        
        data = response.json()
        instances = data.get('instances', [])
        
        print(f"✅ Encontradas {len(instances)} instancias AWS")
        
        connectivity_issues = []
        
        for instance in instances:
            name = instance.get('name', 'Unknown')
            public_ip = instance.get('public_ip')
            private_ip = instance.get('private_ip')
            
            print(f"\n📡 Probando {name} ({public_ip})...")
            
            # Probar SSH (puerto 22)
            ssh_ok = test_connectivity(public_ip, 22)
            print(f"   SSH (22): {'✅' if ssh_ok else '❌'}")
            
            # Probar Node Exporter (puerto 9100)
            node_exporter_ok = test_connectivity(public_ip, 9100)
            print(f"   Node Exporter (9100): {'✅' if node_exporter_ok else '❌'}")
            
            if ssh_ok and not node_exporter_ok:
                connectivity_issues.append({
                    'name': name,
                    'ip': public_ip,
                    'issue': 'Node Exporter no accesible'
                })
            elif not ssh_ok:
                connectivity_issues.append({
                    'name': name,
                    'ip': public_ip,
                    'issue': 'SSH no accesible'
                })
        
        if connectivity_issues:
            print(f"\n⚠️  Problemas encontrados:")
            for issue in connectivity_issues:
                print(f"   • {issue['name']} ({issue['ip']}): {issue['issue']}")
            
            print(f"\n🔧 Soluciones recomendadas:")
            print("1. Verificar Security Groups en AWS Console:")
            print("   - Agregar regla: Tipo=Custom TCP, Puerto=9100, Origen=0.0.0.0/0")
            print("   - Verificar que SSH (22) esté abierto")
            print("2. Reinstalar Node Exporter manualmente en las VMs")
            print("3. Verificar que las VMs estén corriendo")
            
        else:
            print("✅ Todas las instancias están correctamente conectadas")
        
        return len(connectivity_issues) == 0
        
    except Exception as e:
        print(f"❌ Error verificando AWS: {e}")
        return False

def check_prometheus_targets():
    """Verificar targets en Prometheus"""
    try:
        print("\n🎯 Verificando targets de Prometheus...")
        
        response = requests.get('http://localhost:9090/api/v1/targets', timeout=10)
        data = response.json()
        
        aws_targets = []
        for target in data.get('data', {}).get('activeTargets', []):
            if 'aws_instances' in target.get('labels', {}).get('job', ''):
                aws_targets.append(target)
        
        print(f"📊 Targets AWS en Prometheus: {len(aws_targets)}")
        
        for target in aws_targets:
            instance = target.get('labels', {}).get('instance', 'Unknown')
            health = target.get('health', 'unknown')
            last_error = target.get('lastError', '')
            
            status = "✅" if health == "up" else "❌"
            print(f"   {instance}: {status} ({health})")
            
            if last_error:
                print(f"      Error: {last_error}")
        
        return len([t for t in aws_targets if t.get('health') == 'up']) > 0
        
    except Exception as e:
        print(f"❌ Error verificando Prometheus: {e}")
        return False

def main():
    print("=" * 60)
    print("🛠️  Diagnóstico AWS - OptiMon")
    print("=" * 60)
    
    # Verificar instancias AWS
    aws_ok = check_aws_instances()
    
    # Verificar Prometheus
    prometheus_ok = check_prometheus_targets()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print(f"   AWS Connectivity: {'✅' if aws_ok else '❌'}")
    print(f"   Prometheus Targets: {'✅' if prometheus_ok else '❌'}")
    
    if not aws_ok:
        print("\n🔧 ACCIÓN REQUERIDA:")
        print("1. Abrir puerto 9100 en Security Groups de AWS")
        print("2. Reinstalar Node Exporter en las VMs")
        print("3. Verificar que las VMs estén accesibles")
    else:
        print("\n🎉 ¡Todo funcionando correctamente!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()