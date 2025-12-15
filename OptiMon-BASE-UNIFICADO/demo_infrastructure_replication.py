#!/usr/bin/env python3
"""
Demo - Replicación de Infraestructura OptiMon
Muestra cómo generar código Infrastructure as Code basado en VMs descubiertas
"""

import sys
import os
import json
import requests

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Demo: Replicación de Infraestructura OptiMon")
    print("=" * 60)
    
    try:
        # Importar motor de replicación
        from infrastructure_replication_engine import replication_engine
        
        print("✅ Motor de replicación cargado correctamente")
        
        # Datos de ejemplo de instancias AWS
        aws_instances = [
            {
                'id': 'i-1234567890abcdef0',
                'name': 'WebServer-Production',
                'type': 't3.medium',
                'provider': 'aws',
                'ip': '10.0.1.10',
                'status': 'running',
                'zone': 'us-east-1a',
                'source': 'aws_discovery'
            },
            {
                'id': 'i-0987654321fedcba0',
                'name': 'Database-Server',
                'type': 't3.large',
                'provider': 'aws',
                'ip': '10.0.1.20',
                'status': 'running',
                'zone': 'us-east-1b',
                'source': 'aws_discovery'
            }
        ]
        
        # Datos de ejemplo de instancias Azure
        azure_instances = [
            {
                'id': '/subscriptions/sub123/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1',
                'name': 'AppServer-Prod',
                'type': 'Standard_B2s',
                'provider': 'azure',
                'ip': '10.1.1.10',
                'status': 'running',
                'source': 'azure_discovery'
            },
            {
                'id': '/subscriptions/sub123/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm2',
                'name': 'Cache-Server',
                'type': 'Standard_B1s',
                'provider': 'azure',
                'ip': '10.1.1.20',
                'status': 'running',
                'source': 'azure_discovery'
            }
        ]
        
        print("\n📊 Instancias de ejemplo:")
        print(f"AWS: {len(aws_instances)} instancias")
        print(f"Azure: {len(azure_instances)} instancias")
        
        # Generar infraestructura AWS
        print("\n🔧 Generando código Terraform para AWS...")
        aws_result = replication_engine.generate_terraform_aws(aws_instances)
        
        if aws_result.get('success'):
            print(f"✅ AWS: {aws_result['project_name']}")
            print(f"   📁 Directorio: {aws_result['project_path']}")
            print(f"   📄 Archivos: {', '.join(aws_result['files_created'])}")
            print(f"   🖥️  Instancias replicadas: {aws_result['instances_replicated']}")
        else:
            print(f"❌ Error AWS: {aws_result.get('error', 'Error desconocido')}")
        
        # Generar infraestructura Azure
        print("\n🔧 Generando código Terraform para Azure...")
        azure_result = replication_engine.generate_terraform_azure(azure_instances)
        
        if azure_result.get('success'):
            print(f"✅ Azure: {azure_result['project_name']}")
            print(f"   📁 Directorio: {azure_result['project_path']}")
            print(f"   📄 Archivos: {', '.join(azure_result['files_created'])}")
            print(f"   🖥️  VMs replicadas: {azure_result['instances_replicated']}")
        else:
            print(f"❌ Error Azure: {azure_result.get('error', 'Error desconocido')}")
        
        print("\n🎉 Demo completado exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Configura tus credenciales en AWS/Azure")
        print("2. Ejecuta el descubrimiento de instancias en OptiMon")
        print("3. Ve a http://localhost:5000/infrastructure-replication")
        print("4. Selecciona las instancias que quieres replicar")
        print("5. Genera y descarga el código Terraform")
        print("6. Personaliza según tus necesidades")
        print("7. Ejecuta terraform plan/apply")
        
    except ImportError as e:
        print(f"❌ Error importando motor de replicación: {e}")
        print("Asegúrate de que infrastructure_replication_engine.py esté presente")
    except Exception as e:
        print(f"❌ Error en demo: {e}")

if __name__ == "__main__":
    main()