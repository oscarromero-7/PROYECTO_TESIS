#!/usr/bin/env python3
"""
Script de prueba para instalación automática de Windows Exporter a través del dashboard
"""

import requests
import time
import json
import subprocess

def test_dashboard_installation():
    """Prueba la instalación automática de Windows Exporter a través del dashboard"""
    
    print("🧪 Iniciando prueba de instalación automática de Windows Exporter")
    print("=" * 60)
    
    # URL del dashboard
    dashboard_url = "http://localhost:5000"
    install_url = f"{dashboard_url}/api/local/install-node-exporter"
    status_url = f"{dashboard_url}/api/monitoring/status"
    
    try:
        # 1. Verificar que el dashboard esté funcionando
        print("1️⃣ Verificando dashboard...")
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accesible")
        else:
            print(f"❌ Dashboard no accesible: {response.status_code}")
            return False
        
        # 2. Verificar estado inicial
        print("\n2️⃣ Verificando estado inicial...")
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"   Prometheus: {'✅' if status.get('prometheus', {}).get('running') else '❌'}")
            print(f"   Grafana: {'✅' if status.get('grafana', {}).get('running') else '❌'}")
            print(f"   AlertManager: {'✅' if status.get('alertmanager', {}).get('running') else '❌'}")
            print(f"   Windows Exporter: {'✅' if status.get('node_exporter', {}).get('running') else '❌'}")
        else:
            print("❌ No se pudo obtener el estado inicial")
        
        # 3. Realizar instalación automática
        print("\n3️⃣ Iniciando instalación automática...")
        response = requests.post(install_url, timeout=120)  # Timeout de 2 minutos
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Instalación exitosa")
                print(f"   Mensaje: {result.get('message')}")
                if 'details' in result:
                    print(f"   Puerto: {result['details'].get('port')}")
                    print(f"   Métricas URL: {result['details'].get('metrics_url')}")
            else:
                print(f"❌ Error en la instalación: {result.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP en la instalación: {response.status_code}")
            return False
        
        # 4. Esperar un momento para que el servicio se inicie
        print("\n4️⃣ Esperando inicio del servicio...")
        time.sleep(5)
        
        # 5. Verificar que Windows Exporter esté funcionando
        print("\n5️⃣ Verificando Windows Exporter...")
        try:
            metrics_response = requests.get("http://localhost:9182/metrics", timeout=10)
            if metrics_response.status_code == 200:
                metrics_lines = metrics_response.text.split('\n')
                metric_count = len([line for line in metrics_lines if line and not line.startswith('#')])
                print(f"✅ Windows Exporter funcionando con {metric_count} métricas")
            else:
                print(f"❌ Windows Exporter no responde: {metrics_response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error conectando a Windows Exporter: {e}")
            return False
        
        # 6. Verificar estado final
        print("\n6️⃣ Verificando estado final...")
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"   Prometheus: {'✅' if status.get('prometheus', {}).get('running') else '❌'}")
            print(f"   Grafana: {'✅' if status.get('grafana', {}).get('running') else '❌'}")
            print(f"   AlertManager: {'✅' if status.get('alertmanager', {}).get('running') else '❌'}")
            print(f"   Windows Exporter: {'✅' if status.get('node_exporter', {}).get('running') else '❌'}")
            print(f"   Targets activos: {status.get('targets', 0)}")
        
        print("\n🎉 Prueba de instalación automática completada exitosamente")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def verify_prometheus_targets():
    """Verifica que Prometheus esté recogiendo métricas de Windows Exporter"""
    
    print("\n🎯 Verificando integración con Prometheus...")
    try:
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            targets = data.get('data', {}).get('activeTargets', [])
            
            windows_targets = [t for t in targets if '9182' in t.get('scrapeUrl', '')]
            
            if windows_targets:
                target = windows_targets[0]
                health = target.get('health', 'unknown')
                print(f"✅ Target de Windows Exporter encontrado")
                print(f"   Estado: {health}")
                print(f"   URL: {target.get('scrapeUrl', 'N/A')}")
                print(f"   Último scrape: {target.get('lastScrape', 'N/A')}")
                return health == 'up'
            else:
                print("❌ No se encontró target de Windows Exporter en Prometheus")
                return False
        else:
            print(f"❌ Error consultando Prometheus: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando Prometheus: {e}")
        return False

def main():
    print("🚀 PRUEBA COMPLETA DE INSTALACIÓN AUTOMÁTICA")
    print("=" * 60)
    
    # Ejecutar prueba de instalación
    install_success = test_dashboard_installation()
    
    if install_success:
        # Verificar integración con Prometheus
        time.sleep(10)  # Esperar a que Prometheus haga scrape
        prometheus_success = verify_prometheus_targets()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📋 RESUMEN FINAL")
        print(f"Instalación automática: {'✅ ÉXITO' if install_success else '❌ FALLO'}")
        print(f"Integración Prometheus: {'✅ ÉXITO' if prometheus_success else '❌ FALLO'}")
        
        if install_success and prometheus_success:
            print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
            print("🌐 Sistema de monitoreo completamente funcional")
            return True
        else:
            print("\n⚠️ Algunas pruebas fallaron")
            return False
    else:
        print("\n❌ Falló la instalación automática")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)