#!/usr/bin/env python3
"""
Script para corregir el UID del datasource en el dashboard
"""

import requests
import json
import re

def fix_dashboard_datasource():
    """Corregir el UID del datasource en el dashboard"""
    print("[INFO] Corrigiendo UID del datasource...")
    
    # Obtener el UID correcto del datasource
    try:
        response = requests.get("http://localhost:3000/api/datasources", 
                              auth=('admin', 'admin'))
        if response.status_code == 200:
            datasources = response.json()
            prometheus_ds = None
            for ds in datasources:
                if ds['type'] == 'prometheus':
                    prometheus_ds = ds
                    break
            
            if prometheus_ds:
                correct_uid = prometheus_ds['uid']
                print(f"[OK] UID correcto encontrado: {correct_uid}")
            else:
                print("[ERROR] No se encontro datasource de Prometheus")
                return False
        else:
            print(f"[ERROR] Error obteniendo datasources: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error conectando a Grafana: {e}")
        return False
    
    # Leer el dashboard actual
    dashboard_file = "2-INICIAR-MONITOREO/config/grafana/dashboards/windows_local_fixed.json"
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Reemplazar todos los UIDs incorrectos
        original_count = dashboard_content.count('"uid": "prometheus"')
        dashboard_content = dashboard_content.replace('"uid": "prometheus"', f'"uid": "{correct_uid}"')
        
        # Guardar el dashboard corregido
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        print(f"[OK] Reemplazadas {original_count} referencias de UID")
        
        # Importar el dashboard corregido
        dashboard_json = json.loads(dashboard_content)
        
        payload = {
            "dashboard": dashboard_json,
            "overwrite": True,
            "message": "Fixed datasource UID"
        }
        
        response = requests.post(
            "http://localhost:3000/api/dashboards/db",
            json=payload,
            headers={'Content-Type': 'application/json'},
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            result = response.json()
            dashboard_url = f"http://localhost:3000/d/{result.get('uid', 'unknown')}"
            print("[OK] Dashboard corregido e importado!")
            print(f"[URL] {dashboard_url}")
            return True, dashboard_url
        else:
            print(f"[ERROR] Error importando dashboard: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Error procesando dashboard: {e}")
        return False, None

def test_dashboard_query():
    """Probar que las queries funcionen con el UID correcto"""
    print("\n[INFO] Probando consulta directa a Grafana...")
    
    try:
        # Probar query a través de la API de Grafana
        params = {
            'query': 'up{instance="local-computer"}',
            'time': 'now'
        }
        
        response = requests.get(
            "http://localhost:3000/api/datasources/proxy/1/api/v1/query",
            params=params,
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('result'):
                value = data['data']['result'][0]['value'][1]
                print(f"[OK] Query via Grafana funciona: {value}")
                return True
            else:
                print("[WARN] Query via Grafana sin resultados")
                return False
        else:
            print(f"[ERROR] Query via Grafana fallo: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error probando query: {e}")
        return False

if __name__ == "__main__":
    print("CORRIGIENDO DATASOURCE UID EN DASHBOARD")
    print("=" * 50)
    
    success, url = fix_dashboard_datasource()
    
    if success:
        query_works = test_dashboard_query()
        
        if query_works:
            print("\n[SUCCESS] Dashboard completamente corregido!")
            print(f"[ACCESS] Abre: {url}")
            print("[INFO] El dashboard ahora deberia mostrar datos")
        else:
            print("\n[WARN] Dashboard corregido pero queries pueden tener problemas")
            print("[INFO] Verifica manualmente en Grafana")
    else:
        print("\n[ERROR] Error corrigiendo dashboard")
        
    print("\n[DEBUG] Para verificar manualmente:")
    print("1. Abre http://localhost:3000")
    print("2. Ve a Configuration > Data Sources")
    print("3. Verifica que Prometheus este conectado")
    print("4. Prueba queries en Explore")