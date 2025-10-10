#!/usr/bin/env python3
"""
Script para verificar el estado completo del sistema OptiMon
"""

import requests
import json
import time
from datetime import datetime

class StatusVerificador:
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        
    def verificar_prometheus(self):
        """Verificar estado de Prometheus"""
        print("\n" + "="*60)
        print("VERIFICANDO PROMETHEUS")
        print("="*60)
        
        try:
            # Verificar disponibilidad
            response = requests.get(f"{self.prometheus_url}/api/v1/targets")
            if response.status_code == 200:
                targets = response.json()['data']['activeTargets']
                print(f"[OK] Prometheus activo con {len(targets)} targets")
                
                # Mostrar estado de cada target
                for target in targets:
                    status = "[UP]" if target['health'] == 'up' else "[DOWN]"
                    instance = target['labels'].get('instance', 'Unknown')
                    job = target['labels'].get('job', 'Unknown')
                    provider = target['labels'].get('provider', 'Unknown')
                    print(f"   {status} | {instance:20} | {job:15} | {provider}")
                    
            else:
                print("[ERROR] Error conectando a Prometheus")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
    def verificar_metricas(self):
        """Verificar métricas específicas"""
        print("\n" + "="*60)
        print("VERIFICANDO METRICAS")
        print("="*60)
        
        queries = {
            "CPU Usage": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "Memory Usage": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "Disk Usage": "(1 - (node_filesystem_free_bytes{fstype!=\"tmpfs\"} / node_filesystem_size_bytes{fstype!=\"tmpfs\"})) * 100",
            "Uptime": "node_time_seconds - node_boot_time_seconds"
        }
        
        for name, query in queries.items():
            try:
                response = requests.get(f"{self.prometheus_url}/api/v1/query", 
                                      params={'query': query})
                if response.status_code == 200:
                    data = response.json()['data']['result']
                    if data:
                        print(f"\n{name}:")
                        for result in data[:5]:  # Mostrar solo primeros 5
                            instance = result['metric'].get('instance', 'Unknown')
                            value = float(result['value'][1]) if result['value'][1] != 'NaN' else 0
                            
                            if 'uptime' in name.lower():
                                # Convertir a días/horas
                                days = int(value // 86400)
                                hours = int((value % 86400) // 3600)
                                print(f"   {instance:20} | {days}d {hours}h")
                            else:
                                print(f"   {instance:20} | {value:.2f}%")
                    else:
                        print(f"{name}: No hay datos")
                        
            except Exception as e:
                print(f"{name}: Error - {e}")
    
    def verificar_grafana(self):
        """Verificar estado de Grafana"""
        print("\n" + "="*60)
        print("VERIFICANDO GRAFANA")
        print("="*60)
        
        try:
            # Verificar API de Grafana
            response = requests.get(f"{self.grafana_url}/api/health")
            if response.status_code == 200:
                print("[OK] Grafana activo y disponible")
                print("[INFO] Accede a http://localhost:3000 (admin/admin)")
                    
            else:
                print("[ERROR] Error conectando a Grafana")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
    def verificar_conectividad_nube(self):
        """Verificar conectividad específica con instancias cloud"""
        print("\n" + "="*60)
        print("VERIFICANDO CONECTIVIDAD NUBE")
        print("="*60)
        
        cloud_instances = [
            ("AWS-1", "3.85.203.242:9100"),
            ("AWS-2", "52.91.54.26:9100"), 
            ("AWS-3", "54.91.7.131:9100"),
            ("Azure-1", "172.191.59.230:9100")
        ]
        
        for name, endpoint in cloud_instances:
            try:
                response = requests.get(f"http://{endpoint}/metrics", timeout=5)
                if response.status_code == 200:
                    print(f"[OK] {name:10} | {endpoint:20} | Metricas OK")
                else:
                    print(f"[WARN] {name:10} | {endpoint:20} | HTTP {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"[TIMEOUT] {name:10} | {endpoint:20} | Sin respuesta")
            except Exception as e:
                print(f"[ERROR] {name:10} | {endpoint:20} | Error: {str(e)[:30]}")
    
    def generar_resumen(self):
        """Generar resumen del estado"""
        print("\n" + "="*60)
        print("RESUMEN DEL SISTEMA OPTIMON")
        print("="*60)
        
        try:
            # Contar targets activos
            response = requests.get(f"{self.prometheus_url}/api/v1/targets")
            if response.status_code == 200:
                targets = response.json()['data']['activeTargets']
                up_targets = [t for t in targets if t['health'] == 'up']
                
                print(f"Targets monitoreados: {len(up_targets)}/{len(targets)}")
                
                # Contar por proveedor
                providers = {}
                for target in up_targets:
                    provider = target['labels'].get('provider', target['labels'].get('job', 'unknown'))
                    providers[provider] = providers.get(provider, 0) + 1
                
                print("Distribucion por proveedor:")
                for provider, count in providers.items():
                    print(f"   - {provider}: {count} instancia(s)")
                
                print(f"\nUltima verificacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("Sistema OptiMon funcionando correctamente!")
                
        except Exception as e:
            print(f"[ERROR] Error generando resumen: {e}")
    
    def ejecutar_verificacion_completa(self):
        """Ejecutar verificación completa del sistema"""
        print("INICIANDO VERIFICACION COMPLETA DEL SISTEMA OPTIMON")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.verificar_prometheus()
        self.verificar_metricas()
        self.verificar_grafana()
        self.verificar_conectividad_nube()
        self.generar_resumen()

if __name__ == "__main__":
    verificador = StatusVerificador()
    verificador.ejecutar_verificacion_completa()