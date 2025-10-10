#!/usr/bin/env python3
"""
🎯 OPTIMON - SISTEMA DE INICIO INTELIGENTE Y COMPLETO
=====================================================

Este script inicia todo el ecosistema OptiMon de forma inteligente,
incluyendo la ejecución en segundo plano de todos los servicios.

Funcionalidades:
- ✅ Verificación de dependencias
- ✅ Inicio de servicios Docker
- ✅ SMTP Service en segundo plano  
- ✅ Dashboard web en segundo plano
- ✅ Windows Exporter automático
- ✅ Verificación de puertos
- ✅ Validación del sistema completo

Autor: OptiMon Team
Versión: 2.0 (Sistema Completo)
Fecha: Octubre 2025
"""

import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path

class OptiMonManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.required_ports = {
            3000: "Grafana",
            5000: "OptiMon Dashboard", 
            5555: "SMTP Service",
            9090: "Prometheus",
            9093: "AlertManager",
            9182: "Windows Exporter"
        }
        self.services_status = {}
        
    def log(self, message, level="INFO"):
        """Log con timestamp y formato"""
        timestamp = time.strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
    
    def run_command(self, command, shell=True, capture_output=True, background=False):
        """Ejecutar comandos con manejo de errores"""
        try:
            if background:
                # Para Windows, usar subprocess.Popen para procesos en segundo plano
                process = subprocess.Popen(
                    command,
                    shell=shell,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=self.base_dir
                )
                return True, f"Process started with PID {process.pid}"
            else:
                result = subprocess.run(
                    command,
                    shell=shell,
                    capture_output=capture_output,
                    text=True,
                    cwd=self.base_dir,
                    timeout=30
                )
                return result.returncode == 0, result.stdout if capture_output else "OK"
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def check_port(self, port):
        """Verificar si un puerto está en uso"""
        success, output = self.run_command(f"netstat -ano | findstr :{port}")
        return success and str(port) in output
    
    def start_docker_services(self):
        """Iniciar servicios Docker"""
        self.log("Iniciando servicios Docker...")
        
        # Verificar Docker
        success, _ = self.run_command("docker --version")
        if not success:
            self.log("Docker no está disponible", "ERROR")
            return False
            
        # Iniciar servicios
        success, output = self.run_command("docker-compose up -d")
        if success:
            self.log("Servicios Docker iniciados correctamente", "SUCCESS")
            time.sleep(10)  # Dar tiempo para que se inicien
            return True
        else:
            self.log(f"Error iniciando Docker: {output}", "ERROR")
            return False
    
    def start_smtp_service(self):
        """Iniciar SMTP Service en segundo plano"""
        self.log("Iniciando SMTP Service...")
        
        if self.check_port(5555):
            self.log("SMTP Service ya está ejecutándose", "SUCCESS")
            return True
            
        success, output = self.run_command(
            "python optimon_smtp_service.py",
            background=True
        )
        
        if success:
            time.sleep(3)
            if self.check_port(5555):
                self.log("SMTP Service iniciado correctamente", "SUCCESS")
                return True
        
        self.log("Error iniciando SMTP Service", "ERROR")
        return False
    
    def start_dashboard(self):
        """Iniciar Dashboard en segundo plano"""
        self.log("Iniciando OptiMon Dashboard...")
        
        if self.check_port(5000):
            self.log("Dashboard ya está ejecutándose", "SUCCESS")
            return True
            
        success, output = self.run_command(
            "python optimon_dashboard.py --no-debug",
            background=True
        )
        
        if success:
            time.sleep(5)
            if self.check_port(5000):
                self.log("Dashboard iniciado correctamente", "SUCCESS")
                return True
        
        self.log("Error iniciando Dashboard", "ERROR")
        return False
    
    def verify_system_health(self):
        """Verificación completa del sistema"""
        self.log("Verificando estado del sistema...")
        
        # Verificar puertos
        port_status = {}
        for port, service in self.required_ports.items():
            is_running = self.check_port(port)
            port_status[port] = is_running
            status = "✅" if is_running else "❌"
            self.log(f"  {service} (:{port}): {status}")
        
        # Verificar APIs
        try:
            # Dashboard API
            response = requests.get("http://localhost:5000/api/local/windows-exporter/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"  Windows Exporter: ✅ ({data.get('metrics_count', 0)} métricas)")
            else:
                self.log("  Windows Exporter API: ❌", "ERROR")
        except:
            self.log("  Windows Exporter API: ❌", "ERROR")
        
        try:
            # Prometheus
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
            if response.status_code == 200:
                targets = response.json().get('data', {}).get('activeTargets', [])
                active_targets = len([t for t in targets if t.get('health') == 'up'])
                self.log(f"  Prometheus targets: ✅ ({active_targets} activos)")
            else:
                self.log("  Prometheus: ❌", "ERROR")
        except:
            self.log("  Prometheus: ❌", "ERROR")
        
        # Calcular éxito general
        active_ports = sum(1 for status in port_status.values() if status)
        total_ports = len(port_status)
        success_rate = (active_ports / total_ports) * 100
        
        return success_rate, port_status
    
    def show_system_info(self):
        """Mostrar información del sistema"""
        self.log("=" * 60)
        self.log("🚀 OPTIMON - SISTEMA DE MONITOREO COMPLETO")
        self.log("=" * 60)
        self.log("🌐 Interfaces disponibles:")
        self.log("  • Dashboard OptiMon: http://localhost:5000")
        self.log("  • Grafana: http://localhost:3000 (admin/admin)")
        self.log("  • Prometheus: http://localhost:9090")
        self.log("  • AlertManager: http://localhost:9093")
        self.log("  • Windows Exporter: http://localhost:9182/metrics")
        self.log("📧 SMTP Service: puerto 5555 (interno)")
        self.log("=" * 60)
    
    def start_complete_system(self):
        """Iniciar sistema completo"""
        self.log("🚀 INICIANDO OPTIMON - SISTEMA COMPLETO")
        self.log("=" * 60)
        
        steps = [
            ("Docker Services", self.start_docker_services),
            ("SMTP Service", self.start_smtp_service), 
            ("OptiMon Dashboard", self.start_dashboard)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            self.log(f"Ejecutando: {step_name}")
            if step_func():
                success_count += 1
            else:
                self.log(f"Falló: {step_name}", "ERROR")
        
        # Verificación final
        time.sleep(5)
        success_rate, port_status = self.verify_system_health()
        
        self.log("=" * 60)
        if success_rate >= 90:
            self.log(f"🎉 SISTEMA INICIADO EXITOSAMENTE ({success_rate:.1f}%)", "SUCCESS")
            self.show_system_info()
            return True
        else:
            self.log(f"⚠️ SISTEMA PARCIALMENTE INICIADO ({success_rate:.1f}%)", "WARNING")
            return False

def main():
    """Función principal"""
    manager = OptiMonManager()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                     🎯 OPTIMON v2.0                         ║
║              Sistema de Monitoreo Completo                  ║
║                                                              ║
║  ✅ Docker Services (Prometheus, Grafana, AlertManager)     ║
║  ✅ SMTP Service (puerto 5555)                              ║
║  ✅ Web Dashboard (puerto 5000)                             ║
║  ✅ Windows Exporter (puerto 9182)                          ║
║  ✅ Ejecución en segundo plano                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        success = manager.start_complete_system()
        if success:
            manager.log("🎉 Todos los servicios están ejecutándose en segundo plano", "SUCCESS")
            manager.log("💡 Tip: Usa 'netstat -ano | findstr :puerto' para ver procesos", "INFO")
            return 0
        else:
            manager.log("❌ Algunos servicios fallaron al iniciarse", "ERROR")
            return 1
    except KeyboardInterrupt:
        manager.log("⏹️ Proceso interrumpido por el usuario", "WARNING")
        return 130
    except Exception as e:
        manager.log(f"❌ Error crítico: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    exit(main())