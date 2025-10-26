#!/usr/bin/env python3
"""
Script de Diagnóstico de Métricas - Valores Reales
Muestra los valores reales que deberían aparecer en Grafana
"""

import requests
import json
import time
from datetime import datetime

def get_metric_value(query, description):
    """Obtiene el valor actual de una métrica"""
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
                return value, True
            else:
                return None, False
        else:
            return None, False
            
    except Exception as e:
        print(f"Error consultando {description}: {str(e)}")
        return None, False

def format_bytes(bytes_value):
    """Formatea bytes en unidades legibles"""
    if bytes_value >= 1024**3:
        return f"{bytes_value / (1024**3):.2f} GB"
    elif bytes_value >= 1024**2:
        return f"{bytes_value / (1024**2):.2f} MB"
    elif bytes_value >= 1024:
        return f"{bytes_value / 1024:.2f} KB"
    else:
        return f"{bytes_value:.0f} bytes"

def format_bps(bps_value):
    """Formatea bits por segundo"""
    if bps_value >= 1000000:
        return f"{bps_value / 1000000:.2f} Mbps"
    elif bps_value >= 1000:
        return f"{bps_value / 1000:.2f} Kbps"
    else:
        return f"{bps_value:.2f} bps"

def main():
    print("📊 OptiMon - Diagnóstico de Valores Reales")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # CPU Usage
    cpu_value, cpu_ok = get_metric_value(
        "100 - (avg(irate(windows_cpu_time_total{mode=\"idle\"}[5m])) * 100)",
        "CPU Usage"
    )
    
    # Memory Usage  
    memory_value, memory_ok = get_metric_value(
        "100 * (1 - (windows_memory_available_bytes / windows_memory_physical_total_bytes))",
        "Memory Usage"
    )
    
    # Memory Available
    memory_available, mem_avail_ok = get_metric_value(
        "windows_memory_available_bytes",
        "Memory Available"
    )
    
    # Memory Total
    memory_total, mem_total_ok = get_metric_value(
        "windows_memory_physical_total_bytes",
        "Memory Total"
    )
    
    # Disk Usage
    disk_value, disk_ok = get_metric_value(
        "100 - ((windows_logical_disk_free_bytes{volume=\"C:\"} / windows_logical_disk_size_bytes{volume=\"C:\"}) * 100)",
        "Disk Usage"
    )
    
    # Disk Free
    disk_free, disk_free_ok = get_metric_value(
        "windows_logical_disk_free_bytes{volume=\"C:\"}",
        "Disk Free"
    )
    
    # Disk Total
    disk_total, disk_total_ok = get_metric_value(
        "windows_logical_disk_size_bytes{volume=\"C:\"}",
        "Disk Total"
    )
    
    # Network Received
    net_rx, net_rx_ok = get_metric_value(
        "rate(windows_net_bytes_received_total[5m]) * 8",
        "Network Received"
    )
    
    # Network Sent
    net_tx, net_tx_ok = get_metric_value(
        "rate(windows_net_bytes_sent_total[5m]) * 8",
        "Network Sent"
    )
    
    print("🖥️  MÉTRICAS DEL SISTEMA:")
    print("-" * 40)
    
    # CPU
    if cpu_ok:
        print(f"🔥 CPU Usage: {cpu_value:.2f}%")
        if cpu_value < 0 or cpu_value > 100:
            print("   ⚠️  ALERTA: Valor fuera de rango normal (0-100%)")
    else:
        print("❌ CPU Usage: No disponible")
    
    print()
    
    # Memory
    if memory_ok and mem_avail_ok and mem_total_ok:
        print(f"💾 Memory Usage: {memory_value:.2f}%")
        print(f"   Available: {format_bytes(memory_available)}")
        print(f"   Total: {format_bytes(memory_total)}")
        
        # Verificación manual del cálculo
        manual_memory_usage = 100 * (1 - (memory_available / memory_total))
        print(f"   Verificación: {manual_memory_usage:.2f}%")
        
        if memory_value < 0 or memory_value > 100:
            print("   ⚠️  ALERTA: Valor fuera de rango normal (0-100%)")
    else:
        print("❌ Memory Usage: No disponible")
    
    print()
    
    # Disk
    if disk_ok and disk_free_ok and disk_total_ok:
        print(f"💿 Disk Usage (C:): {disk_value:.2f}%")
        print(f"   Free: {format_bytes(disk_free)}")
        print(f"   Total: {format_bytes(disk_total)}")
        
        # Verificación manual del cálculo
        manual_disk_usage = 100 - ((disk_free / disk_total) * 100)
        print(f"   Verificación: {manual_disk_usage:.2f}%")
        
        if disk_value < 0 or disk_value > 100:
            print("   ⚠️  ALERTA: Valor fuera de rango normal (0-100%)")
    else:
        print("❌ Disk Usage: No disponible")
    
    print()
    
    # Network
    if net_rx_ok and net_tx_ok:
        print(f"🌐 Network Traffic:")
        print(f"   Received: {format_bps(net_rx)}")
        print(f"   Sent: {format_bps(net_tx)}")
        
        if net_rx < 0 or net_tx < 0:
            print("   ⚠️  ALERTA: Valores negativos detectados")
    else:
        print("❌ Network Traffic: No disponible")
    
    print()
    print("=" * 60)
    
    # Resumen de problemas
    problems = []
    
    if cpu_ok and (cpu_value < 0 or cpu_value > 100):
        problems.append("CPU con valores fuera de rango")
    
    if memory_ok and (memory_value < 0 or memory_value > 100):
        problems.append("Memoria con valores fuera de rango")
    
    if disk_ok and (disk_value < 0 or disk_value > 100):
        problems.append("Disco con valores fuera de rango")
    
    if net_rx_ok and net_rx < 0:
        problems.append("Red RX con valores negativos")
    
    if net_tx_ok and net_tx < 0:
        problems.append("Red TX con valores negativos")
    
    if not problems:
        print("✅ TODAS LAS MÉTRICAS ESTÁN EN RANGOS NORMALES")
        print()
        print("🎯 Los valores mostrados arriba son los que deberían")
        print("   aparecer en Grafana. Si ves valores diferentes,")
        print("   el problema está en las queries del dashboard.")
    else:
        print("⚠️  PROBLEMAS DETECTADOS:")
        for problem in problems:
            print(f"   - {problem}")
        print()
        print("🔧 SOLUCIONES:")
        print("   - Verificar que las queries de Prometheus estén correctas")
        print("   - Comprobar que las métricas de Windows Exporter funcionen")
        print("   - Reiniciar Windows Exporter si es necesario")
    
    print()
    print("🔄 Para actualizar Grafana:")
    print("   1. docker compose restart grafana")
    print("   2. Abrir http://localhost:3000")
    print("   3. Verificar dashboard 'OptiMon - Windows System Monitoring'")

if __name__ == "__main__":
    main()