#!/usr/bin/env python3
"""
OptiMon - Setup Automático Completo
Configura todo el sistema de monitoreo automáticamente
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path

def print_step(message, step_type="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m"
    }
    reset = "\033[0m"
    icon = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️", 
        "ERROR": "❌",
        "HEADER": "🚀"
    }
    print(f"{colors.get(step_type, '')}{icon.get(step_type, '')} {message}{reset}")

def run_command(command, description, cwd=None, shell=True, background=False):
    """Ejecutar comando con manejo de errores"""
    print_step(f"Ejecutando: {description}")
    
    try:
        if background:
            # Para procesos en segundo plano
            process = subprocess.Popen(
                command,
                shell=shell,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            print_step(f"Proceso iniciado en segundo plano (PID: {process.pid})", "SUCCESS")
            return True, process
        else:
            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print_step(f"✓ {description} completado", "SUCCESS")
                return True, result.stdout
            else:
                print_step(f"✗ Error en {description}: {result.stderr}", "ERROR")
                return False, result.stderr
                
    except subprocess.TimeoutExpired:
        print_step(f"✗ Timeout en {description}", "ERROR")
        return False, "Timeout"
    except Exception as e:
        print_step(f"✗ Excepción en {description}: {e}", "ERROR")
        return False, str(e)

def check_port(host, port, timeout=5):
    """Verificar si un puerto está disponible"""
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def wait_for_service(url, max_attempts=30, delay=2):
    """Esperar a que un servicio esté disponible"""
    print_step(f"Esperando servicio en {url}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_step(f"Servicio disponible en {url}", "SUCCESS")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    print_step(f"Servicio no disponible en {url} después de {max_attempts} intentos", "WARNING")
    return False

def setup_docker_services():
    """Configurar servicios Docker"""
    print_step("Configurando servicios Docker...", "HEADER")
    
    # Verificar Docker
    success, _ = run_command("docker --version", "Verificar Docker")
    if not success:
        print_step("Docker no está disponible", "ERROR")
        return False
    
    # Detener servicios existentes
    run_command("docker compose down", "Detener servicios Docker existentes")
    time.sleep(3)
    
    # Iniciar servicios
    success, _ = run_command("docker compose up -d", "Iniciar servicios Docker")
    if not success:
        return False
    
    # Esperar servicios
    time.sleep(15)
    
    # Verificar servicios
    services = [
        ("http://localhost:9090", "Prometheus"),
        ("http://localhost:3000", "Grafana"),
        ("http://localhost:9093", "AlertManager")
    ]
    
    for url, name in services:
        if wait_for_service(url, max_attempts=15):
            print_step(f"{name} iniciado correctamente", "SUCCESS")
        else:
            print_step(f"Error iniciando {name}", "ERROR")
            return False
    
    return True

def setup_optimon_portal():
    """Configurar portal OptiMon"""
    print_step("Configurando portal OptiMon...", "HEADER")
    
    # Detener procesos Python existentes
    run_command("taskkill /f /im python.exe", "Detener procesos Python existentes")
    time.sleep(2)
    
    # Iniciar OptiMon en segundo plano usando PowerShell Job
    powershell_cmd = '''Start-Job -ScriptBlock { 
        cd "C:\\Users\\oagr2\\Documents\\GitHub\\PROYECTO_TESIS\\OptiMon-BASE-UNIFICADO"
        python app.py 
    } -Name "OptiMonServer"'''
    
    success, process = run_command(
        ["powershell", "-Command", powershell_cmd],
        "Iniciar servidor OptiMon",
        shell=False
    )
    
    if not success:
        print_step("Error iniciando servidor OptiMon", "ERROR")
        return False
    
    # Esperar a que el servidor inicie
    if wait_for_service("http://localhost:5000/api/health", max_attempts=20):
        print_step("Portal OptiMon iniciado correctamente", "SUCCESS")
        return True
    else:
        print_step("Error: Portal OptiMon no responde", "ERROR")
        return False

def setup_windows_exporter():
    """Configurar Windows Exporter automáticamente"""
    print_step("Configurando Windows Exporter...", "HEADER")
    
    # Eliminar instalaciones existentes
    run_command("taskkill /f /im windows_exporter.exe", "Detener Windows Exporter existente")
    time.sleep(2)
    
    # Llamar al endpoint de configuración automática
    try:
        print_step("Ejecutando configuración automática...")
        response = requests.post("http://localhost:5000/api/local/setup", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print_step("Configuración automática completada", "SUCCESS")
            
            # Mostrar resultados
            for step in result.get('steps', []):
                status = "SUCCESS" if step['success'] else "ERROR"
                print_step(f"  {step['step']}: {step['message']}", status)
            
            return result['success']
        else:
            print_step(f"Error en configuración automática: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_step(f"Error ejecutando configuración automática: {e}", "ERROR")
        return False

def verify_complete_system():
    """Verificar que todo el sistema esté funcionando"""
    print_step("Verificando sistema completo...", "HEADER")
    
    # Verificar servicios
    services_check = [
        ("http://localhost:5000/api/health", "OptiMon Portal"),
        ("http://localhost:9090/api/v1/targets", "Prometheus"),
        ("http://localhost:3000", "Grafana"),
        ("http://localhost:9182/metrics", "Windows Exporter")
    ]
    
    all_ok = True
    for url, service in services_check:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print_step(f"{service}: ✓ Funcionando", "SUCCESS")
            else:
                print_step(f"{service}: ✗ Error {response.status_code}", "ERROR")
                all_ok = False
        except Exception as e:
            print_step(f"{service}: ✗ No disponible ({e})", "ERROR")
            all_ok = False
    
    # Verificar targets de Prometheus
    try:
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
        if response.status_code == 200:
            targets = response.json()['data']['activeTargets']
            windows_target = next((t for t in targets if t['labels']['job'] == 'windows_local'), None)
            
            if windows_target and windows_target['health'] == 'up':
                print_step("Target Windows Exporter: ✓ UP y recolectando métricas", "SUCCESS")
            else:
                print_step("Target Windows Exporter: ✗ No disponible o DOWN", "ERROR")
                all_ok = False
    except:
        print_step("No se pudo verificar targets de Prometheus", "ERROR")
        all_ok = False
    
    return all_ok

def main():
    """Función principal de configuración automática"""
    print_step("OPTIMON - CONFIGURACIÓN AUTOMÁTICA COMPLETA", "HEADER")
    print_step("Iniciando configuración automática del sistema de monitoreo...", "INFO")
    
    # Cambiar al directorio correcto
    os.chdir(Path(__file__).parent)
    
    steps = [
        ("Servicios Docker", setup_docker_services),
        ("Portal OptiMon", setup_optimon_portal), 
        ("Windows Exporter", setup_windows_exporter),
        ("Verificación del Sistema", verify_complete_system)
    ]
    
    for step_name, step_function in steps:
        print_step(f"\n{'='*50}")
        print_step(f"PASO: {step_name}", "HEADER")
        print_step(f"{'='*50}")
        
        if not step_function():
            print_step(f"✗ Error en paso: {step_name}", "ERROR")
            print_step("Configuración automática fallida", "ERROR")
            return False
        
        print_step(f"✓ Paso completado: {step_name}", "SUCCESS")
    
    # Resumen final
    print_step(f"\n{'='*60}")
    print_step("🎉 CONFIGURACIÓN AUTOMÁTICA COMPLETADA EXITOSAMENTE", "SUCCESS")
    print_step(f"{'='*60}")
    
    print_step("\n📊 ACCESOS AL SISTEMA:")
    print_step("  • Portal OptiMon:     http://localhost:5000")
    print_step("  • Grafana:           http://localhost:3000 (admin/admin)")
    print_step("  • Prometheus:        http://localhost:9090")
    print_step("  • Windows Exporter:  http://localhost:9182/metrics")
    
    print_step("\n✅ Sistema de monitoreo completamente operativo")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_step("\nConfiguración cancelada por el usuario", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_step(f"Error inesperado: {e}", "ERROR")
        sys.exit(1)