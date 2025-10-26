#!/usr/bin/env python3
"""
Script para probar las queries directamente como las haría Grafana
y mostrar exactamente qué valores está obteniendo
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_grafana_query(query, description, panel_id=None):
    """Prueba una query exactamente como Grafana lo haría"""
    try:
        # Parámetros similares a los que usa Grafana
        end_time = int(time.time())
        start_time = end_time - 3600  # última hora
        
        url = "http://localhost:9090/api/v1/query_range"
        params = {
            'query': query,
            'start': start_time,
            'end': end_time,
            'step': '15s'  # cada 15 segundos
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and data['data']['result']:
                # Obtener los últimos valores
                result = data['data']['result'][0]
                values = result['values']
                
                if values:
                    # Últimos 5 valores
                    last_values = [float(val[1]) for val in values[-5:]]
                    current_value = last_values[-1]
                    max_value = max(last_values)
                    min_value = min(last_values)
                    
                    print(f"✅ {description}")
                    print(f"   Query: {query}")
                    print(f"   Valor actual: {current_value:.2f}")
                    print(f"   Rango (últimos 5): {min_value:.2f} - {max_value:.2f}")
                    
                    # Verificar si hay valores problemáticos
                    if any(v > 100 for v in last_values) or any(v < 0 for v in last_values):
                        problematic = [v for v in last_values if v > 100 or v < 0]
                        print(f"   ⚠️  VALORES PROBLEMÁTICOS: {problematic}")
                        return False, current_value
                    else:
                        print(f"   ✅ Todos los valores en rango normal")
                        return True, current_value
                else:
                    print(f"⚠️  {description}")
                    print(f"   Query: {query}")
                    print(f"   Sin valores en el rango de tiempo")
                    return False, None
            else:
                print(f"❌ {description}")
                print(f"   Query: {query}")
                print(f"   Error: {data.get('error', 'Sin resultados')}")
                return False, None
        else:
            print(f"❌ {description}")
            print(f"   Query: {query}")
            print(f"   HTTP Error: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Query: {query}")
        print(f"   Exception: {str(e)}")
        return False, None

def test_instant_query(query, description):
    """Prueba una query instantánea"""
    try:
        url = "http://localhost:9090/api/v1/query"
        params = {
            'query': query,
            'time': int(time.time())
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and data['data']['result']:
                value = float(data['data']['result'][0]['value'][1])
                print(f"✅ {description}: {value:.2f}")
                return True, value
            else:
                print(f"❌ {description}: Sin datos")
                return False, None
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False, None

def main():
    print("🔍 Prueba de Queries como Grafana")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Queries que usa Grafana (exactamente como aparecen en el dashboard)
    queries = [
        # Query original de CPU que puede estar causando problemas
        ("100 - (avg(irate(windows_cpu_time_total{mode=\"idle\"}[5m])) * 100)", "CPU Usage (Query Original)"),
        
        # Query alternativa de CPU
        ("(1 - avg(irate(windows_cpu_time_total{mode=\"idle\"}[5m]))) * 100", "CPU Usage (Query Alternativa)"),
        
        # Query de memoria corregida
        ("100 * (1 - (windows_memory_available_bytes / windows_memory_physical_total_bytes))", "Memory Usage (Corregida)"),
        
        # Query de memoria alternativa
        ("(1 - (windows_memory_available_bytes / windows_memory_physical_total_bytes)) * 100", "Memory Usage (Alternativa)"),
        
        # Query de disco
        ("100 - ((windows_logical_disk_free_bytes{volume=\"C:\"} / windows_logical_disk_size_bytes{volume=\"C:\"}) * 100)", "Disk Usage"),
        
        # Queries de red
        ("rate(windows_net_bytes_received_total[5m]) * 8", "Network RX (bps)"),
        ("rate(windows_net_bytes_sent_total[5m]) * 8", "Network TX (bps)")
    ]
    
    print("📊 Probando queries con datos de series temporales:")
    print("-" * 60)
    
    success_count = 0
    total_count = len(queries)
    
    for query, description in queries:
        success, value = test_grafana_query(query, description)
        if success:
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Resumen: {success_count}/{total_count} queries sin problemas")
    
    # También probar queries instantáneas para comparar
    print("\n🎯 Valores instantáneos actuales:")
    print("-" * 30)
    
    instant_queries = [
        ("100 - (avg(irate(windows_cpu_time_total{mode=\"idle\"}[5m])) * 100)", "CPU %"),
        ("100 * (1 - (windows_memory_available_bytes / windows_memory_physical_total_bytes))", "Memory %"),
        ("100 - ((windows_logical_disk_free_bytes{volume=\"C:\"} / windows_logical_disk_size_bytes{volume=\"C:\"}) * 100)", "Disk %")
    ]
    
    for query, desc in instant_queries:
        test_instant_query(query, desc)
    
    print("\n" + "=" * 60)
    print("🔧 ACCIONES RECOMENDADAS:")
    print("1. Abrir Grafana: http://localhost:3000")
    print("2. Buscar dashboard: 'OptiMon - DASHBOARD CORREGIDO v2'")
    print("3. Si aún ves valores > 100%, usar el nuevo dashboard creado")
    print("4. Verificar que el datasource Prometheus esté configurado")

if __name__ == "__main__":
    main()