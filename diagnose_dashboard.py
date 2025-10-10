#!/usr/bin/env python3
"""
Script para diagnosticar y resolver completamente el problema del dashboard
"""

import requests
import json
import time

def test_prometheus_directly():
    """Probar conexión directa a Prometheus"""
    print("[INFO] Probando conexion directa a Prometheus...")
    
    queries = {
        "System Status": "up{instance=\"local-computer\"}",
        "Load Average": "node_load1{instance=\"local-computer\"}",
        "Memory Total": "node_memory_MemTotal_bytes{instance=\"local-computer\"}"
    }
    
    working = 0
    for name, query in queries.items():
        try:
            response = requests.get(f"http://localhost:9090/api/v1/query", 
                                  params={'query': query}, timeout=5)
            if response.status_code == 200:
                data = response.json()['data']['result']
                if data:
                    value = data[0]['value'][1]
                    print(f"[OK] {name}: {value}")
                    working += 1
                else:
                    print(f"[WARN] {name}: Sin datos")
            else:
                print(f"[ERROR] {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
    
    return working == len(queries)

def test_grafana_datasource():
    """Probar el datasource de Grafana"""
    print("\n[INFO] Probando datasource de Grafana...")
    
    try:
        # Obtener información del datasource
        response = requests.get("http://localhost:3000/api/datasources/1", 
                              auth=('admin', 'admin'))
        if response.status_code == 200:
            ds_info = response.json()
            print(f"[OK] Datasource: {ds_info['name']} ({ds_info['type']})")
            print(f"[URL] {ds_info['url']}")
            print(f"[UID] {ds_info['uid']}")
            
            # Probar query a través del datasource
            response = requests.get(
                "http://localhost:3000/api/datasources/proxy/1/api/v1/query",
                params={'query': 'up{instance="local-computer"}'},
                auth=('admin', 'admin')
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('result'):
                    value = data['data']['result'][0]['value'][1]
                    print(f"[OK] Query via Grafana: {value}")
                    return True
                else:
                    print("[WARN] Query sin resultados")
            else:
                print(f"[ERROR] Query error: {response.status_code}")
                print(f"[RESPONSE] {response.text}")
            
        else:
            print(f"[ERROR] Error obteniendo datasource: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    
    return False

def create_simple_dashboard():
    """Crear un dashboard muy simple para probar"""
    print("\n[INFO] Creando dashboard de prueba simple...")
    
    simple_dashboard = {
        "dashboard": {
            "id": None,
            "title": "Test Windows Local - Simple",
            "uid": "test-windows-simple",
            "tags": ["test", "windows"],
            "timezone": "",
            "panels": [
                {
                    "id": 1,
                    "title": "System Status",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "up{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "red", "value": 0}
                                ]
                            }
                        }
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "calcs": ["lastNotNull"],
                            "fields": ""
                        },
                        "orientation": "auto",
                        "textMode": "auto",
                        "colorMode": "background",
                        "graphMode": "area",
                        "justifyMode": "center"
                    }
                },
                {
                    "id": 2,
                    "title": "Load Average",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "node_load1{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            }
                        }
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "calcs": ["lastNotNull"],
                            "fields": ""
                        },
                        "orientation": "auto",
                        "textMode": "auto",
                        "colorMode": "value",
                        "graphMode": "area",
                        "justifyMode": "center"
                    }
                }
            ],
            "time": {"from": "now-5m", "to": "now"},
            "refresh": "5s"
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/dashboards/db",
            json=simple_dashboard,
            headers={'Content-Type': 'application/json'},
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            result = response.json()
            dashboard_url = f"http://localhost:3000/d/{result.get('uid', 'test-windows-simple')}"
            print(f"[OK] Dashboard simple creado: {dashboard_url}")
            return True, dashboard_url
        else:
            print(f"[ERROR] Error creando dashboard: {response.status_code}")
            print(f"[RESPONSE] {response.text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False, None

if __name__ == "__main__":
    print("DIAGNOSTICO COMPLETO DEL DASHBOARD")
    print("=" * 50)
    
    # Paso 1: Probar Prometheus directamente
    prometheus_ok = test_prometheus_directly()
    
    # Paso 2: Probar datasource de Grafana
    grafana_ok = test_grafana_datasource()
    
    # Paso 3: Crear dashboard simple de prueba
    if prometheus_ok and grafana_ok:
        success, url = create_simple_dashboard()
        
        if success:
            print(f"\n[SUCCESS] Dashboard de prueba creado exitosamente!")
            print(f"[ACCESS] Abre: {url}")
            print("[INFO] Este dashboard simple deberia mostrar datos")
            print("[NEXT] Si este funciona, el problema era de complejidad del dashboard")
        else:
            print("\n[ERROR] Fallo creando dashboard simple")
    else:
        print("\n[ERROR] Problemas base detectados:")
        if not prometheus_ok:
            print("  - Prometheus no responde correctamente")
        if not grafana_ok:
            print("  - Datasource de Grafana no funciona")
    
    print("\n[SUMMARY]")
    print(f"  Prometheus directo: {'OK' if prometheus_ok else 'ERROR'}")
    print(f"  Grafana datasource: {'OK' if grafana_ok else 'ERROR'}")
    print("  Dashboard simple: Creado para prueba")