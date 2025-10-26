#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys

print("=== VERIFICACION FINAL DE ERRORES ===")
print()

services = [
    ("OptiMon Health", "http://localhost:5000/api/health"),
    ("OptiMon Metrics", "http://localhost:5000/api/metrics"),
    ("OptiMon Local Status", "http://localhost:5000/api/local/status"),
    ("Prometheus", "http://localhost:9090/-/healthy"),
    ("Grafana", "http://localhost:3000/api/health"),
    ("AlertManager", "http://localhost:9093/-/healthy"),
    ("Windows Exporter", "http://localhost:9182/metrics")
]

errors_found = []
successful_checks = 0

for name, url in services:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name}")
            successful_checks += 1
            
            if "health" in url and "optimon" in name.lower():
                try:
                    data = response.json()
                    print(f"     Status: {data.get('status', 'unknown')}")
                    components = data.get('components', {})
                    for comp, status in components.items():
                        status_text = "OK" if status else "FAIL"
                        print(f"     {comp}: {status_text}")
                except:
                    pass
        else:
            print(f"[WARNING] {name}: Status {response.status_code}")
            errors_found.append(f"{name} returned {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)}")
        errors_found.append(f"{name}: {str(e)}")

print()
print("=== RESUMEN FINAL ===")
print(f"Servicios funcionando: {successful_checks}/{len(services)}")

if errors_found:
    print("ERRORES ENCONTRADOS:")
    for error in errors_found:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("TODOS LOS SERVICIOS FUNCIONANDO CORRECTAMENTE!")
    print()
    print("Enlaces disponibles:")
    print("  - Portal: http://localhost:5000")
    print("  - Grafana: http://localhost:3000")
    print("  - Prometheus: http://localhost:9090")
    print("  - AlertManager: http://localhost:9093")
    sys.exit(0)