#!/usr/bin/env python3
"""
Script para importar el dashboard de Windows Local a Grafana
"""

import requests
import json
import time
import sys

def import_dashboard():
    """Importar dashboard de Windows Local"""
    grafana_url = "http://localhost:3000"
    dashboard_file = "2-INICIAR-MONITOREO/config/grafana/dashboards/windows_local_dashboard.json"
    
    print("[INFO] Importando dashboard de Windows Local...")
    
    # Esperar a que Grafana esté disponible
    max_retries = 30
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
        print("[ERROR] Error: Grafana no esta disponible")
        return False
    
    try:
        # Leer el dashboard
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_json = json.load(f)
        
        # Preparar payload para importación
        payload = {
            "dashboard": dashboard_json,
            "overwrite": True,
            "message": "Imported Windows Local Dashboard"
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
            
            print("[OK] Dashboard importado exitosamente!")
            print(f"[URL] {dashboard_url}")
            print(f"[UID] {dashboard_uid}")
            return True
        else:
            print(f"[ERROR] Error importando dashboard: {response.status_code}")
            print(f"[RESPONSE] {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"[ERROR] No se encontro el archivo {dashboard_file}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def verify_metrics():
    """Verificar que las métricas estén disponibles"""
    print("\n[INFO] Verificando metricas de Windows Local...")
    
    prometheus_url = "http://localhost:9090"
    
    queries = [
        ("CPU", "up{instance=\"local-computer\"}"),
        ("Memory", "node_memory_MemTotal_bytes{instance=\"local-computer\"}"),
        ("Disk", "node_filesystem_size_bytes{instance=\"local-computer\"}"),
        ("Network", "node_network_receive_bytes_total{instance=\"local-computer\"}")
    ]
    
    for name, query in queries:
        try:
            response = requests.get(f"{prometheus_url}/api/v1/query", 
                                  params={'query': query}, timeout=5)
            if response.status_code == 200:
                data = response.json()['data']['result']
                if data:
                    print(f"[OK] {name}: Metricas disponibles")
                else:
                    print(f"[WARN] {name}: Sin datos")
            else:
                print(f"[ERROR] {name}: Error HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: Error - {e}")

if __name__ == "__main__":
    print("CONFIGURANDO DASHBOARD DE WINDOWS LOCAL")
    print("=" * 50)
    
    success = import_dashboard()
    verify_metrics()
    
    if success:
        print("\n[SUCCESS] Dashboard de Windows Local configurado exitosamente!")
        print("[FEATURES] Caracteristicas del dashboard:")
        print("   - CPU Usage en tiempo real")
        print("   - Memory Usage y estadisticas")
        print("   - Disk Usage por dispositivo")
        print("   - Network I/O")
        print("   - System Uptime")
        print("   - Load Average")
        print("   - CPU por modo (user, system, idle)")
        print("\n[ACCESS] Accede a: http://localhost:3000")
        print("[LOGIN] Credenciales: admin/admin")
    else:
        print("\n[ERROR] Error configurando dashboard")
        sys.exit(1)