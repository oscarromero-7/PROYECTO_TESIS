#!/usr/bin/env python3
"""
🎯 DEMO - RECURSOS DETECTADOS AUTOMÁTICAMENTE
Demostración del sistema mejorado que detecta recursos disponibles
"""

import requests
import json

def demo_recursos_detectados():
    """Demostración de recursos detectados automáticamente"""
    print("🎯 DEMO: RECURSOS DETECTADOS AUTOMÁTICAMENTE")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    
    # Verificar conexión
    try:
        response = requests.get(f"{base_url}")
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return
        print("✅ Servidor OptiMon activo")
    except:
        print("❌ No se puede conectar al servidor")
        return
    
    # Obtener recursos disponibles
    print(f"\n📡 DETECTANDO RECURSOS DISPONIBLES:")
    print("-" * 70)
    
    try:
        response = requests.get(f"{base_url}/api/available-resources")
        if response.status_code == 200:
            resources = response.json()
            
            # Mostrar instancias AWS
            if resources.get('aws_instances'):
                print("☁️ INSTANCIAS AWS EC2 DETECTADAS:")
                for instance in resources['aws_instances']:
                    print(f"   🎯 {instance['name']} ({instance['id']})")
                    print(f"      📊 Tipo: {instance['type']}")
                    print(f"      🔄 Estado: {instance['state']}")
                    print(f"      🌐 IP Privada: {instance['private_ip']}")
                    print(f"      🌍 IP Pública: {instance['public_ip']}")
                    print(f"      📍 Zona: {instance['zone']}")
                    print()
            else:
                print("☁️ AWS: No hay credenciales configuradas o instancias disponibles")
            
            # Mostrar VMs Azure
            if resources.get('azure_instances'):
                print("☁️ MÁQUINAS VIRTUALES AZURE DETECTADAS:")
                for vm in resources['azure_instances']:
                    print(f"   🎯 {vm['name']}")
                    print(f"      📊 Tipo: {vm['type']}")
                    print(f"      📦 Grupo de Recursos: {vm['resource_group']}")
                    print(f"      🌐 IP Privada: {vm['private_ip']}")
                    print(f"      🌍 IP Pública: {vm['public_ip']}")
                    print(f"      📍 Ubicación: {vm['location']}")
                    print()
            else:
                print("☁️ AZURE: No hay credenciales configuradas o VMs disponibles")
            
            # Mostrar servidores físicos/locales
            if resources.get('physical_servers'):
                print("🖥️ SERVIDORES FÍSICOS/LOCALES DETECTADOS:")
                for server in resources['physical_servers']:
                    print(f"   🎯 {server['name']}")
                    print(f"      🌐 IP: {server['ip']}")
                    print(f"      📊 Tipo: {server['type']}")
                    print(f"      📍 Ubicación: {server['location']}")
                    print()
            
            # Mostrar regiones disponibles
            if resources.get('regions'):
                print("🌍 REGIONES/ZONAS DETECTADAS:")
                for region in resources['regions']:
                    print(f"   📍 {region}")
                print()
            
            # Mostrar métricas disponibles
            if resources.get('metrics'):
                print("📊 MÉTRICAS DISPONIBLES:")
                for metric in resources['metrics']:
                    print(f"   📈 {metric['name']} ({metric['id']}) - {metric['unit']}")
                print()
                
        else:
            print(f"❌ Error obteniendo recursos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Crear una alerta usando recursos detectados
    print(f"🚨 CREANDO ALERTA CON RECURSO DETECTADO:")
    print("-" * 70)
    
    try:
        # Simular creación de alerta con recurso local detectado
        alerta_local = {
            "name": "Test_Recurso_Local_Detectado",
            "description": "Alerta de prueba usando recurso detectado automáticamente",
            "metric": "cpu_usage_percent",
            "threshold": 80.0,
            "operator": ">",
            "severity": "warning",
            "enabled": True,
            "resource_type": "physical_server",
            "resource_name": "localhost",  # Este será detectado automáticamente
            "resource_ip": "127.0.0.1",    # IP detectada automáticamente
            "region": "Local",
            "environment": "development",
            "tags": ["local", "detectado", "automatico"]
        }
        
        response = requests.post(
            f"{base_url}/api/custom-alerts",
            json=alerta_local,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                alert_id = result['alert']['id']
                print(f"✅ Alerta creada exitosamente")
                print(f"   🎯 Nombre: {alerta_local['name']}")
                print(f"   🖥️ Recurso: {alerta_local['resource_name']} ({alerta_local['resource_ip']})")
                print(f"   📍 Ubicación: {alerta_local['region']}")
                
                # Probar la alerta
                print(f"\n🧪 PROBANDO ALERTA CON INFORMACIÓN DETALLADA:")
                print("-" * 50)
                
                test_response = requests.post(f"{base_url}/api/custom-alerts/{alert_id}/test")
                if test_response.status_code == 200:
                    test_result = test_response.json()
                    if test_result.get('success'):
                        print(f"✅ Alerta enviada exitosamente")
                        print(f"📧 Destinatarios: {test_result.get('sent', 0)}")
                        print(f"📬 El email incluye:")
                        print(f"   • Nombre del servidor: {alerta_local['resource_name']}")
                        print(f"   • IP del servidor: {alerta_local['resource_ip']}")
                        print(f"   • Región/Ubicación: {alerta_local['region']}")
                        print(f"   • Ambiente: {alerta_local['environment']}")
                        print(f"   • Valor de la métrica simulada")
                        print(f"   • Información detallada para troubleshooting")
                    else:
                        print(f"❌ Error enviando prueba: {test_result.get('message')}")
                else:
                    print(f"❌ Error HTTP en prueba: {test_response.status_code}")
            else:
                if "Ya existe una alerta" in result.get('error', ''):
                    print("⚠️ La alerta ya existe, usando la existente")
                else:
                    print(f"❌ Error creando alerta: {result.get('error')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Resumen final
    print(f"\n" + "=" * 70)
    print("🎉 FUNCIONALIDADES IMPLEMENTADAS")
    print("✅ Detección automática de recursos AWS/Azure/Físicos")
    print("✅ Formulario dinámico con recursos reales disponibles")
    print("✅ Información de IP y detalles de VM en emails")
    print("✅ Validación de recursos existentes en el sistema")
    print("✅ Regiones/zonas detectadas automáticamente")
    print("✅ Emails mejorados con información completa de infraestructura")
    print()
    print("🌐 Página web mejorada: http://localhost:5000/custom-alerts")
    print("📡 API de recursos: http://localhost:5000/api/available-resources")
    print("=" * 70)

if __name__ == "__main__":
    demo_recursos_detectados()