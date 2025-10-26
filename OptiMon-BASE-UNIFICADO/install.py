#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon Unified Installer
Instalador único que configura todo el sistema automáticamente
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_header():
    print("🚀 OptiMon Sistema Unificado - Instalador Automático")
    print("=" * 60)
    print("📋 Versión: 3.0.0-UNIFIED")
    print("🎯 Configuración automática completa")
    print()

def check_requirements():
    """Verificar requisitos del sistema"""
    print("🔍 Verificando requisitos del sistema...")
    
    requirements = {
        'docker': False,
        'python': False,
        'pip': False
    }
    
    # Verificar Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            requirements['docker'] = True
            print("✅ Docker encontrado")
        else:
            print("❌ Docker no encontrado")
    except FileNotFoundError:
        print("❌ Docker no instalado")
    
    # Verificar Python
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            requirements['python'] = True
            print(f"✅ Python encontrado: {result.stdout.strip()}")
        else:
            print("❌ Python no encontrado")
    except:
        print("❌ Error verificando Python")
    
    # Verificar pip
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            requirements['pip'] = True
            print("✅ pip encontrado")
        else:
            print("❌ pip no encontrado")
    except:
        print("❌ Error verificando pip")
    
    print()
    return all(requirements.values())

def install_python_dependencies():
    """Instalar dependencias Python"""
    print("📦 Instalando dependencias Python...")
    
    dependencies = [
        'flask',
        'requests',
        'psutil',
        'pyyaml'
    ]
    
    for dep in dependencies:
        try:
            print(f"   Instalando {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {dep} instalado")
            else:
                print(f"   ❌ Error instalando {dep}: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Excepción instalando {dep}: {e}")
    
    print()

def setup_docker_services():
    """Configurar servicios Docker"""
    print("🐳 Configurando servicios Docker...")
    
    try:
        # Detener servicios existentes
        print("   Deteniendo servicios existentes...")
        subprocess.run(['docker-compose', 'down'], capture_output=True)
        
        # Iniciar servicios
        print("   Iniciando servicios Docker...")
        result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Servicios Docker iniciados correctamente")
            
            # Esperar a que los servicios estén listos
            print("   ⏳ Esperando servicios...")
            time.sleep(30)
            
            return True
        else:
            print(f"   ❌ Error iniciando servicios: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción configurando Docker: {e}")
        return False

def setup_email_service():
    """Configurar servicio de email"""
    print("📧 Configurando servicio de email...")
    
    try:
        # Crear archivo .env con configuración por defecto
        env_content = """# OptiMon SMTP Configuration
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=Proyecto20251985@hotmail.com
SMTP_PASSWORD=proyecto2025
SMTP_USE_TLS=true
EMAIL_FROM_NAME=OptiMon Sistema Unificado
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("   ✅ Configuración SMTP creada")
        
        # Crear configuración de destinatarios por defecto
        os.makedirs('config', exist_ok=True)
        
        email_config = {
            'recipients': [
                {'email': 'Proyecto20251985@hotmail.com', 'active': True}
            ],
            'notifications_enabled': True,
            'created': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('config/email_recipients.json', 'w', encoding='utf-8') as f:
            json.dump(email_config, f, indent=2, ensure_ascii=False)
        
        print("   ✅ Destinatarios configurados")
        
        # Iniciar servicio email
        print("   🚀 Iniciando servicio email...")
        subprocess.Popen([
            sys.executable, 'core/email_service.py'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error configurando email: {e}")
        return False

def setup_local_monitoring():
    """Configurar monitoreo local automático"""
    print("💻 Configurando monitoreo local...")
    
    try:
        # El app.py se encargará de instalar Windows Exporter automáticamente
        print("   ✅ Configuración de monitoreo local preparada")
        print("   📝 Windows Exporter se instalará automáticamente al acceder al panel")
        return True
        
    except Exception as e:
        print(f"   ❌ Error configurando monitoreo local: {e}")
        return False

def verify_services():
    """Verificar que todos los servicios estén funcionando"""
    print("🔍 Verificando servicios...")
    
    services = {
        'Prometheus': ('localhost', 9090),
        'Grafana': ('localhost', 3000),
        'AlertManager': ('localhost', 9093)
    }
    
    all_ok = True
    
    for service_name, (host, port) in services.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ {service_name} activo en puerto {port}")
            else:
                print(f"   ❌ {service_name} no responde en puerto {port}")
                all_ok = False
                
        except Exception as e:
            print(f"   ❌ Error verificando {service_name}: {e}")
            all_ok = False
    
    # Verificar servicio email
    try:
        response = requests.get('http://localhost:5555/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ Servicio Email activo en puerto 5555")
        else:
            print("   ❌ Servicio Email no responde correctamente")
            all_ok = False
    except:
        print("   ⏳ Servicio Email iniciándose...")
    
    print()
    return all_ok

def start_main_application():
    """Iniciar aplicación principal"""
    print("🚀 Iniciando aplicación principal...")
    
    try:
        print("   📱 OptiMon Panel estará disponible en: http://localhost:5000")
        print("   📊 Grafana disponible en: http://localhost:3000 (admin/admin)")
        print("   📈 Prometheus disponible en: http://localhost:9090")
        print("   🚨 AlertManager disponible en: http://localhost:9093")
        print()
        print("✅ ¡Instalación completada exitosamente!")
        print()
        print("📋 Próximos pasos:")
        print("   1. Abrir http://localhost:5000 en tu navegador")
        print("   2. Configurar credenciales cloud (opcional)")
        print("   3. Agregar destinatarios de email")
        print("   4. El monitoreo local se configurará automáticamente")
        print()
        
        # Iniciar aplicación principal
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\n⏹️ Instalación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando aplicación: {e}")

def main():
    """Función principal del instalador"""
    print_header()
    
    # Verificar requisitos
    if not check_requirements():
        print("❌ Requisitos no cumplidos. Instale Docker y Python antes de continuar.")
        return False
    
    # Instalar dependencias Python
    install_python_dependencies()
    
    # Configurar Docker
    if not setup_docker_services():
        print("❌ Error configurando servicios Docker")
        return False
    
    # Configurar email
    if not setup_email_service():
        print("❌ Error configurando servicio email")
        return False
    
    # Configurar monitoreo local
    if not setup_local_monitoring():
        print("❌ Error configurando monitoreo local")
        return False
    
    # Verificar servicios
    if verify_services():
        print("✅ Todos los servicios están funcionando correctamente")
    else:
        print("⚠️ Algunos servicios pueden necesitar más tiempo para iniciar")
    
    # Iniciar aplicación principal
    start_main_application()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n🎉 ¡OptiMon Sistema Unificado instalado exitosamente!")
        else:
            print("\n❌ Instalación no completada")
    except KeyboardInterrupt:
        print("\n⏹️ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        
    input("\nPresiona Enter para continuar...")