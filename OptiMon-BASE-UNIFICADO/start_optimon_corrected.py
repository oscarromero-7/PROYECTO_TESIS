import requests
import json
import time
import subprocess
import sys

def start_services():
    """Iniciar los servicios de Docker"""
    print("🚀 Iniciando servicios...")
    try:
        subprocess.run(["docker", "compose", "up", "-d"], check=True, cwd=".")
        print("✅ Servicios iniciados correctamente")
        time.sleep(10)  # Dar tiempo para que se inicien
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando servicios: {e}")
        return False

def wait_for_grafana():
    """Esperar a que Grafana esté disponible"""
    print("⏳ Esperando a que Grafana esté disponible...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana está disponible")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(f"   Intento {attempt + 1}/{max_attempts}")
    
    print("❌ Grafana no está disponible después de 60 segundos")
    return False

def import_dashboard():
    """Importar el dashboard corregido a Grafana"""
    print("📊 Importando dashboard corregido...")
    
    dashboard_path = "config/grafana/dashboard_windows_corrected.json"
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        
        response = requests.post(
            "http://admin:admin@localhost:3000/api/dashboards/db",
            json=dashboard_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard importado correctamente: {result['url']}")
            return True
        else:
            print(f"❌ Error importando dashboard: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importando dashboard: {e}")
        return False

def verify_metrics():
    """Verificar que las métricas estén funcionando"""
    print("🔍 Verificando métricas...")
    
    try:
        # Verificar CPU
        cpu_response = requests.get(
            "http://localhost:9090/api/v1/query?query=100%20-%20(avg(irate(windows_cpu_time_total%7Bmode%3D%22idle%22%2Cjob%3D%22windows_local%22%7D%5B5m%5D))%20*%20100)",
            timeout=10
        )
        
        if cpu_response.status_code == 200:
            cpu_data = cpu_response.json()
            if cpu_data['data']['result']:
                cpu_value = float(cpu_data['data']['result'][0]['value'][1])
                print(f"✅ CPU Usage: {cpu_value:.2f}%")
            else:
                print("⚠️  No hay datos de CPU disponibles")
        
        # Verificar memoria
        memory_response = requests.get(
            "http://localhost:9090/api/v1/query?query=windows_memory_available_bytes%7Bjob%3D%22windows_local%22%7D%20%2F%201024%20%2F%201024%20%2F%201024",
            timeout=10
        )
        
        if memory_response.status_code == 200:
            memory_data = memory_response.json()
            if memory_data['data']['result']:
                memory_value = float(memory_data['data']['result'][0]['value'][1])
                print(f"✅ Memoria disponible: {memory_value:.2f} GB")
            else:
                print("⚠️  No hay datos de memoria disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando métricas: {e}")
        return False

def open_dashboard():
    """Abrir el dashboard en el navegador"""
    dashboard_url = "http://localhost:3000/d/optimon-windows-corrected/optimon-windows-local-monitoring-corrected?orgId=1&refresh=30s"
    print(f"🌐 Abriendo dashboard: {dashboard_url}")
    
    try:
        import webbrowser
        webbrowser.open(dashboard_url)
        print("✅ Dashboard abierto en el navegador")
    except Exception as e:
        print(f"⚠️  No se pudo abrir automáticamente: {e}")
        print(f"📋 URL manual: {dashboard_url}")

def main():
    print("=" * 60)
    print("🔧 OptiMon - Sistema de Monitoreo Corregido")
    print("=" * 60)
    
    # Paso 1: Iniciar servicios
    if not start_services():
        sys.exit(1)
    
    # Paso 2: Esperar a Grafana
    if not wait_for_grafana():
        sys.exit(1)
    
    # Paso 3: Importar dashboard
    if not import_dashboard():
        print("⚠️  Continuando sin importar dashboard...")
    
    # Dar tiempo para que las métricas se estabilicen
    print("⏳ Esperando estabilización de métricas...")
    time.sleep(15)
    
    # Paso 4: Verificar métricas
    verify_metrics()
    
    # Paso 5: Abrir dashboard
    open_dashboard()
    
    print("\n" + "=" * 60)
    print("✅ Sistema OptiMon iniciado correctamente")
    print("🌐 Grafana: http://localhost:3000")
    print("📊 Prometheus: http://localhost:9090")
    print("🔧 Portal: http://localhost:5000")
    print("📋 Usuario: admin / Contraseña: admin")
    print("=" * 60)

if __name__ == "__main__":
    main()