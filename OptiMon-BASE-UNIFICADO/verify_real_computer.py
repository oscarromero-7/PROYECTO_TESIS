#!/usr/bin/env python3
"""
OptiMon - Sistema Unificado de Monitoreo v3.0.0
Script consolidado de verificación y gestión completa
"""

import requests
import json
import time
import webbrowser
import subprocess
import sys
from datetime import datetime

class OptiMonManager:
    def __init__(self):
        self.base_url_grafana = "http://localhost:3000"
        self.base_url_prometheus = "http://localhost:9090" 
        self.base_url_windows = "http://localhost:9182"
        self.credentials = ('admin', 'admin')
    
    def check_services(self):
        """Verificar todos los servicios"""
        print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
        print("=" * 50)
        
        services = [
            ("Grafana", f"{self.base_url_grafana}/api/health"),
            ("Prometheus", f"{self.base_url_prometheus}/-/healthy"),
            ("Windows Exporter", f"{self.base_url_windows}/metrics"),
        ]
        
        results = {}
        for name, url in services:
            try:
                if name == "Windows Exporter":
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200 and "windows_memory" in response.text:
                        results[name] = "✅ FUNCIONANDO"
                    else:
                        results[name] = "❌ SIN MÉTRICAS"
                else:
                    response = requests.get(url, timeout=5)
                    results[name] = "✅ FUNCIONANDO" if response.status_code == 200 else f"❌ ERROR {response.status_code}"
            except:
                results[name] = "❌ NO RESPONDE"
        
        for service, status in results.items():
            print(f"{status} {service}")
        
        return all("✅" in status for status in results.values())
    
    def verify_metrics_availability(self):
        """Verificar métricas específicas disponibles"""
        print("\n📊 VERIFICANDO MÉTRICAS CRÍTICAS...")
        
        required_metrics = [
            "windows_memory_physical_total_bytes",
            "windows_memory_available_bytes",
            "windows_cpu_time_total",
            "windows_logical_disk_size_bytes",
            "windows_logical_disk_free_bytes",
            "windows_system_processes"
        ]
        
        try:
            response = requests.get(f"{self.base_url_windows}/metrics", timeout=10)
            if response.status_code != 200:
                print("❌ Error accediendo a métricas")
                return False
            
            metrics_text = response.text
            found_metrics = {}
            
            for metric in required_metrics:
                if metric in metrics_text:
                    found_metrics[metric] = "✅"
                else:
                    found_metrics[metric] = "❌"
            
            for metric, status in found_metrics.items():
                print(f"  {status} {metric}")
            
            return all(status == "✅" for status in found_metrics.values())
            
        except Exception as e:
            print(f"❌ Error verificando métricas: {e}")
            return False
    
    def test_prometheus_queries(self):
        """Probar queries específicas"""
        print("\n🧪 PROBANDO QUERIES DE PROMETHEUS...")
        
        queries = [
            ("CPU", '100 - (avg(irate(windows_cpu_time_total{job="windows_local",mode="idle"}[5m])) * 100)'),
            ("Memoria", '100 * (1 - (windows_memory_available_bytes{job="windows_local"} / windows_memory_physical_total_bytes{job="windows_local"}))'),
            ("Disco", '100 - ((windows_logical_disk_free_bytes{job="windows_local",volume="C:"} / windows_logical_disk_size_bytes{job="windows_local",volume="C:"}) * 100)'),
            ("Procesos", 'windows_system_processes{job="windows_local"}')
        ]
        
        results = {}
        for name, query in queries:
            try:
                response = requests.get(
                    f"{self.base_url_prometheus}/api/v1/query",
                    params={'query': query},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success' and data['data']['result']:
                        value = float(data['data']['result'][0]['value'][1])
                        results[name] = f"✅ {value:.2f}"
                        print(f"  ✅ {name}: {value:.2f}")
                    else:
                        results[name] = "❌ Sin datos"
                        print(f"  ❌ {name}: Sin datos")
                else:
                    results[name] = f"❌ HTTP {response.status_code}"
                    print(f"  ❌ {name}: Error HTTP {response.status_code}")
                    
            except Exception as e:
                results[name] = f"❌ Error: {e}"
                print(f"  ❌ {name}: Error - {e}")
        
        return all("✅" in result for result in results.values()), results
    
    def restart_grafana(self):
        """Reiniciar contenedor de Grafana"""
        print("\n🔄 REINICIANDO GRAFANA...")
        try:
            subprocess.run(["docker", "compose", "restart", "grafana"], 
                         check=True, capture_output=True)
            print("✅ Grafana reiniciado")
            time.sleep(5)  # Esperar a que inicie
            return True
        except Exception as e:
            print(f"❌ Error reiniciando Grafana: {e}")
            return False
    
    def open_dashboard(self):
        """Abrir dashboard en navegador"""
        print("\n🌐 ABRIENDO DASHBOARD...")
        
        try:
            # Abrir Grafana principal
            webbrowser.open(self.base_url_grafana)
            time.sleep(2)
            
            # Intentar abrir dashboard específico
            dashboard_url = f"{self.base_url_grafana}/d/optimon-real-computer/monitoreo-tu-computadora-100-real"
            webbrowser.open(dashboard_url)
            
            print("🎯 Dashboard abierto en tu navegador")
            return True
            
        except Exception as e:
            print(f"⚠️ No se pudo abrir automáticamente: {e}")
            print(f"   Abrir manualmente: {self.base_url_grafana}")
            return False
    
    def create_enhanced_dashboard(self):
        """Crear dashboard mejorado con gráficos avanzados"""
        print("\n📊 CREANDO/ACTUALIZANDO DASHBOARD AVANZADO...")
        
        enhanced_dashboard = {
            "dashboard": {
                "id": None,
                "title": "🖥️ TU COMPUTADORA - MONITOREO AVANZADO",
                "tags": ["windows", "monitoring", "real-computer", "advanced"],
                "timezone": "browser",
                "panels": [
                    # Panel de valores actuales
                    {
                        "id": 1,
                        "title": "🖥️ ESTADO ACTUAL DE TU COMPUTADORA",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": '100 - (avg(irate(windows_cpu_time_total{job="windows_local",mode="idle"}[5m])) * 100)',
                                "legendFormat": "🖥️ CPU"
                            },
                            {
                                "expr": '100 * (1 - (windows_memory_available_bytes{job="windows_local"} / windows_memory_physical_total_bytes{job="windows_local"}))',
                                "legendFormat": "🧠 Memoria"
                            },
                            {
                                "expr": '100 - ((windows_logical_disk_free_bytes{job="windows_local",volume="C:"} / windows_logical_disk_size_bytes{job="windows_local",volume="C:"}) * 100)',
                                "legendFormat": "💿 Disco C:"
                            },
                            {
                                "expr": 'windows_system_processes{job="windows_local"}',
                                "legendFormat": "📋 Procesos"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 70},
                                        {"color": "red", "value": 90}
                                    ]
                                }
                            },
                            "overrides": [
                                {
                                    "matcher": {"id": "byName", "options": "📋 Procesos"},
                                    "properties": [
                                        {"id": "unit", "value": "short"},
                                        {"id": "max", "value": 500}
                                    ]
                                }
                            ]
                        },
                        "options": {
                            "colorMode": "background",
                            "graphMode": "area",
                            "orientation": "horizontal"
                        },
                        "gridPos": {"h": 6, "w": 24, "x": 0, "y": 0}
                    },
                    # Gráfico de tendencias combinado
                    {
                        "id": 2,
                        "title": "📈 TENDENCIAS - TU COMPUTADORA",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": '100 - (avg(irate(windows_cpu_time_total{job="windows_local",mode="idle"}[5m])) * 100)',
                                "legendFormat": "🖥️ CPU %"
                            },
                            {
                                "expr": '100 * (1 - (windows_memory_available_bytes{job="windows_local"} / windows_memory_physical_total_bytes{job="windows_local"}))',
                                "legendFormat": "🧠 Memoria %"
                            },
                            {
                                "expr": '100 - ((windows_logical_disk_free_bytes{job="windows_local",volume="C:"} / windows_logical_disk_size_bytes{job="windows_local",volume="C:"}) * 100)',
                                "legendFormat": "💿 Disco C: %"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                                "custom": {
                                    "drawStyle": "line",
                                    "lineWidth": 2,
                                    "fillOpacity": 10,
                                    "gradientMode": "opacity"
                                }
                            }
                        },
                        "options": {
                            "legend": {
                                "displayMode": "table",
                                "placement": "right",
                                "calcs": ["lastNotNull", "max", "mean"]
                            }
                        },
                        "gridPos": {"h": 9, "w": 24, "x": 0, "y": 6}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s",
                "schemaVersion": 30,
                "version": 1
            },
            "folderId": 0,
            "overwrite": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url_grafana}/api/dashboards/db",
                json=enhanced_dashboard,
                auth=self.credentials,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print("✅ Dashboard avanzado creado/actualizado")
                return True
            else:
                print(f"❌ Error creando dashboard: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_complete_verification(self):
        """Ejecutar verificación completa y solucionar problemas"""
        print("🖥️ OPTIMON - VERIFICACIÓN Y SOLUCIÓN COMPLETA")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Paso 1: Verificar servicios
        if not self.check_services():
            print("\n❌ SERVICIOS NO FUNCIONALES")
            print("💡 SOLUCIÓN: Ejecutar 'docker compose up -d' y reintentar")
            return False
        
        # Paso 2: Verificar métricas
        if not self.verify_metrics_availability():
            print("\n❌ MÉTRICAS NO DISPONIBLES")
            print("💡 SOLUCIÓN: Verificar Windows Exporter en puerto 9182")
            return False
        
        # Paso 3: Probar queries
        queries_ok, results = self.test_prometheus_queries()
        if not queries_ok:
            print("\n❌ QUERIES NO FUNCIONAN")
            print("💡 SOLUCIÓN: Verificar configuración de Prometheus")
            return False
        
        # Paso 4: Crear/actualizar dashboard
        if not self.create_enhanced_dashboard():
            print("\n❌ DASHBOARD NO CREADO")
            return False
        
        # Paso 5: Reiniciar Grafana para cargar cambios
        if not self.restart_grafana():
            print("\n⚠️ Grafana no reiniciado, pero dashboard debería funcionar")
        
        # Paso 6: Abrir dashboard
        self.open_dashboard()
        
        print("\n🎉 ¡VERIFICACIÓN COMPLETA EXITOSA!")
        print("✅ Servicios funcionando")
        print("✅ Métricas disponibles")
        print("✅ Queries funcionando")
        print("✅ Dashboard creado/actualizado")
        print("✅ Sistema completamente operativo")
        
        print("\n📊 MÉTRICAS ACTUALES:")
        for metric, value in results.items():
            print(f"  {value} {metric}")
        
        print("\n🎯 ACCESO AL SISTEMA:")
        print("🌐 Grafana: http://localhost:3000")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin")
        print("📊 Dashboard: 'TU COMPUTADORA - MONITOREO AVANZADO'")
        
        print("\n🚀 CARACTERÍSTICAS DEL SISTEMA:")
        print("✅ Monitoreo 100% de TU computadora real")
        print("✅ Valores precisos entre 0-100%")
        print("✅ Gráficos avanzados y tendencias")
        print("✅ Actualización automática cada 10s")
        print("✅ Completamente automatizado")
        
        return True

def main():
    manager = OptiMonManager()
    success = manager.run_complete_verification()
    
    if not success:
        print("\n❌ VERIFICACIÓN FALLÓ")
        print("🔧 Revisa los mensajes de error arriba")
        sys.exit(1)
    else:
        print("\n✅ ¡SISTEMA COMPLETAMENTE OPERATIVO!")

if __name__ == "__main__":
    main()