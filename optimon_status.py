#!/usr/bin/env python3
"""
OptiMon - Configurador Final y Estado del Sistema
Script para verificar y mostrar el estado completo del sistema automatizado
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def print_header(title):
    """Imprimir encabezado formateado"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def check_file_exists(file_path, description):
    """Verificar si un archivo existe"""
    if os.path.exists(file_path):
        print(f"[OK] {description}: OK")
        return True
    else:
        print(f"[ERROR] {description}: FALTANTE")
        return False

def check_service_status():
    """Verificar estado del servicio OptiMon"""
    print_header("ESTADO DEL SERVICIO OPTIMON")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Verificar archivos principales
    files_to_check = [
        ("optimon_dashboard_service.py", "Servicio principal"),
        ("dashboard_auto_verifier_simple.py", "Motor de verificación"),
        ("configure_optimon.py", "Configurador"),
        ("install_optimon_service.bat", "Instalador Windows"),
        ("MANUAL_OPTIMON_SERVICE.md", "Manual de usuario")
    ]
    
    all_files_ok = True
    for file_name, description in files_to_check:
        if not check_file_exists(os.path.join(base_dir, file_name), description):
            all_files_ok = False
    
    # Verificar dependencias Python
    print("\nDEPENDENCIAS PYTHON:")
    dependencies = ["schedule", "requests", "json", "datetime"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"[OK] {dep}: Instalado")
        except ImportError:
            print(f"[ERROR] {dep}: FALTANTE")
            all_files_ok = False
    
    return all_files_ok

def check_docker_services():
    """Verificar servicios Docker"""
    print_header("SERVICIOS DOCKER")
    
    try:
        # Verificar docker-compose
        result = subprocess.run([
            'docker-compose', 'ps'
        ], capture_output=True, text=True, cwd='2-INICIAR-MONITOREO')
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            services_count = 0
            for line in lines:
                if 'Up' in line:
                    services_count += 1
                    service_name = line.split()[0]
                    print(f"[OK] {service_name}: Activo")
            
            if services_count >= 3:
                print(f"\n[OK] Servicios Docker: {services_count} activos")
                return True
            else:
                print(f"\n[WARNING] Servicios Docker: Solo {services_count} activos (esperado: 3+)")
                return False
        else:
            print("[ERROR] Error verificando servicios Docker")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando docker-compose: {e}")
        return False

def check_web_interfaces():
    """Verificar interfaces web"""
    print_header("INTERFACES WEB")
    
    interfaces = [
        ("http://localhost:3000", "Grafana"),
        ("http://localhost:9090", "Prometheus"),
        ("http://localhost:9093", "AlertManager")
    ]
    
    all_ok = True
    
    for url, name in interfaces:
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name}: Disponible ({url})")
            else:
                print(f"[WARNING] {name}: Respuesta {response.status_code} ({url})")
                all_ok = False
        except Exception as e:
            print(f"[ERROR] {name}: No disponible ({url})")
            all_ok = False
    
    return all_ok

def show_configuration():
    """Mostrar configuración actual"""
    print_header("CONFIGURACION ACTUAL")
    
    config_file = "optimon_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("Configuración cargada:")
            for key, value in config.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error leyendo configuración: {e}")
    else:
        print("[WARNING] Archivo de configuracion no encontrado")
        print("Ejecuta: python configure_optimon.py")

def show_recent_logs():
    """Mostrar logs recientes"""
    print_header("LOGS RECIENTES")
    
    log_files = [
        "optimon_service.log",
        "dashboard_verification.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n{log_file} (últimas 5 líneas):")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"  Error leyendo log: {e}")
        else:
            print(f"\n{log_file}: No encontrado")

def run_verification_test():
    """Ejecutar prueba de verificación"""
    print_header("PRUEBA DE VERIFICACION")
    
    try:
        result = subprocess.run([
            sys.executable, 'dashboard_auto_verifier_simple.py'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[OK] Verificacion automatica: EXITOSA")
            if "AUTOMATIZACION COMPLETADA EXITOSAMENTE" in result.stdout:
                print("[OK] Todos los dashboards funcionando correctamente")
            return True
        else:
            print("[ERROR] Verificacion automatica: FALLO")
            print("Error:", result.stderr[:200])
            return False
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando verificacion: {e}")
        return False

def show_installation_instructions():
    """Mostrar instrucciones de instalación"""
    print_header("INSTRUCCIONES DE INSTALACION")
    
    print("""
PARA INSTALAR COMO SERVICIO DE WINDOWS:

1. Como Administrador, ejecutar:
   install_optimon_service.bat

2. Configurar parámetros:
   python configure_optimon.py

3. Iniciar servicio:
   schtasks /run /tn "OptiMon Dashboard Service"

4. Verificar estado:
   schtasks /query /tn "OptiMon Dashboard Service"

PARA VERIFICACION MANUAL:
   python optimon_dashboard_service.py

PARA MONITOREO CONTINUO:
   python optimon_dashboard_service.py --service
    """)

def main():
    """Función principal del configurador"""
    print("OPTIMON - CONFIGURADOR FINAL Y VERIFICACION DE ESTADO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificaciones del sistema
    checks = []
    checks.append(("Archivos del servicio", check_service_status()))
    checks.append(("Servicios Docker", check_docker_services()))
    checks.append(("Interfaces web", check_web_interfaces()))
    
    # Mostrar configuración y logs
    show_configuration()
    show_recent_logs()
    
    # Ejecutar prueba de verificación
    checks.append(("Verificación automática", run_verification_test()))
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    all_ok = True
    for check_name, check_result in checks:
        status = "[OK] OK" if check_result else "[ERROR] ERROR"
        print(f"{status} {check_name}")
        if not check_result:
            all_ok = False
    
    print(f"\nESTADO GENERAL DEL SISTEMA: {'[OK] OPERATIVO' if all_ok else '[WARNING] REQUIERE ATENCION'}")
    
    if all_ok:
        print("\n[SUCCESS] OptiMon esta completamente operativo y listo para monitoreo automatico!")
        print("\nPara activar monitoreo continuo:")
        print("   python optimon_dashboard_service.py --service")
    else:
        print("\n[WARNING] Algunos componentes requieren atencion.")
        print("Revisa los errores mostrados arriba.")
    
    show_installation_instructions()

if __name__ == "__main__":
    main()