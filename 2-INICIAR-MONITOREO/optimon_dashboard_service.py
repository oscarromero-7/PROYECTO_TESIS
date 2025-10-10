#!/usr/bin/env python3
"""
OptiMon Dashboard Service Manager
Gestiona el dashboard como un servicio en segundo plano
"""

import os
import sys
import time
import psutil
import subprocess
import argparse
import requests
from pathlib import Path

class OptiMonDashboardService:
    def __init__(self):
        self.port = 5000
        self.dashboard_script = "optimon_dashboard.py"
        self.base_dir = Path(__file__).parent
        
    def is_running(self):
        """Verificar si el dashboard está ejecutándose"""
        try:
            # Verificar por puerto
            for conn in psutil.net_connections():
                if conn.laddr.port == self.port and conn.status == psutil.CONN_LISTEN:
                    return True, conn.pid
        except:
            pass
        
        # Verificar por proceso
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and any('optimon_dashboard.py' in cmd for cmd in proc.info['cmdline']):
                    return True, proc.info['pid']
            except:
                continue
        
        return False, None
    
    def start(self):
        """Iniciar el dashboard"""
        running, pid = self.is_running()
        if running:
            print(f"✅ El dashboard ya está ejecutándose (PID: {pid})")
            return True
        
        print("🚀 Iniciando OptiMon Dashboard...")
        
        try:
            # Cambiar al directorio del script
            os.chdir(self.base_dir)
            
            # Iniciar en segundo plano
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    [sys.executable, self.dashboard_script],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:  # Linux/macOS
                subprocess.Popen(
                    [sys.executable, self.dashboard_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            
            # Esperar y verificar que se inició
            for i in range(15):  # Esperar hasta 15 segundos
                time.sleep(1)
                running, pid = self.is_running()
                if running:
                    print(f"✅ Dashboard iniciado correctamente (PID: {pid})")
                    print(f"🌐 Accede a: http://localhost:{self.port}")
                    return True
                
            print("❌ Error: El dashboard no se pudo iniciar")
            return False
            
        except Exception as e:
            print(f"❌ Error iniciando el dashboard: {e}")
            return False
    
    def stop(self):
        """Detener el dashboard"""
        running, pid = self.is_running()
        if not running:
            print("ℹ️  El dashboard no está ejecutándose")
            return True
        
        print(f"🛑 Deteniendo dashboard (PID: {pid})...")
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # Esperar a que termine
            for i in range(10):
                time.sleep(0.5)
                if not proc.is_running():
                    print("✅ Dashboard detenido correctamente")
                    return True
            
            # Forzar si no se detuvo
            proc.kill()
            print("✅ Dashboard detenido (forzado)")
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo el dashboard: {e}")
            return False
    
    def restart(self):
        """Reiniciar el dashboard"""
        print("🔄 Reiniciando dashboard...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Mostrar estado del dashboard"""
        running, pid = self.is_running()
        
        if running:
            print(f"✅ Dashboard ejecutándose (PID: {pid})")
            print(f"🌐 URL: http://localhost:{self.port}")
            
            # Verificar conectividad
            try:
                response = requests.get(f"http://localhost:{self.port}/api/health", timeout=5)
                print(f"📡 Estado API: {'OK' if response.status_code == 200 else 'Error'}")
            except:
                print("📡 Estado API: No disponible")
        else:
            print("❌ Dashboard no está ejecutándose")
        
        return running

def main():
    parser = argparse.ArgumentParser(description='OptiMon Dashboard Service Manager')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'], 
                       help='Acción a realizar')
    
    args = parser.parse_args()
    
    service = OptiMonDashboardService()
    
    if args.action == 'start':
        service.start()
    elif args.action == 'stop':
        service.stop()
    elif args.action == 'restart':
        service.restart()
    elif args.action == 'status':
        service.status()

if __name__ == '__main__':
    main()