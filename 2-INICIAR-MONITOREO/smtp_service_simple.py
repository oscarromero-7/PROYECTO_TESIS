#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon SMTP Service - Versión Simple
Servicio SMTP automatizado sin emojis para compatibilidad con Windows
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

class OptimOnSMTPService:
    """Servicio SMTP simplificado"""
    
    def __init__(self):
        self.smtp_process = None
        self.pid_file = Path("optimon_smtp.pid")
        
    def start(self):
        """Inicia el servicio SMTP"""
        if self.is_running():
            print(">> El servicio SMTP ya esta ejecutandose")
            return True
            
        print(">> Iniciando OptiMon SMTP Service...")
        
        try:
            # Verificar configuración
            if not self._check_env_file():
                return False
                
            # Iniciar el servicio
            self._start_service()
            
            print(">> OptiMon SMTP Service iniciado exitosamente")
            print(">> Puerto: 5555")
            print(">> Para detener: python smtp_service_simple.py stop")
            
            return True
            
        except Exception as e:
            print(f">> Error iniciando servicio: {e}")
            return False
            
    def stop(self):
        """Detiene el servicio SMTP"""
        print(">> Deteniendo OptiMon SMTP Service...")
        
        if self.smtp_process:
            try:
                self.smtp_process.terminate()
                self.smtp_process.wait(timeout=10)
                print(">> Servicio SMTP detenido")
            except subprocess.TimeoutExpired:
                self.smtp_process.kill()
                print(">> Servicio SMTP terminado forzadamente")
        
        # También intentar terminar por PID
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
            except:
                pass
            self.pid_file.unlink()
        
        print(">> OptiMon SMTP Service detenido")
        
    def status(self):
        """Muestra el estado del servicio"""
        if self.is_running():
            print(">> OptiMon SMTP Service esta ejecutandose")
            print(">> Puerto: 5555")
            print(">> URL: http://localhost:5555")
            return True
        else:
            print(">> OptiMon SMTP Service no esta ejecutandose")
            return False
            
    def is_running(self):
        """Verifica si el servicio está ejecutándose"""
        try:
            import requests
            response = requests.get("http://localhost:5555/health", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def _check_env_file(self):
        """Verifica la configuración .env"""
        env_file = Path(".env")
        if not env_file.exists():
            print(">> Error: Archivo .env no encontrado")
            print(">> Copia .env.gmail a .env y configura tus credenciales")
            return False
            
        print(">> Configuracion .env encontrada")
        return True
        
    def _start_service(self):
        """Inicia el servicio como proceso en segundo plano"""
        # Crear comando de inicio
        if sys.platform == "win32":
            # En Windows, usar START para ejecutar en ventana separada
            cmd = f'start "OptiMon SMTP" cmd /k "python optimon_smtp_service.py"'
            subprocess.run(cmd, shell=True)
        else:
            # En Linux/Mac, usar nohup
            self.smtp_process = subprocess.Popen(
                [sys.executable, "optimon_smtp_service.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Esperar un poco para que inicie
        time.sleep(3)
        
        # Verificar que esté funcionando
        if not self.is_running():
            raise Exception("El servicio no se inicio correctamente")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python smtp_service_simple.py {start|stop|status}")
        print("")
        print("Comandos:")
        print("  start  - Iniciar servicio SMTP")
        print("  stop   - Detener servicio SMTP") 
        print("  status - Ver estado del servicio")
        sys.exit(1)
        
    service = OptimOnSMTPService()
    command = sys.argv[1].lower()
    
    if command == "start":
        if service.start():
            print(">> Servicio iniciado correctamente")
        else:
            print(">> Error iniciando servicio")
            sys.exit(1)
            
    elif command == "stop":
        service.stop()
        
    elif command == "status":
        service.status()
        
    else:
        print(">> Comando no valido. Usar: start|stop|status")
        sys.exit(1)

if __name__ == "__main__":
    main()