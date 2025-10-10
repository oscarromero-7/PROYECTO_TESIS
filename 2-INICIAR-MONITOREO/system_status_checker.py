#!/usr/bin/env python3
"""
Verificador completo del estado del sistema OptiMon
"""

import requests
import subprocess
import socket

def check_port(host, port):
    """Verificar si un puerto está abierto"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_system_status():
    """Verificar el estado completo del sistema"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA OPTIMON")
    print("=" * 50)
    
    # 1. Verificar Dashboard OptiMon
    print("\n1. 📊 Dashboard OptiMon (Puerto 5000)")
    if check_port("localhost", 5000):
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Dashboard ejecutándose correctamente")
            else:
                print(f"   ⚠️  Dashboard responde pero con error: {response.status_code}")
        except:
            print("   ❌ Dashboard no responde a API")
    else:
        print("   ❌ Dashboard no está ejecutándose")
    
    # 2. Verificar Windows Exporter
    print("\n2. 🖥️  Windows Exporter (Puerto 9182)")
    if check_port("localhost", 9182):
        try:
            response = requests.get("http://localhost:5000/api/local/windows-exporter/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"   ✅ Windows Exporter funcionando")
                print(f"   📊 Métricas disponibles: {status.get('metrics_count', 'N/A')}")
                print(f"   🔧 Versión: {status.get('version', 'N/A')}")
            else:
                print("   ⚠️  Windows Exporter detectado pero API no responde")
        except:
            print("   ⚠️  Windows Exporter en puerto pero no verificable vía API")
    else:
        print("   ❌ Windows Exporter no está ejecutándose")
    
    # 3. Verificar Prometheus
    print("\n3. 📈 Prometheus (Puerto 9090)")
    if check_port("localhost", 9090):
        try:
            response = requests.get("http://localhost:9090/-/healthy", timeout=5)
            if response.status_code == 200:
                print("   ✅ Prometheus ejecutándose correctamente")
            else:
                print("   ⚠️  Prometheus responde pero con problemas")
        except:
            print("   ⚠️  Prometheus en puerto pero no responde a health check")
    else:
        print("   ❌ Prometheus no está ejecutándose")
    
    # 4. Verificar Grafana
    print("\n4. 📊 Grafana (Puerto 3000)")
    if check_port("localhost", 3000):
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Grafana ejecutándose correctamente")
                
                # Verificar dashboards ocultos
                try:
                    dash_response = requests.get("http://localhost:3000/api/search", 
                                               auth=('admin', 'admin'), timeout=5)
                    if dash_response.status_code == 200:
                        dashboards = dash_response.json()
                        hidden_dashboards = [d for d in dashboards if d.get('title', '').startswith('[HIDDEN]')]
                        visible_optimon = [d for d in dashboards if 'optimon' in d.get('title', '').lower() and not d.get('title', '').startswith('[HIDDEN]')]
                        
                        print(f"   🔒 Dashboards ocultos: {len(hidden_dashboards)}")
                        print(f"   👁️  Dashboards OptiMon visibles: {len(visible_optimon)}")
                except:
                    print("   ⚠️  No se pudo verificar estado de dashboards")
            else:
                print("   ⚠️  Grafana responde pero con problemas")
        except:
            print("   ⚠️  Grafana en puerto pero no responde completamente")
    else:
        print("   ❌ Grafana no está ejecutándose")
    
    # 5. Verificar AlertManager
    print("\n5. 🚨 AlertManager (Puerto 9093)")
    if check_port("localhost", 9093):
        try:
            response = requests.get("http://localhost:9093/-/healthy", timeout=5)
            if response.status_code == 200:
                print("   ✅ AlertManager ejecutándose correctamente")
            else:
                print("   ⚠️  AlertManager responde pero con problemas")
        except:
            print("   ⚠️  AlertManager en puerto pero no responde a health check")
    else:
        print("   ❌ AlertManager no está ejecutándose")
    
    # 6. Verificar SMTP Service
    print("\n6. 📧 SMTP Service (Puerto 5555)")
    if check_port("localhost", 5555):
        print("   ✅ SMTP Service ejecutándose")
    else:
        print("   ❌ SMTP Service no está ejecutándose")
    
    # 7. Verificar credenciales de nube
    print("\n7. ☁️  Credenciales de Nube")
    try:
        response = requests.get("http://localhost:5000/api/cloud/credentials", timeout=5)
        if response.status_code == 200:
            creds = response.json()
            print(f"   AWS: {'✅ Configurado' if creds.get('aws_configured') else '❌ No configurado'}")
            print(f"   Azure: {'✅ Configurado' if creds.get('azure_configured') else '❌ No configurado'}")
            print(f"   GCP: {'🚫 Deshabilitado' if not creds.get('gcp_configured') else '⚠️ Habilitado'}")
        else:
            print("   ⚠️  No se pudo verificar credenciales")
    except:
        print("   ❌ Error verificando credenciales")
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICACIÓN COMPLETADA")

if __name__ == '__main__':
    check_system_status()