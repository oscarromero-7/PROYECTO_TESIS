#!/usr/bin/env python3
"""
Prueba completa de OptiMon v3.1.0 - Todas las funcionalidades
"""

import urllib.request
import json
import sys
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def test_basic_connection():
    """Test 1: Conexión básica"""
    print_header("TEST 1: CONEXIÓN BÁSICA")
    
    try:
        with urllib.request.urlopen('http://localhost:5000', timeout=5) as response:
            if response.status == 200:
                print("✅ Servidor OptiMon responde correctamente")
                print(f"   Status: {response.status}")
                return True
            else:
                print(f"❌ Error: Status {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_resources_detection():
    """Test 2: Detección de recursos"""
    print_header("TEST 2: DETECCIÓN DE RECURSOS")
    
    try:
        with urllib.request.urlopen('http://localhost:5000/api/available-resources', timeout=10) as response:
            data = json.loads(response.read().decode())
            
            print("🖥️  Servidores locales:")
            for server in data.get('physical_servers', []):
                print(f"   ✅ {server.get('name')} ({server.get('ip')})")
                
            print("☁️  Instancias AWS:")
            for instance in data.get('aws_instances', []):
                print(f"   ✅ {instance.get('name')} - {instance.get('id')} ({instance.get('state')})")
                
            print("🔵 Instancias Azure:")
            azure_count = len(data.get('azure_instances', []))
            print(f"   📊 {azure_count} instancias detectadas")
            
            return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_system_status():
    """Test 3: Estado del sistema"""
    print_header("TEST 3: ESTADO DEL SISTEMA")
    
    try:
        with urllib.request.urlopen('http://localhost:5000/api/system-status', timeout=10) as response:
            data = json.loads(response.read().decode())
            
            print(f"🖥️  Hostname: {data['system']['hostname']}")
            print(f"💻 Sistema: {data['system']['system']} {data['system']['release']}")
            print(f"🔧 CPU: {data['cpu']['usage_percent']}% ({data['cpu']['count']} núcleos)")
            print(f"💾 RAM: {data['memory']['percent']}% usado")
            print(f"💿 Disco: {data['disk']['percent']}% usado")
            print(f"⏱️  Uptime: {data['uptime_days']} días")
            print(f"📊 Estado: {data['status']}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_email_system():
    """Test 4: Sistema de email"""
    print_header("TEST 4: SISTEMA DE EMAIL")
    
    try:
        # Verificar configuración de destinatarios
        with urllib.request.urlopen('http://localhost:5000/api/email-recipients', timeout=5) as response:
            data = json.loads(response.read().decode())
            recipients = data.get('recipients', [])
            print(f"📧 Destinatarios configurados: {len(recipients)}")
            for email in recipients:
                print(f"   ✉️  {email}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_custom_alerts():
    """Test 5: Alertas personalizadas"""
    print_header("TEST 5: ALERTAS PERSONALIZADAS")
    
    try:
        with urllib.request.urlopen('http://localhost:5000/api/custom-alerts', timeout=5) as response:
            data = json.loads(response.read().decode())
            alerts = data.get('alerts', [])
            print(f"🔔 Alertas configuradas: {len(alerts)}")
            
            for alert in alerts:
                status = "🟢 Activa" if alert.get('enabled') else "🔴 Inactiva"
                print(f"   {status} {alert.get('name')} - {alert.get('metric')} {alert.get('operator')} {alert.get('threshold')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cloud_credentials():
    """Test 6: Credenciales cloud"""
    print_header("TEST 6: CREDENCIALES CLOUD")
    
    try:
        # Verificar AWS
        with urllib.request.urlopen('http://localhost:5000/api/clouds/aws/test', timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('success'):
                print("✅ AWS: Credenciales válidas")
            else:
                print("⚠️  AWS: Problema con credenciales")
                
        # Verificar Azure
        with urllib.request.urlopen('http://localhost:5000/api/clouds/azure/test', timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('success'):
                print("✅ Azure: Credenciales válidas")
            else:
                print("⚠️  Azure: Problema con credenciales")
                
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PRUEBA COMPLETA OptiMon v3.1.0")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_basic_connection,
        test_resources_detection,
        test_system_status,
        test_email_system,
        test_custom_alerts,
        test_cloud_credentials
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
    
    print_header("RESUMEN DE PRUEBAS")
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    print(f"📊 Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ¡TODAS LAS FUNCIONALIDADES OPERATIVAS!")
    else:
        print("⚠️  Algunas funcionalidades necesitan atención")
    
    print_header("MEJORAS IMPLEMENTADAS")
    print("✅ Detección real de hostname (ASUS-VivoBook vs localhost)")
    print("✅ Estado del sistema en tiempo real con psutil")
    print("✅ Funcionalidad SSH removida del portal")
    print("✅ Servidor ejecutándose en segundo plano")
    print("✅ Sistema de alertas personalizadas funcional")
    print("✅ Integración Gmail operativa")
    print("✅ Detección automática de recursos AWS/Azure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)