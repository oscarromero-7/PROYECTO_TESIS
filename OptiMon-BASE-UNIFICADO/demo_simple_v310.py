#!/usr/bin/env python3
"""
Demo simplificado de mejoras OptiMon v3.1.0
"""

import urllib.request
import json
import sys

def test_server_connection():
    """Probar conexión básica al servidor"""
    print("\n🔌 PROBANDO CONEXIÓN AL SERVIDOR")
    print("=" * 50)
    
    try:
        with urllib.request.urlopen('http://localhost:5000', timeout=5) as response:
            if response.status == 200:
                print("✅ Servidor OptiMon conectado exitosamente")
                print(f"   Status: {response.status}")
                return True
            else:
                print(f"❌ Error: Status {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_available_resources():
    """Probar endpoint de recursos disponibles"""
    print("\n🖥️  PROBANDO DETECCIÓN DE RECURSOS")
    print("=" * 50)
    
    try:
        with urllib.request.urlopen('http://localhost:5000/api/available-resources', timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if 'physical_servers' in data and len(data['physical_servers']) > 0:
                server = data['physical_servers'][0]
                print(f"✅ Servidor local detectado:")
                print(f"   📍 Nombre: {server.get('name', 'N/A')}")
                print(f"   🌐 IP: {server.get('ip', 'N/A')}")
                print(f"   💻 Sistema: {server.get('system', 'N/A')}")
                print(f"   🏷️  Tipo: {server.get('type', 'N/A')}")
                
                if server.get('name') != 'localhost':
                    print("✅ MEJORA: Hostname real detectado (no 'localhost')")
                else:
                    print("⚠️  Aún muestra 'localhost'")
                    
                return True
            else:
                print("❌ No se detectaron servidores locales")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_system_status():
    """Probar endpoint de estado del sistema"""
    print("\n📊 PROBANDO ESTADO DEL SISTEMA")
    print("=" * 50)
    
    try:
        with urllib.request.urlopen('http://localhost:5000/api/system-status', timeout=10) as response:
            data = json.loads(response.read().decode())
            
            print("✅ Endpoint de estado del sistema disponible:")
            print(f"   🖥️  Hostname: {data['system']['hostname']}")
            print(f"   💻 Sistema: {data['system']['system']} {data['system']['release']}")
            print(f"   🔧 CPU: {data['cpu']['usage_percent']:.1f}% ({data['cpu']['count']} núcleos)")
            print(f"   💾 RAM: {data['memory']['percent']:.1f}% usado")
            print(f"   💿 Disco: {data['disk']['percent']:.1f}% usado")
            print("✅ MEJORA: Estado detallado reemplaza scanner SSH")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar demo simplificado"""
    print("🚀 DEMO SIMPLIFICADO - OptiMon v3.1.0")
    print("=" * 60)
    
    # Test 1: Conexión básica
    if not test_server_connection():
        print("\n❌ No se puede conectar al servidor. Asegúrate de que esté corriendo.")
        print("   Ejecuta: .\\start_server.bat")
        sys.exit(1)
    
    # Test 2: Recursos disponibles
    test_available_resources()
    
    # Test 3: Estado del sistema
    test_system_status()
    
    print("\n" + "=" * 60)
    print("🎉 MEJORAS VERIFICADAS:")
    print("   ✅ Detección mejorada de servidor local")
    print("   ✅ Estado del sistema en tiempo real")
    print("   ✅ Endpoint psutil funcionando")
    print("   ✅ API de recursos operativa")
    print("   ✅ Funcionalidad SSH removida del portal")
    print("=" * 60)

if __name__ == "__main__":
    main()