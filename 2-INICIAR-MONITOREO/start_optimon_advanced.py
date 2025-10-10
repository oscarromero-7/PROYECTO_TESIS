#!/usr/bin/env python3
"""
Script para iniciar OptiMon Dashboard en segundo plano
Incluye manejo mejorado de contenedores y verificación de servicios
"""

import subprocess
import time
import sys
import os
import psutil
import json
import requests
from pathlib import Path

def log(message):
    """Imprimir mensaje con timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_port_in_use(port):
    """Verificar si un puerto está en uso"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True, conn.pid
    return False, None

def kill_process_on_port(port):
    """Terminar proceso que usa un puerto específico"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.pid:
            try:
                process = psutil.Process(conn.pid)
                log(f"🔥 Terminando proceso {conn.pid} en puerto {port}")
                process.terminate()
                time.sleep(2)
                if process.is_running():
                    process.kill()
                return True
            except:
                pass
    return False

def verify_docker_services():
    """Verificar y gestionar servicios Docker"""
    log("🐳 Verificando servicios Docker...")
    
    try:
        # Verificar si Docker está corriendo
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            log("❌ Docker no está corriendo")
            return False
        
        # Verificar docker-compose
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, cwd='.')
        
        # Si hay servicios corriendo, verificar su estado
        services = ['prometheus', 'grafana', 'alertmanager']
        running_services = []
        
        for service in services:
            if service in result.stdout:
                running_services.append(service)
        
        if len(running_services) == len(services):
            log(f"✅ Servicios Docker activos: {', '.join(running_services)}")
            return True
        else:
            log(f"⚠️ Algunos servicios Docker faltantes. Reiniciando...")
            # Reiniciar servicios
            subprocess.run(['docker-compose', 'down'], capture_output=True)
            time.sleep(3)
            subprocess.run(['docker-compose', 'up', '-d'], capture_output=True)
            time.sleep(10)
            return True
            
    except Exception as e:
        log(f"❌ Error verificando Docker: {e}")
        return False

def start_smtp_service():
    """Iniciar servicio SMTP en segundo plano"""
    log("📧 Verificando servicio SMTP...")
    
    # Verificar si ya está corriendo
    port_used, pid = check_port_in_use(5555)
    if port_used:
        log(f"✅ SMTP ya está corriendo en puerto 5555 (PID: {pid})")
        return True
    
    try:
        # Verificar que el archivo existe
        smtp_file = Path('optimon_smtp_service.py')
        if not smtp_file.exists():
            log(f"❌ Archivo no encontrado: {smtp_file.absolute()}")
            return False
        
        # Iniciar SMTP service
        log("🚀 Iniciando servicio SMTP...")
        process = subprocess.Popen(
            [sys.executable, str(smtp_file)],
            cwd=str(Path.cwd()),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Esperar un momento y verificar
        time.sleep(5)
        port_used, pid = check_port_in_use(5555)
        if port_used:
            log(f"✅ SMTP iniciado correctamente (PID: {pid})")
            return True
        else:
            log("❌ Error: SMTP no pudo iniciarse")
            return False
            
    except Exception as e:
        log(f"❌ Error iniciando SMTP: {e}")
        return False

def start_windows_exporter():
    """Iniciar Windows Exporter si está instalado"""
    log("📊 Verificando Windows Exporter...")
    
    # Verificar si ya está corriendo
    port_used, pid = check_port_in_use(9182)
    if port_used:
        log(f"✅ Windows Exporter ya está corriendo en puerto 9182 (PID: {pid})")
        return True
    
    # Buscar Windows Exporter instalado
    possible_paths = [
        'windows_exporter/windows_exporter.exe',
        'C:/optimon/windows_exporter/windows_exporter.exe'
    ]
    
    for exe_path in possible_paths:
        if os.path.exists(exe_path):
            try:
                log("🚀 Iniciando Windows Exporter...")
                process = subprocess.Popen(
                    [exe_path, '--web.listen-address=:9182'],
                    cwd='.',
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                time.sleep(3)
                port_used, pid = check_port_in_use(9182)
                if port_used:
                    log(f"✅ Windows Exporter iniciado (PID: {pid})")
                    return True
                    
            except Exception as e:
                log(f"❌ Error iniciando Windows Exporter: {e}")
    
    log("⚠️ Windows Exporter no encontrado o no instalado")
    return False

def start_dashboard():
    """Iniciar dashboard en segundo plano"""
    log("🌐 Verificando Dashboard...")
    
    # Verificar si ya está corriendo
    port_used, pid = check_port_in_use(5000)
    if port_used:
        log(f"⚠️ Puerto 5000 ocupado por PID {pid}, terminando...")
        kill_process_on_port(5000)
        time.sleep(2)
    
    try:
        # Verificar que el archivo existe
        dashboard_file = Path('optimon_dashboard.py')
        if not dashboard_file.exists():
            log(f"❌ Archivo no encontrado: {dashboard_file.absolute()}")
            return False
        
        log("🚀 Iniciando Dashboard en segundo plano...")
        process = subprocess.Popen(
            [sys.executable, str(dashboard_file), '--background'],
            cwd=str(Path.cwd()),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Esperar y verificar
        time.sleep(8)
        port_used, pid = check_port_in_use(5000)
        if port_used:
            log(f"✅ Dashboard iniciado correctamente (PID: {pid})")
            log("🌐 Accesible en: http://localhost:5000")
            return True
        else:
            log("❌ Error: Dashboard no pudo iniciarse")
            return False
            
    except Exception as e:
        log(f"❌ Error iniciando Dashboard: {e}")
        return False

def verify_all_services():
    """Verificar que todos los servicios estén funcionando"""
    log("🔍 Verificación final de servicios...")
    
    services = {
        'Docker Prometheus': ('localhost', 9090),
        'Docker Grafana': ('localhost', 3000),
        'Docker AlertManager': ('localhost', 9093),
        'SMTP Service': ('localhost', 5555),
        'Dashboard': ('localhost', 5000),
        'Windows Exporter': ('localhost', 9182)
    }
    
    status = {}
    for service, (host, port) in services.items():
        port_used, pid = check_port_in_use(port)
        status[service] = {
            'running': port_used,
            'pid': pid,
            'port': port
        }
        
        if port_used:
            log(f"✅ {service}: ✅ (PID: {pid})")
        else:
            log(f"❌ {service}: ❌")
    
    # Crear archivo de estado
    with open('optimon_status.json', 'w') as f:
        json.dump(status, f, indent=2)
    
    return status

def main():
    log("🚀 INICIANDO OPTIMON - SISTEMA COMPLETO")
    log("=" * 60)
    
    # 1. Verificar Docker
    if not verify_docker_services():
        log("❌ Error crítico: Servicios Docker no disponibles")
        return False
    
    # 2. Iniciar SMTP
    start_smtp_service()
    
    # 3. Iniciar Windows Exporter
    start_windows_exporter()
    
    # 4. Iniciar Dashboard
    if not start_dashboard():
        log("❌ Error crítico: Dashboard no pudo iniciarse")
        return False
    
    # 5. Verificación final
    log("\n" + "=" * 60)
    status = verify_all_services()
    
    # Contar servicios activos
    active_services = sum(1 for s in status.values() if s['running'])
    total_services = len(status)
    
    log(f"\n📊 RESUMEN: {active_services}/{total_services} servicios activos")
    
    if active_services >= 4:  # Al menos Docker + SMTP + Dashboard
        log("🎉 OptiMon iniciado exitosamente!")
        log("🌐 Dashboard: http://localhost:5000")
        log("📈 Prometheus: http://localhost:9090")
        log("📊 Grafana: http://localhost:3000")
        return True
    else:
        log("⚠️ Algunos servicios no pudieron iniciarse")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)