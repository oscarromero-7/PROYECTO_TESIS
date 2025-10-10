#!/usr/bin/env python3
"""
🔍 DIAGNOSTICO GRAFANA - Verificar Datasources y Credenciales
Verifica qué datasources están configurados en Grafana y de dónde vienen las credenciales
"""

import requests
import json
from datetime import datetime

def check_grafana_datasources():
    """Verificar datasources configurados en Grafana"""
    print("🔍 DIAGNÓSTICO DE GRAFANA - DATASOURCES Y CREDENCIALES")
    print("=" * 70)
    
    grafana_url = "http://localhost:3000"
    api_url = f"{grafana_url}/api/datasources"
    
    # Credenciales por defecto de Grafana
    auth = ('admin', 'admin')
    
    try:
        print(f"📡 Consultando: {api_url}")
        response = requests.get(api_url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            datasources = response.json()
            print(f"✅ Respuesta exitosa - {len(datasources)} datasources encontrados")
            print()
            
            for i, ds in enumerate(datasources, 1):
                print(f"📊 DATASOURCE #{i}:")
                print(f"   Nombre: {ds.get('name', 'N/A')}")
                print(f"   Tipo: {ds.get('type', 'N/A')}")
                print(f"   URL: {ds.get('url', 'N/A')}")
                print(f"   UID: {ds.get('uid', 'N/A')}")
                print(f"   Por defecto: {ds.get('isDefault', False)}")
                
                # Verificar si tiene credenciales de nube
                json_data = ds.get('jsonData', {})
                secure_json_data = ds.get('secureJsonData', {})
                
                if json_data:
                    print(f"   Datos JSON: {json.dumps(json_data, indent=2)}")
                
                if secure_json_data:
                    print(f"   Datos seguros configurados: {list(secure_json_data.keys())}")
                
                print("-" * 50)
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    print()
    print("📋 RESUMEN:")
    print("- Los datasources mostrados están configurados en Grafana")
    print("- Si aparecen credenciales de AWS/Azure, vienen de:")
    print("  1. Configuración previa en el sistema")
    print("  2. Variables de entorno")
    print("  3. Dashboards importados con configuración")
    print("  4. Configuración manual anterior")

def check_grafana_dashboards():
    """Verificar dashboards configurados"""
    print("\n🎯 VERIFICANDO DASHBOARDS CONFIGURADOS")
    print("=" * 50)
    
    grafana_url = "http://localhost:3000"
    api_url = f"{grafana_url}/api/search"
    auth = ('admin', 'admin')
    
    try:
        response = requests.get(api_url, auth=auth, timeout=10)
        if response.status_code == 200:
            dashboards = response.json()
            print(f"✅ {len(dashboards)} dashboards encontrados:")
            
            for dash in dashboards:
                print(f"   📊 {dash.get('title', 'Sin título')} (UID: {dash.get('uid', 'N/A')})")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print(f"🕒 Diagnóstico ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_grafana_datasources()
    check_grafana_dashboards()
    
    print("\n" + "=" * 70)
    print("🎯 Para solucionar credenciales no deseadas:")
    print("1. Accede a Grafana: http://localhost:3000")
    print("2. Ve a Configuration > Data Sources")
    print("3. Elimina o edita los datasources no deseados")
    print("4. O usa el dashboard OptiMon para gestionar credenciales")