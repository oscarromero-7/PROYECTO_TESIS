#!/usr/bin/env python3
"""
Reporte final de estado de OptiMon
Verificación completa de todas las funcionalidades
"""

import requests
import json
import time
import psutil

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_all_endpoints():
    """Probar todos los endpoints del dashboard"""
    log("🌐 PROBANDO ENDPOINTS DEL DASHBOARD")
    log("=" * 60)
    
    endpoints = [
        ("Dashboard principal", "http://localhost:5000", "GET"),
        ("Estado de monitoreo", "http://localhost:5000/api/monitoring/status", "GET"),
        ("Estado del sistema", "http://localhost:5000/api/system-status", "GET"),
        ("Health check SMTP", "http://localhost:5555/health", "GET"),
        ("Métricas Windows Exporter", "http://localhost:9182/metrics", "GET"),
        ("Targets Prometheus", "http://localhost:9090/api/v1/targets", "GET"),
        ("API Grafana", "http://localhost:3000/api/health", "GET"),
        ("API AlertManager", "http://localhost:9093/api/v1/status", "GET")
    ]
    
    results = {}
    
    for name, url, method in endpoints:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ HTTP {response.status_code}"
            results[name] = {
                "status": response.status_code == 200,
                "code": response.status_code,
                "url": url
            }
            log(f"  {name}: {status}")
        except Exception as e:
            results[name] = {
                "status": False,
                "error": str(e),
                "url": url
            }
            log(f"  {name}: ❌ Error - {e}")
    
    return results

def test_system_metrics():
    """Probar métricas del sistema"""
    log("\n📊 PROBANDO MÉTRICAS DEL SISTEMA")
    log("=" * 60)
    
    try:
        # Métricas locales
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        
        log(f"  CPU: {cpu}%")
        log(f"  Memoria: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)")
        log(f"  Disco: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)")
        
        # Verificar Windows Exporter métricas
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=5)
            if response.status_code == 200:
                metrics_lines = response.text.split('\n')
                total_metrics = len([line for line in metrics_lines if line and not line.startswith('#')])
                windows_metrics = len([line for line in metrics_lines if 'windows_' in line and not line.startswith('#')])
                log(f"  Windows Exporter: {total_metrics} métricas totales, {windows_metrics} específicas de Windows")
                return True
            else:
                log(f"  ❌ Error accediendo a métricas: HTTP {response.status_code}")
                return False
        except Exception as e:
            log(f"  ❌ Error accediendo a métricas: {e}")
            return False
            
    except Exception as e:
        log(f"  ❌ Error obteniendo métricas del sistema: {e}")
        return False

def test_prometheus_integration():
    """Probar integración con Prometheus"""
    log("\n🎯 PROBANDO INTEGRACIÓN PROMETHEUS")
    log("=" * 60)
    
    try:
        # Obtener targets
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            targets = data.get('data', {}).get('activeTargets', [])
            
            total_targets = len(targets)
            up_targets = len([t for t in targets if t.get('health') == 'up'])
            
            log(f"  Total targets: {total_targets}")
            log(f"  Targets activos: {up_targets}")
            
            # Buscar Windows Exporter específicamente
            windows_targets = [t for t in targets if '9182' in t.get('scrapeUrl', '')]
            if windows_targets:
                target = windows_targets[0]
                log(f"  Windows Exporter: {target.get('health', 'unknown')}")
                log(f"  URL: {target.get('scrapeUrl', 'N/A')}")
                return target.get('health') == 'up'
            else:
                log(f"  ❌ Windows Exporter no encontrado en targets")
                return False
        else:
            log(f"  ❌ Error consultando Prometheus: HTTP {response.status_code}")
            return False
    except Exception as e:
        log(f"  ❌ Error consultando Prometheus: {e}")
        return False

def verify_ports():
    """Verificar que todos los puertos estén activos"""
    log("\n🔌 VERIFICANDO PUERTOS")
    log("=" * 60)
    
    expected_ports = {
        3000: "Grafana",
        5000: "OptiMon Dashboard", 
        5555: "SMTP Service",
        9090: "Prometheus",
        9093: "AlertManager",
        9182: "Windows Exporter"
    }
    
    active_ports = {}
    for conn in psutil.net_connections():
        if conn.laddr.port in expected_ports:
            active_ports[conn.laddr.port] = conn.pid
    
    results = {}
    for port, service in expected_ports.items():
        if port in active_ports:
            log(f"  ✅ {service}: Puerto {port} activo (PID: {active_ports[port]})")
            results[service] = True
        else:
            log(f"  ❌ {service}: Puerto {port} inactivo")
            results[service] = False
    
    return results

def generate_final_report():
    """Generar reporte final"""
    log("\n🚀 GENERANDO REPORTE FINAL DE OPTIMON")
    log("=" * 80)
    
    # Ejecutar todas las pruebas
    endpoint_results = test_all_endpoints()
    metrics_ok = test_system_metrics()
    prometheus_ok = test_prometheus_integration()
    port_results = verify_ports()
    
    # Calcular estadísticas
    total_endpoints = len(endpoint_results)
    working_endpoints = sum(1 for r in endpoint_results.values() if r.get('status', False))
    
    total_ports = len(port_results)
    active_ports = sum(1 for r in port_results.values() if r)
    
    # Generar reporte
    log("\n" + "=" * 80)
    log("📋 REPORTE FINAL - OPTIMON SISTEMA DE MONITOREO")
    log("=" * 80)
    
    log(f"🌐 Endpoints del dashboard: {working_endpoints}/{total_endpoints} funcionando ({working_endpoints/total_endpoints*100:.1f}%)")
    log(f"🔌 Puertos de servicios: {active_ports}/{total_ports} activos ({active_ports/total_ports*100:.1f}%)")
    log(f"📊 Métricas del sistema: {'✅ Funcionando' if metrics_ok else '❌ Error'}")
    log(f"🎯 Integración Prometheus: {'✅ Funcionando' if prometheus_ok else '❌ Error'}")
    
    # Calcular score final
    scores = [
        working_endpoints/total_endpoints,
        active_ports/total_ports,
        1 if metrics_ok else 0,
        1 if prometheus_ok else 0
    ]
    final_score = sum(scores) / len(scores) * 100
    
    log(f"\n🏆 PUNTUACIÓN FINAL: {final_score:.1f}%")
    
    if final_score >= 90:
        log("🎉 EXCELENTE - Sistema completamente operativo")
        status = "EXCELENTE"
    elif final_score >= 75:
        log("✅ BUENO - Sistema mayormente funcional")
        status = "BUENO"
    elif final_score >= 50:
        log("⚠️ ACEPTABLE - Sistema funcionando con algunos problemas")
        status = "ACEPTABLE"
    else:
        log("❌ CRÍTICO - Sistema con problemas graves")
        status = "CRÍTICO"
    
    # Guardar reporte JSON
    final_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "final_score": final_score,
        "status": status,
        "endpoints": endpoint_results,
        "ports": port_results,
        "metrics_working": metrics_ok,
        "prometheus_integration": prometheus_ok,
        "summary": {
            "endpoints_working": f"{working_endpoints}/{total_endpoints}",
            "ports_active": f"{active_ports}/{total_ports}",
            "overall_health": status
        }
    }
    
    with open('optimon_final_report.json', 'w') as f:
        json.dump(final_report, f, indent=2)
    
    log(f"\n📄 Reporte completo guardado en: optimon_final_report.json")
    return final_score >= 75

if __name__ == "__main__":
    success = generate_final_report()
    exit(0 if success else 1)