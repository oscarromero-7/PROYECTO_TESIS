#!/usr/bin/env python3
"""
Script para configurar correctamente el datasource de Grafana
"""

import requests
import json
import time

def login_grafana():
    """Hacer login en Grafana"""
    session = requests.Session()
    
    # Hacer login
    login_data = {
        "user": "admin",
        "password": "admin"
    }
    
    response = session.post("http://localhost:3000/login", data=login_data)
    
    if response.status_code == 200:
        print("✅ Login exitoso en Grafana")
        return session
    else:
        print(f"❌ Error en login: {response.status_code}")
        return None

def configure_datasource(session):
    """Configurar o actualizar el datasource de Prometheus"""
    
    # Configuración del datasource
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://prometheus:9090",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST",
            "queryTimeout": "60s",
            "timeInterval": "15s",
            "manageAlerts": True,
            "cacheLevel": "Medium"
        },
        "secureJsonData": {}
    }
    
    # Primero, intentar obtener datasources existentes
    response = session.get("http://localhost:3000/api/datasources")
    
    if response.status_code == 200:
        datasources = response.json()
        prometheus_ds = None
        
        for ds in datasources:
            if ds['type'] == 'prometheus':
                prometheus_ds = ds
                break
        
        if prometheus_ds:
            # Actualizar datasource existente
            print(f"🔄 Actualizando datasource existente (ID: {prometheus_ds['id']})")
            
            datasource_config['id'] = prometheus_ds['id']
            datasource_config['uid'] = prometheus_ds.get('uid', 'prometheus')
            
            response = session.put(f"http://localhost:3000/api/datasources/{prometheus_ds['id']}", 
                                 json=datasource_config)
            
            if response.status_code == 200:
                print("✅ Datasource actualizado correctamente")
                return True
            else:
                print(f"❌ Error actualizando datasource: {response.status_code}")
                print(response.text)
                return False
        else:
            # Crear nuevo datasource
            print("🆕 Creando nuevo datasource")
            
            response = session.post("http://localhost:3000/api/datasources", 
                                  json=datasource_config)
            
            if response.status_code == 200:
                print("✅ Datasource creado correctamente")
                return True
            else:
                print(f"❌ Error creando datasource: {response.status_code}")
                print(response.text)
                return False
    else:
        print(f"❌ Error obteniendo datasources: {response.status_code}")
        return False

def test_datasource(session):
    """Probar la conexión del datasource"""
    
    # Obtener el ID del datasource Prometheus
    response = session.get("http://localhost:3000/api/datasources")
    
    if response.status_code == 200:
        datasources = response.json()
        
        for ds in datasources:
            if ds['type'] == 'prometheus':
                # Probar la conexión
                test_response = session.get(f"http://localhost:3000/api/datasources/{ds['id']}/health")
                
                if test_response.status_code == 200:
                    health_data = test_response.json()
                    print(f"✅ Test de datasource: {health_data.get('status', 'OK')}")
                    if 'message' in health_data:
                        print(f"📝 Mensaje: {health_data['message']}")
                    return True
                else:
                    print(f"❌ Error en test de datasource: {test_response.status_code}")
                    return False
        
        print("❌ No se encontró datasource Prometheus")
        return False
    else:
        print(f"❌ Error obteniendo datasources para test: {response.status_code}")
        return False

def force_dashboard_reload(session):
    """Forzar recarga de dashboards"""
    try:
        # Obtener lista de dashboards
        response = session.get("http://localhost:3000/api/search?type=dash-db")
        
        if response.status_code == 200:
            dashboards = response.json()
            
            corrected_dashboard = None
            for dashboard in dashboards:
                if "CORREGIDO" in dashboard.get('title', ''):
                    corrected_dashboard = dashboard
                    break
            
            if corrected_dashboard:
                print(f"✅ Dashboard encontrado: {corrected_dashboard['title']}")
                print(f"📍 URL: http://localhost:3000{corrected_dashboard['url']}")
                return corrected_dashboard['url']
            else:
                print("⚠️  Dashboard 'CORREGIDO' no encontrado")
                return None
        else:
            print(f"❌ Error obteniendo dashboards: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error buscando dashboards: {str(e)}")
        return None

def main():
    print("🔧 CONFIGURACIÓN DATASOURCE GRAFANA")
    print("=" * 50)
    
    # Esperar a que Grafana esté listo
    print("⏳ Esperando que Grafana esté listo...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana está listo")
                break
        except:
            pass
        
        if i < 9:
            time.sleep(2)
            print(f"   Intento {i+1}/10...")
    else:
        print("❌ Grafana no responde")
        return
    
    # Login
    session = login_grafana()
    if not session:
        return
    
    print()
    
    # Configurar datasource
    print("🔗 CONFIGURANDO DATASOURCE")
    print("-" * 30)
    success = configure_datasource(session)
    
    if success:
        print()
        print("🧪 PROBANDO DATASOURCE")
        print("-" * 25)
        test_datasource(session)
        
        print()
        print("📊 BUSCANDO DASHBOARD CORREGIDO")
        print("-" * 35)
        dashboard_url = force_dashboard_reload(session)
        
        print()
        print("=" * 50)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print()
        print("🎯 ACCESOS:")
        print(f"   Grafana: http://localhost:3000")
        print(f"   Login: admin / admin")
        
        if dashboard_url:
            print(f"   Dashboard: http://localhost:3000{dashboard_url}")
        
        print()
        print("🔍 VERIFICACIONES:")
        print("   1. El datasource 'Prometheus' debe estar configurado")
        print("   2. URL: http://prometheus:9090")
        print("   3. Usar dashboard 'OptiMon - DASHBOARD CORREGIDO v2'")
        print("   4. Los valores deben estar entre 0-100%")
        
    else:
        print("❌ Error configurando datasource")

if __name__ == "__main__":
    main()