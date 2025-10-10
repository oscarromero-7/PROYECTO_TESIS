#!/usr/bin/env python3
"""
Servicio de Monitoreo Automatizado de Dashboards - OptiMon
Sistema completamente automatizado que se ejecuta como servicio
"""

import schedule
import time
import subprocess
import sys
import os
import json
from datetime import datetime

class OptiMonDashboardService:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.base_dir, "optimon_service.log")
        self.config_file = os.path.join(self.base_dir, "optimon_config.json")
        
        # Cargar configuración
        self.load_config()
    
    def load_config(self):
        """Cargar configuración del servicio"""
        default_config = {
            "verification_interval_minutes": 5,
            "auto_restart_services": True,
            "max_retry_attempts": 3,
            "notification_webhook": "",
            "enabled_checks": {
                "prometheus_health": True,
                "grafana_health": True,
                "dashboard_validation": True,
                "datasource_correction": True,
                "auto_import": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Guardar configuración actual"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def log(self, message):
        """Escribir al log del servicio"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except:
            pass
    
    def run_dashboard_verification(self):
        """Ejecutar verificación de dashboards"""
        self.log("Iniciando verificacion automatica de dashboards...")
        
        try:
            # Ejecutar el verificador simplificado
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.base_dir, 'dashboard_auto_verifier_simple.py')
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("Verificacion completada exitosamente")
                # Extraer información del resultado
                if "AUTOMATIZACION COMPLETADA EXITOSAMENTE" in result.stdout:
                    self.log("Todos los dashboards funcionando correctamente")
                else:
                    self.log("Verificacion con advertencias - revisar logs")
            else:
                self.log(f"Verificacion fallo - codigo: {result.returncode}")
                self.log(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log("Verificacion timeout - proceso tardó más de 5 minutos")
        except Exception as e:
            self.log(f"Error ejecutando verificacion: {e}")
    
    def check_docker_services(self):
        """Verificar estado de servicios Docker"""
        self.log("Verificando servicios Docker...")
        
        try:
            # Verificar docker-compose
            result = subprocess.run([
                'docker-compose', 'ps'
            ], capture_output=True, text=True, cwd=os.path.join(self.base_dir, '2-INICIAR-MONITOREO'))
            
            if result.returncode == 0:
                # Contar servicios UP
                up_services = result.stdout.count('Up')
                self.log(f"Servicios Docker verificados: {up_services} activos")
                
                if up_services < 3:  # Esperamos Prometheus, Grafana, AlertManager
                    self.log("ALERTA: Algunos servicios Docker no están activos")
                    if self.config.get('auto_restart_services', False):
                        self.restart_docker_services()
            else:
                self.log("Error verificando servicios Docker")
                
        except Exception as e:
            self.log(f"Error verificando Docker: {e}")
    
    def restart_docker_services(self):
        """Reiniciar servicios Docker si es necesario"""
        self.log("Reiniciando servicios Docker...")
        
        try:
            # Reiniciar servicios
            result = subprocess.run([
                'docker-compose', 'restart'
            ], capture_output=True, text=True, cwd=os.path.join(self.base_dir, '2-INICIAR-MONITOREO'))
            
            if result.returncode == 0:
                self.log("Servicios Docker reiniciados exitosamente")
                time.sleep(30)  # Esperar a que los servicios se estabilicen
            else:
                self.log(f"Error reiniciando servicios: {result.stderr}")
                
        except Exception as e:
            self.log(f"Error reiniciando Docker: {e}")
    
    def run_scheduled_check(self):
        """Ejecutar verificación programada completa"""
        self.log("=" * 60)
        self.log("INICIANDO VERIFICACION PROGRAMADA")
        self.log("=" * 60)
        
        # 1. Verificar servicios Docker
        if self.config['enabled_checks']['prometheus_health']:
            self.check_docker_services()
        
        # 2. Ejecutar verificación de dashboards
        if self.config['enabled_checks']['dashboard_validation']:
            self.run_dashboard_verification()
        
        self.log("Verificacion programada completada")
        self.log("=" * 60)
    
    def start_service(self):
        """Iniciar el servicio de monitoreo"""
        self.log("INICIANDO SERVICIO DE MONITOREO OPTIMON")
        self.log(f"Intervalo de verificacion: {self.config['verification_interval_minutes']} minutos")
        
        # Programar verificación periódica
        schedule.every(self.config['verification_interval_minutes']).minutes.do(self.run_scheduled_check)
        
        # Ejecutar verificación inicial
        self.run_scheduled_check()
        
        self.log("Servicio iniciado - esperando próxima verificación...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto
                
        except KeyboardInterrupt:
            self.log("Servicio detenido por el usuario")
        except Exception as e:
            self.log(f"Error en servicio: {e}")

def create_windows_service_installer():
    """Crear instalador para servicio de Windows"""
    service_script = '''@echo off
echo Instalando OptiMon Dashboard Service...

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

REM Instalar dependencias de Python si es necesario
python -m pip install schedule requests

REM Crear tarea programada de Windows
schtasks /create /sc minute /mo 5 /tn "OptiMon Dashboard Service" /tr "python \"%~dp0optimon_dashboard_service.py\" --service" /f

echo.
echo Servicio OptiMon instalado exitosamente!
echo.
echo Para iniciar: schtasks /run /tn "OptiMon Dashboard Service"
echo Para detener: schtasks /end /tn "OptiMon Dashboard Service"
echo Para desinstalar: schtasks /delete /tn "OptiMon Dashboard Service" /f
echo.
pause
'''
    
    with open('install_optimon_service.bat', 'w') as f:
        f.write(service_script)
    
    print("[OK] Instalador de servicio creado: install_optimon_service.bat")

def create_config_manager():
    """Crear script para gestionar configuración"""
    config_script = '''#!/usr/bin/env python3
"""
Gestor de Configuración de OptiMon
"""

import json
import os

def load_config():
    """Cargar configuración actual"""
    config_file = "optimon_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    """Guardar configuración"""
    with open("optimon_config.json", 'w') as f:
        json.dump(config, f, indent=2)

def configure_service():
    """Configurar el servicio interactivamente"""
    print("CONFIGURACION DEL SERVICIO OPTIMON")
    print("=" * 40)
    
    config = load_config() or {
        "verification_interval_minutes": 5,
        "auto_restart_services": True,
        "max_retry_attempts": 3,
        "enabled_checks": {
            "prometheus_health": True,
            "grafana_health": True,
            "dashboard_validation": True,
            "datasource_correction": True,
            "auto_import": True
        }
    }
    
    print(f"Intervalo actual: {config['verification_interval_minutes']} minutos")
    new_interval = input("Nuevo intervalo (minutos, Enter para mantener): ")
    if new_interval.strip():
        config['verification_interval_minutes'] = int(new_interval)
    
    print(f"Auto-reinicio: {config['auto_restart_services']}")
    restart = input("Auto-reiniciar servicios? (s/n, Enter para mantener): ")
    if restart.lower() == 's':
        config['auto_restart_services'] = True
    elif restart.lower() == 'n':
        config['auto_restart_services'] = False
    
    save_config(config)
    print("\\nConfiguracion guardada exitosamente!")
    print("Reinicia el servicio para aplicar cambios.")

if __name__ == "__main__":
    configure_service()
'''
    
    with open('configure_optimon.py', 'w') as f:
        f.write(config_script)
    
    print("[OK] Configurador creado: configure_optimon.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        # Ejecutar como servicio
        service = OptiMonDashboardService()
        service.start_service()
    elif len(sys.argv) > 1 and sys.argv[1] == "--install":
        # Crear instaladores
        create_windows_service_installer()
        create_config_manager()
        print("\n[INSTRUCCIONES DE INSTALACION]")
        print("1. Ejecutar: install_optimon_service.bat")
        print("2. Configurar: python configure_optimon.py")
        print("3. Verificar logs: type optimon_service.log")
    else:
        # Ejecutar verificación única
        service = OptiMonDashboardService()
        service.run_scheduled_check()