#!/usr/bin/env python3
"""
Script para importar el dashboard corregido de Windows Local
"""

import requests
import json
import time

def import_fixed_dashboard():
    """Importar dashboard corregido"""
    grafana_url = "http://localhost:3000"
    dashboard_file = "2-INICIAR-MONITOREO/config/grafana/dashboards/windows_local_fixed.json"
    
    print("[INFO] Importando dashboard corregido de Windows Local...")
    
    # Esperar a que Grafana esté disponible
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("[OK] Grafana esta disponible")
                break
        except:
            pass
        
        if i < max_retries - 1:
            print(f"[WAIT] Esperando Grafana... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("[ERROR] Grafana no esta disponible")
        return False
    
    try:
        # Leer el dashboard corregido
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_json = json.load(f)
        
        # Preparar payload para importación
        payload = {
            "dashboard": dashboard_json,
            "overwrite": True,
            "message": "Imported Fixed Windows Local Dashboard"
        }
        
        # Importar dashboard
        response = requests.post(
            f"{grafana_url}/api/dashboards/db",
            json=payload,
            headers={'Content-Type': 'application/json'},
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            result = response.json()
            dashboard_uid = result.get('uid', 'unknown')
            dashboard_url = f"{grafana_url}/d/{dashboard_uid}"
            
            print("[OK] Dashboard corregido importado exitosamente!")
            print(f"[URL] {dashboard_url}")
            print(f"[UID] {dashboard_uid}")
            return True, dashboard_url
        else:
            print(f"[ERROR] Error importando dashboard: {response.status_code}")
            print(f"[RESPONSE] {response.text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False, None

def test_queries():
    """Probar las queries individualmente"""
    print("\n[INFO] Probando queries individuales...")
    
    prometheus_url = "http://localhost:9090"
    
    queries = {
        "Status": "up{instance=\"local-computer\"}",
        "Load": "node_load1{instance=\"local-computer\"}",
        "Uptime": "time() - node_boot_time_seconds{instance=\"local-computer\"}",
        "Memory Total": "node_memory_MemTotal_bytes{instance=\"local-computer\"}",
        "Memory Available": "node_memory_MemAvailable_bytes{instance=\"local-computer\"}"
    }
    
    working_queries = 0
    for name, query in queries.items():
        try:
            response = requests.get(f"{prometheus_url}/api/v1/query", 
                                  params={'query': query}, timeout=5)
            if response.status_code == 200:
                data = response.json()['data']['result']
                if data:
                    value = data[0]['value'][1]
                    print(f"[OK] {name}: {value}")
                    working_queries += 1
                else:
                    print(f"[WARN] {name}: Sin datos")
            else:
                print(f"[ERROR] {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
    
    print(f"\n[SUMMARY] {working_queries}/{len(queries)} queries funcionando")
    return working_queries == len(queries)

if __name__ == "__main__":
    print("CORRIGIENDO DASHBOARD DE WINDOWS LOCAL")
    print("=" * 50)
    
    # Probar queries primero
    queries_ok = test_queries()
    
    if queries_ok:
        success, url = import_fixed_dashboard()
        
        if success:
            print("\n[SUCCESS] Dashboard corregido importado!")
            print(f"[ACCESS] Abre: {url}")
            print("[LOGIN] Credenciales: admin/admin")
            print("\n[FEATURES] El dashboard incluye:")
            print("   - System Status (UP/DOWN)")
            print("   - Load Average (1m)")
            print("   - System Uptime")
            print("   - Total Memory")
            print("   - Load Average Time Series")
            print("   - Memory Usage Time Series")
            print("   - Network I/O")
            print("   - Disk Usage")
        else:
            print("\n[ERROR] Error importando dashboard")
    else:
        print("\n[ERROR] Problemas con las queries de Prometheus")
        print("[INFO] Verifica que el Node Exporter este corriendo en puerto 9100")