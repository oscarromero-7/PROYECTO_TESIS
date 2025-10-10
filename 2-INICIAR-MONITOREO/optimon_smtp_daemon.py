#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon SMTP Daemon Service
Servicio que se ejecuta en segundo plano para envío automático de emails
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from threading import Thread
import subprocess

# Agregar la ruta del proyecto al path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

def setup_logging():
    """Configura el logging para el daemon"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "optimon_smtp_daemon.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("OptimOnSMTPDaemon")

class OptimOnSMTPDaemon:
    """Daemon para el servicio SMTP OptiMon"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.smtp_process = None
        self.running = False
        self.pid_file = Path("optimon_smtp.pid")
        
    def start(self):
        """Inicia el daemon SMTP"""
        if self.is_running():
            self.logger.warning("El servicio SMTP ya está ejecutándose")
            return True
            
        self.logger.info("🚀 Iniciando OptiMon SMTP Daemon...")
        
        try:
            # Verificar configuración antes de iniciar
            if not self._check_configuration():
                return False
                
            # Iniciar el servicio SMTP
            self._start_smtp_service()
            
            # Registrar el PID
            self._write_pid()
            
            # Configurar manejadores de señales
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            self.logger.info("✅ OptiMon SMTP Daemon iniciado exitosamente")
            
            # Mantenerse vivo y monitorear el servicio
            self._monitor_service()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando daemon: {e}")
            return False
            
    def stop(self):
        """Detiene el daemon SMTP"""
        self.logger.info("🛑 Deteniendo OptiMon SMTP Daemon...")
        
        self.running = False
        
        if self.smtp_process:
            try:
                self.smtp_process.terminate()
                self.smtp_process.wait(timeout=10)
                self.logger.info("✅ Servicio SMTP detenido")
            except subprocess.TimeoutExpired:
                self.smtp_process.kill()
                self.logger.warning("⚠️ Servicio SMTP forzadamente terminado")
        
        self._remove_pid()
        self.logger.info("✅ OptiMon SMTP Daemon detenido")
        
    def restart(self):
        """Reinicia el daemon SMTP"""
        self.logger.info("🔄 Reiniciando OptiMon SMTP Daemon...")
        self.stop()
        time.sleep(2)
        return self.start()
        
    def is_running(self):
        """Verifica si el daemon está ejecutándose"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificar si el proceso existe (Windows)
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                self._remove_pid()
                return False
                
        except (ValueError, FileNotFoundError):
            return False
            
    def status(self):
        """Muestra el estado del daemon"""
        if self.is_running():
            print("✅ OptiMon SMTP Daemon está ejecutándose")
            print(f"📁 PID File: {self.pid_file}")
            print(f"📊 Puerto: 5555")
            return True
        else:
            print("❌ OptiMon SMTP Daemon no está ejecutándose")
            return False
            
    def _check_configuration(self):
        """Verifica la configuración SMTP"""
        env_file = Path(".env")
        if not env_file.exists():
            self.logger.error("❌ Archivo .env no encontrado")
            return False
            
        # Verificar variables requeridas
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            required_vars = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_HOST']
            missing_vars = []
            
            for var in required_vars:
                value = os.getenv(var)
                if not value or value == 'default_password':
                    missing_vars.append(var)
                    
            if missing_vars:
                self.logger.error(f"❌ Variables SMTP faltantes: {missing_vars}")
                return False
                
            self.logger.info("✅ Configuración SMTP verificada")
            return True
            
        except ImportError:
            self.logger.error("❌ python-dotenv no instalado")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error verificando configuración: {e}")
            return False
            
    def _start_smtp_service(self):
        """Inicia el servicio SMTP como subproceso"""
        try:
            smtp_script = Path("optimon_smtp_service.py")
            if not smtp_script.exists():
                raise FileNotFoundError("optimon_smtp_service.py no encontrado")
                
            # Iniciar como subproceso
            self.smtp_process = subprocess.Popen(
                [sys.executable, str(smtp_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_path)
            )
            
            # Esperar un poco para verificar que inició correctamente
            time.sleep(3)
            
            if self.smtp_process.poll() is not None:
                stdout, stderr = self.smtp_process.communicate()
                raise Exception(f"Servicio SMTP falló al iniciar: {stderr.decode()}")
                
            self.logger.info("✅ Servicio SMTP iniciado como subproceso")
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando servicio SMTP: {e}")
            raise
            
    def _monitor_service(self):
        """Monitorea el servicio y lo reinicia si es necesario"""
        self.logger.info("👁️ Iniciando monitoreo del servicio...")
        
        while self.running:
            try:
                # Verificar si el proceso sigue vivo
                if self.smtp_process and self.smtp_process.poll() is not None:
                    self.logger.warning("⚠️ Servicio SMTP se detuvo, reiniciando...")
                    self._start_smtp_service()
                    
                # Verificar conectividad HTTP
                import requests
                try:
                    response = requests.get("http://localhost:5555/health", timeout=5)
                    if response.status_code != 200:
                        raise Exception("Health check falló")
                except:
                    self.logger.warning("⚠️ Health check falló, reiniciando servicio...")
                    if self.smtp_process:
                        self.smtp_process.terminate()
                    time.sleep(2)
                    self._start_smtp_service()
                    
                # Esperar antes del siguiente check
                time.sleep(30)  # Check cada 30 segundos
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"❌ Error en monitoreo: {e}")
                time.sleep(10)
                
    def _write_pid(self):
        """Escribe el PID del daemon"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
    def _remove_pid(self):
        """Elimina el archivo PID"""
        if self.pid_file.exists():
            self.pid_file.unlink()
            
    def _signal_handler(self, signum, frame):
        """Manejador de señales para cierre limpio"""
        self.logger.info(f"📡 Señal recibida: {signum}")
        self.stop()
        sys.exit(0)

def main():
    """Función principal del daemon"""
    if len(sys.argv) < 2:
        print("Uso: python optimon_smtp_daemon.py {start|stop|restart|status}")
        sys.exit(1)
        
    daemon = OptimOnSMTPDaemon()
    command = sys.argv[1].lower()
    
    if command == "start":
        if daemon.start():
            print("✅ OptiMon SMTP Daemon iniciado")
        else:
            print("❌ Error iniciando daemon")
            sys.exit(1)
            
    elif command == "stop":
        daemon.stop()
        print("✅ OptiMon SMTP Daemon detenido")
        
    elif command == "restart":
        if daemon.restart():
            print("✅ OptiMon SMTP Daemon reiniciado")
        else:
            print("❌ Error reiniciando daemon")
            sys.exit(1)
            
    elif command == "status":
        daemon.status()
        
    else:
        print("Comando no válido. Usar: start|stop|restart|status")
        sys.exit(1)

if __name__ == "__main__":
    main()