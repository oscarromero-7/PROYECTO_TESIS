#!/usr/bin/env python3
"""
🚀 OPTIMON - INICIO RÁPIDO CON SERVICIOS EN SEGUNDO PLANO
========================================================

Script de inicio rápido que:
1. Inicia todos los servicios OptiMon en segundo plano
2. Verifica que estén funcionando correctamente  
3. Ejecuta pruebas completas si se solicita
4. Mantiene los servicios ejecutándose

Uso:
  python start_optimon_background.py            # Solo iniciar servicios
  python start_optimon_background.py --test     # Iniciar y probar
  python start_optimon_background.py --stop     # Detener servicios

Autor: OptiMon Team
Versión: 2.0
Fecha: Octubre 2025
"""

import subprocess
import time
import sys
import requests
import psutil
from pathlib import Path

class OptiMonQuickStart:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def log(self, message, level="INFO"):
        """Log con timestamp y formato"""
        timestamp = time.strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
    
    def is_port_in_use(self, port):
        """Verificar si un puerto está en uso"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return True
            return False
        except:
            return False
    
    def wait_for_service(self, name, port, url=None, timeout=60):
        """Esperar a que un servicio esté disponible"""
        self.log(f"Esperando a que {name} esté disponible...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Verificar puerto
            if self.is_port_in_use(port):
                if url:
                    try:
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            self.log(f"{name} está disponible en puerto {port}", "SUCCESS")
                            return True
                    except:
                        pass
                else:
                    self.log(f"{name} está disponible en puerto {port}", "SUCCESS")
                    return True
            
            time.sleep(2)
        
        self.log(f"Timeout esperando {name}", "WARNING")
        return False
    
    def start_services(self):
        """Iniciar todos los servicios en segundo plano"""
        self.log("🚀 INICIANDO SERVICIOS OPTIMON EN SEGUNDO PLANO")
        self.log("=" * 60)
        
        try:
            # Detener servicios existentes primero
            self.log("Deteniendo servicios existentes...")
            subprocess.run([
                sys.executable, "optimon_service_manager.py", "--stop"
            ], check=False, capture_output=True, cwd=self.base_dir)
            
            time.sleep(3)
            
            # Iniciar gestor de servicios en segundo plano
            self.log("Iniciando gestor de servicios...")
            
            # En Windows, usar CREATE_NEW_PROCESS_GROUP para proceso independiente
            if sys.platform == "win32":
                process = subprocess.Popen([
                    sys.executable, "optimon_service_manager.py", "--daemon"
                ], cwd=self.base_dir, 
                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
            else:
                process = subprocess.Popen([
                    sys.executable, "optimon_service_manager.py", "--daemon"
                ], cwd=self.base_dir,
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
            
            self.log(f"Gestor de servicios iniciado (PID: {process.pid})")
            
            # Esperar a que los servicios se inicien
            services_to_wait = [
                ("Prometheus", 9090, "http://localhost:9090/api/v1/status/config"),
                ("Grafana", 3000, "http://localhost:3000/api/health"),
                ("AlertManager", 9093, "http://localhost:9093/api/v1/status"),
                ("SMTP Service", 5555, "http://localhost:5555/health"),
                ("Dashboard", 5000, "http://localhost:5000/")
            ]
            
            all_started = True
            for service_name, port, url in services_to_wait:
                if not self.wait_for_service(service_name, port, url, timeout=30):
                    all_started = False
            
            if all_started:
                self.log("=" * 60)
                self.log("🎉 TODOS LOS SERVICIOS INICIADOS CORRECTAMENTE", "SUCCESS")
                self.show_service_status()
                return True
            else:
                self.log("⚠️ Algunos servicios no se iniciaron correctamente", "WARNING")
                self.show_service_status()
                return False
                
        except Exception as e:
            self.log(f"Error iniciando servicios: {e}", "ERROR")
            return False
    
    def stop_services(self):
        """Detener todos los servicios"""
        self.log("🛑 DETENIENDO SERVICIOS OPTIMON")
        self.log("=" * 60)
        
        try:
            # Usar el gestor de servicios para detener
            result = subprocess.run([
                sys.executable, "optimon_service_manager.py", "--stop"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Servicios detenidos correctamente", "SUCCESS")
            else:
                self.log("Algunos servicios pueden no haberse detenido completamente", "WARNING")
            
            # Verificación adicional
            time.sleep(3)
            self.show_service_status()
            
        except Exception as e:
            self.log(f"Error deteniendo servicios: {e}", "ERROR")
    
    def show_service_status(self):
        """Mostrar estado actual de servicios"""
        self.log("=" * 60)
        self.log("📊 ESTADO ACTUAL DE SERVICIOS")
        self.log("=" * 60)
        
        services = [
            ("Prometheus", 9090),
            ("Grafana", 3000), 
            ("AlertManager", 9093),
            ("SMTP Service", 5555),
            ("Dashboard", 5000),
            ("Windows Exporter", 9182)
        ]
        
        active_services = 0
        for service_name, port in services:
            if self.is_port_in_use(port):
                self.log(f"✅ {service_name}: EJECUTÁNDOSE (Puerto: {port})", "SUCCESS")
                active_services += 1
            else:
                self.log(f"❌ {service_name}: DETENIDO (Puerto: {port})", "ERROR")
        
        self.log("=" * 60)
        self.log(f"📈 SERVICIOS ACTIVOS: {active_services}/{len(services)}")
        
        if active_services >= 4:
            self.log("🎉 Sistema funcionando correctamente", "SUCCESS")
        elif active_services >= 2:
            self.log("⚠️ Sistema funcionando parcialmente", "WARNING")
        else:
            self.log("❌ Sistema con problemas serios", "ERROR")
        
        self.log("=" * 60)
    
    def run_tests(self):
        """Ejecutar pruebas completas"""
        self.log("🧪 EJECUTANDO PRUEBAS COMPLETAS")
        self.log("=" * 60)
        
        try:
            # Verificar que el script de pruebas existe
            test_script = self.base_dir / "test_complete_integral.py"
            if not test_script.exists():
                self.log("Script de pruebas no encontrado", "ERROR")
                return False
            
            # Ejecutar pruebas
            result = subprocess.run([
                sys.executable, str(test_script)
            ], cwd=self.base_dir, capture_output=True, text=True, timeout=300)
            
            # Mostrar salida
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                self.log("Pruebas ejecutadas exitosamente", "SUCCESS")
                return True
            else:
                self.log("Algunas pruebas fallaron", "WARNING")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Timeout ejecutando pruebas (5 minutos)", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error ejecutando pruebas: {e}", "ERROR")
            return False
    
    def show_access_info(self):
        """Mostrar información de acceso"""
        self.log("=" * 60)
        self.log("🌐 INFORMACIÓN DE ACCESO")
        self.log("=" * 60)
        self.log("Dashboard OptiMon: http://localhost:5000")
        self.log("Grafana: http://localhost:3000 (admin/admin)")
        self.log("Prometheus: http://localhost:9090")
        self.log("AlertManager: http://localhost:9093")
        self.log("Windows Exporter Metrics: http://localhost:9182/metrics")
        self.log("=" * 60)
        self.log("💡 Para detener servicios: python start_optimon_background.py --stop")
        self.log("💡 Para ver estado: python optimon_service_manager.py --status")

def main():
    """Función principal"""
    import argparse
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║         🚀 OPTIMON v2.0 - INICIO RÁPIDO EN SEGUNDO PLANO     ║
║                                                              ║
║  Gestión completa de servicios OptiMon:                     ║
║  • Inicio automático en segundo plano                       ║
║  • Verificación de estado                                   ║
║  • Pruebas completas opcionales                             ║
║  • Gestión de servicios Docker                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    parser = argparse.ArgumentParser(description="OptiMon Quick Start")
    parser.add_argument('--test', action='store_true', help='Ejecutar pruebas después del inicio')
    parser.add_argument('--stop', action='store_true', help='Detener todos los servicios')
    parser.add_argument('--status', action='store_true', help='Mostrar solo el estado')
    
    args = parser.parse_args()
    
    starter = OptiMonQuickStart()
    
    try:
        if args.stop:
            starter.stop_services()
            return 0
        
        elif args.status:
            starter.show_service_status()
            return 0
        
        else:
            # Iniciar servicios
            success = starter.start_services()
            
            if success:
                starter.show_access_info()
                
                # Ejecutar pruebas si se solicita
                if args.test:
                    time.sleep(5)  # Esperar un poco más antes de las pruebas
                    test_success = starter.run_tests()
                    if test_success:
                        starter.log("🎉 INICIO Y PRUEBAS COMPLETADOS EXITOSAMENTE", "SUCCESS")
                    else:
                        starter.log("⚠️ Servicios iniciados pero algunas pruebas fallaron", "WARNING")
                
                return 0 if success else 1
            else:
                starter.log("❌ Error en el inicio de servicios", "ERROR")
                return 1
    
    except KeyboardInterrupt:
        starter.log("⏹️ Interrumpido por el usuario", "WARNING")
        return 130
    except Exception as e:
        starter.log(f"❌ Error crítico: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    exit(main())