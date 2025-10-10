#!/usr/bin/env python3
"""
Prueba completa de la funcionalidad de instalación de Windows Exporter
Incluye todos los casos posibles y verificación de estado
"""

import requests
import json
import time

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_windows_exporter_status():
    """Probar endpoint de estado"""
    log("🔍 PROBANDO ESTADO DE WINDOWS EXPORTER")
    log("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000/api/local/windows-exporter/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Estado obtenido exitosamente:")
            log(f"   - Ejecutándose: {'✅' if data.get('running') else '❌'}")
            log(f"   - Puerto: {data.get('port', 'N/A')}")
            log(f"   - Métricas: {data.get('metrics_count', 0)}")
            log(f"   - Versión: {data.get('version', 'unknown')}")
            log(f"   - Instalado: {'✅' if data.get('installed') else '❌'}")
            log(f"   - Ruta: {data.get('installation_path', 'N/A')}")
            return data
        else:
            log(f"❌ Error obteniendo estado: HTTP {response.status_code}")
            return None
    except Exception as e:
        log(f"❌ Error de conexión: {e}")
        return None

def test_installation_api():
    """Probar API de instalación"""
    log("\n🚀 PROBANDO API DE INSTALACIÓN")
    log("=" * 60)
    
    try:
        log("Enviando solicitud de instalación...")
        response = requests.post("http://localhost:5000/api/local/install-node-exporter", timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            message = data.get('message', '')
            details = data.get('details', {})
            
            if success:
                log(f"✅ Instalación exitosa: {message}")
                log(f"   Estado: {details.get('status', 'unknown')}")
                if 'port' in details:
                    log(f"   Puerto: {details['port']}")
                if 'metrics_url' in details:
                    log(f"   Métricas: {details['metrics_url']}")
                if 'path' in details:
                    log(f"   Ruta: {details['path']}")
            else:
                log(f"⚠️ Resultado: {message}")
                log(f"   Estado: {details.get('status', 'unknown')}")
                if 'suggestion' in details:
                    log(f"   Sugerencia: {details['suggestion']}")
            
            return data
        else:
            log(f"❌ Error HTTP: {response.status_code}")
            try:
                error_data = response.json()
                log(f"   Mensaje: {error_data.get('message', 'Sin mensaje')}")
            except:
                log(f"   Respuesta: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        log("❌ Timeout en la instalación (>120s)")
        return None
    except Exception as e:
        log(f"❌ Error de conexión: {e}")
        return None

def verify_metrics_endpoint():
    """Verificar que las métricas están disponibles"""
    log("\n📊 VERIFICANDO MÉTRICAS")
    log("=" * 60)
    
    try:
        response = requests.get("http://localhost:9182/metrics", timeout=10)
        if response.status_code == 200:
            lines = response.text.split('\n')
            total_metrics = len([line for line in lines if line and not line.startswith('#')])
            windows_metrics = len([line for line in lines if 'windows_' in line and not line.startswith('#')])
            
            log(f"✅ Métricas disponibles:")
            log(f"   - Total: {total_metrics}")
            log(f"   - Windows específicas: {windows_metrics}")
            
            # Mostrar algunas métricas de ejemplo
            log(f"   - Ejemplos:")
            windows_lines = [line for line in lines[:50] if 'windows_' in line and not line.startswith('#')]
            for i, line in enumerate(windows_lines[:3]):
                log(f"     {line}")
            
            return True
        else:
            log(f"❌ Error accediendo a métricas: HTTP {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error accediendo a métricas: {e}")
        return False

def verify_prometheus_integration():
    """Verificar integración con Prometheus"""
    log("\n🎯 VERIFICANDO INTEGRACIÓN PROMETHEUS")
    log("=" * 60)
    
    try:
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            targets = data.get('data', {}).get('activeTargets', [])
            
            # Buscar target de Windows Exporter
            windows_targets = [t for t in targets if '9182' in t.get('scrapeUrl', '')]
            
            if windows_targets:
                target = windows_targets[0]
                health = target.get('health', 'unknown')
                last_scrape = target.get('lastScrape', 'N/A')
                
                log(f"✅ Target encontrado:")
                log(f"   - Estado: {health}")
                log(f"   - URL: {target.get('scrapeUrl', 'N/A')}")
                log(f"   - Último scrape: {last_scrape}")
                log(f"   - Duración scrape: {target.get('lastScrapeDuration', 'N/A')}")
                
                return health == 'up'
            else:
                log(f"❌ Target de Windows Exporter no encontrado en Prometheus")
                log(f"   Total targets: {len(targets)}")
                return False
        else:
            log(f"❌ Error consultando Prometheus: HTTP {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error consultando Prometheus: {e}")
        return False

def main():
    log("🧪 PRUEBA COMPLETA - WINDOWS EXPORTER E INSTALACIÓN")
    log("=" * 80)
    
    # 1. Verificar estado actual
    current_status = test_windows_exporter_status()
    
    # 2. Probar API de instalación
    install_result = test_installation_api()
    
    # 3. Verificar métricas después de la instalación
    time.sleep(3)  # Dar tiempo para que se inicie
    metrics_ok = verify_metrics_endpoint()
    
    # 4. Verificar integración con Prometheus
    time.sleep(5)  # Dar tiempo para que Prometheus haga scrape
    prometheus_ok = verify_prometheus_integration()
    
    # 5. Verificar estado final
    log("\n🔍 ESTADO FINAL")
    log("=" * 60)
    final_status = test_windows_exporter_status()
    
    # Resumen
    log("\n" + "=" * 80)
    log("📋 RESUMEN DE PRUEBAS")
    log("=" * 80)
    
    tests = [
        ("Estado inicial", current_status is not None),
        ("API de instalación", install_result is not None and install_result.get('success', False)),
        ("Métricas disponibles", metrics_ok),
        ("Integración Prometheus", prometheus_ok),
        ("Estado final", final_status is not None and final_status.get('running', False))
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"  {test_name}: {status}")
    
    percentage = (passed / total) * 100
    log(f"\n🏆 RESULTADO: {passed}/{total} pruebas exitosas ({percentage:.1f}%)")
    
    if percentage >= 90:
        log("🎉 EXCELENTE - Instalación y funcionalidad perfectas")
        return True
    elif percentage >= 75:
        log("✅ BUENO - Sistema funcionando bien")
        return True
    else:
        log("⚠️ NECESITA ATENCIÓN - Algunos problemas detectados")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)