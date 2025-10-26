#!/usr/bin/env python3
"""
OptiMon - Iniciador Completo para Usuario Final
Simula experiencia de primer uso: instalación, configuración y ejecución
"""

import subprocess
import sys
import time
import requests
import webbrowser
import os
import threading
from datetime import datetime
from pathlib import Path

def print_banner():
    """Banner de bienvenida"""
    print("🚀" + "=" * 60 + "🚀")
    print("🖥️  OPTIMON - SISTEMA UNIFICADO DE MONITOREO v3.0.0")
    print("👤 EXPERIENCIA DE USUARIO FINAL - PRIMER USO")
    print("📅 " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🚀" + "=" * 60 + "🚀")
    print()

def check_prerequisites():
    """Verificar prerequisitos del sistema"""
    print("🔍 VERIFICANDO PREREQUISITOS DEL SISTEMA...")
    print("-" * 50)
    
    checks = []
    
    # Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            checks.append(("✅", f"Docker: {result.stdout.strip()}"))
        else:
            checks.append(("❌", "Docker no encontrado"))
    except:
        checks.append(("❌", "Docker no instalado"))
    
    # Docker Compose
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            checks.append(("✅", f"Docker Compose: OK"))
        else:
            checks.append(("❌", "Docker Compose no funcional"))
    except:
        checks.append(("❌", "Docker Compose no disponible"))
    
    # Python
    try:
        python_version = sys.version.split()[0]
        checks.append(("✅", f"Python: {python_version}"))
    except:
        checks.append(("❌", "Python no disponible"))
    
    # Puerto 5000
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        if result != 0:
            checks.append(("✅", "Puerto 5000: Disponible"))
        else:
            checks.append(("⚠️", "Puerto 5000: En uso"))
    except:
        checks.append(("✅", "Puerto 5000: Disponible"))
    
    for status, message in checks:
        print(f"{status} {message}")
    
    failed = sum(1 for status, _ in checks if status == "❌")
    return failed == 0

def install_dependencies():
    """Instalar dependencias Python"""
    print("\n📦 INSTALANDO DEPENDENCIAS...")
    print("-" * 40)
    
    try:
        print("🔄 Instalando requerimientos...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"❌ Error instalando dependencias: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout instalando dependencias")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_windows_exporter():
    """Configurar Windows Exporter (simulando usuario final)"""
    print("\n🖥️ CONFIGURANDO MONITOREO DE TU COMPUTADORA...")
    print("-" * 50)
    
    try:
        # Verificar si Windows Exporter ya está corriendo
        result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
        if ":9182" in result.stdout:
            print("✅ Windows Exporter ya está ejecutándose")
            return True
        
        # Ejecutar node_exporter_installer.py
        print("🔄 Instalando Windows Exporter...")
        result = subprocess.run([sys.executable, "node_exporter_installer.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Windows Exporter configurado")
            return True
        else:
            print(f"⚠️ Warning Windows Exporter: {result.stderr}")
            # Intentar continuar, puede que ya esté instalado
            return True
            
    except Exception as e:
        print(f"⚠️ Windows Exporter setup: {e}")
        # No es crítico, continuar
        return True

def start_containers():
    """Iniciar contenedores Docker"""
    print("\n🐳 INICIANDO CONTENEDORES DOCKER...")
    print("-" * 40)
    
    try:
        print("🔄 Levantando servicios...")
        result = subprocess.run(["docker", "compose", "up", "-d"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Contenedores iniciados correctamente")
            print("🔄 Esperando que los servicios estén listos...")
            time.sleep(10)
            return True
        else:
            print(f"❌ Error iniciando contenedores: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_web_portal():
    """Iniciar portal web"""
    print("\n🌐 INICIANDO PORTAL WEB OPTIMON...")
    print("-" * 40)
    
    try:
        print("� Iniciando servidor Flask...")
        
        # Cambiar al directorio correcto
        os.chdir(Path(__file__).parent)
        
        # Importar y ejecutar app
        from app import app
        
        def run_flask():
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
        # Ejecutar en hilo separado
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Esperar a que inicie
        time.sleep(5)
        
        # Verificar que esté funcionando
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Portal web funcionando")
            return True
        else:
            print(f"❌ Portal web error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error iniciando portal: {e}")
        return False

def verify_system():
    """Verificar que todo esté funcionando"""
    print("\n🔍 VERIFICACIÓN FINAL DEL SISTEMA...")
    print("-" * 45)
    
    services = [
        ("Portal OptiMon", "http://localhost:5000/api/health"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Windows Exporter", "http://localhost:9182/metrics")
    ]
    
    results = []
    for name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                results.append(("✅", f"{name}: Funcionando"))
            else:
                results.append(("❌", f"{name}: Error {response.status_code}"))
        except:
            results.append(("❌", f"{name}: No responde"))
    
    for status, message in results:
        print(f"{status} {message}")
    
    working = sum(1 for status, _ in results if status == "✅")
    return working >= 3  # Al menos 3 de 4 servicios

def open_user_interface():
    """Abrir interfaz de usuario"""
    print("\n🎯 ABRIENDO INTERFAZ DE USUARIO...")
    print("-" * 40)
    
    try:
        print("🌐 Abriendo portal web en tu navegador...")
        webbrowser.open("http://localhost:5000")
        time.sleep(2)
        
        print("📊 Abriendo Grafana...")
        webbrowser.open("http://localhost:3000")
        
        print("✅ Interfaces abiertas")
        return True
        
    except Exception as e:
        print(f"⚠️ Error abriendo navegadores: {e}")
        print("   Abrir manualmente:")
        print("   - Portal OptiMon: http://localhost:5000")
        print("   - Grafana: http://localhost:3000")
        return True

def show_user_guide():
    """Mostrar guía de usuario"""
    print("\n� GUÍA DE USUARIO FINAL")
    print("=" * 50)
    
    print("\n🎯 ACCESOS PRINCIPALES:")
    print("┌─────────────────────────────────────────────┐")
    print("│ 🌐 Portal OptiMon: http://localhost:5000   │")
    print("│ 📊 Grafana:        http://localhost:3000   │")
    print("│ 🔧 Prometheus:     http://localhost:9090   │")
    print("└─────────────────────────────────────────────┘")
    
    print("\n🔑 CREDENCIALES:")
    print("┌─────────────────────────────────────────────┐")
    print("│ Grafana:  admin / admin                     │")
    print("│ Portal:   No requiere login                 │")
    print("└─────────────────────────────────────────────┘")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1️⃣  Accede al portal: http://localhost:5000")
    print("2️⃣  Configura tus credenciales de Azure")
    print("3️⃣  Explora los dashboards de monitoreo")
    print("4️⃣  Genera infraestructura en la nube")
    print("5️⃣  Monitorea tu computadora en tiempo real")
    
    print("\n✨ FUNCIONALIDADES DISPONIBLES:")
    print("🖥️  Monitoreo local (tu computadora)")
    print("☁️  Generación de infraestructura Azure")
    print("📊 Dashboards avanzados de Grafana")
    print("🔔 Sistema de alertas")
    print("📈 Métricas en tiempo real")

def main():
    """Función principal - Experiencia completa de usuario final"""
    print_banner()
    
    print("🎯 SIMULANDO EXPERIENCIA DE USUARIO FINAL")
    print("� Como si fuera la primera vez que usas OptiMon")
    print()
    
    # Paso 1: Prerequisitos
    if not check_prerequisites():
        print("\n❌ PREREQUISITOS NO CUMPLIDOS")
        print("💡 Instala Docker y Docker Compose antes de continuar")
        return False
    
    # Paso 2: Dependencias
    if not install_dependencies():
        print("\n❌ ERROR EN DEPENDENCIAS")
        return False
    
    # Paso 3: Windows Exporter
    setup_windows_exporter()
    
    # Paso 4: Contenedores
    if not start_containers():
        print("\n❌ ERROR EN CONTENEDORES")
        return False
    
    # Paso 5: Portal Web
    if not start_web_portal():
        print("\n❌ ERROR EN PORTAL WEB")
        return False
    
    # Paso 6: Verificación
    if not verify_system():
        print("\n⚠️ ALGUNOS SERVICIOS NO FUNCIONAN")
        print("💡 Pero el sistema básico debería estar operativo")
    
    # Paso 7: Abrir interfaces
    open_user_interface()
    
    # Paso 8: Guía de usuario
    show_user_guide()
    
    print("\n🎉 ¡OPTIMON LISTO PARA USAR!")
    print("🚀 Disfruta explorando todas las funcionalidades")
    
    # Mantener el servidor corriendo
    print("\n🔄 SERVIDOR EJECUTÁNDOSE...")
    print("💡 Presiona Ctrl+C para detener")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 ¡Gracias por usar OptiMon!")
        return True

if __name__ == "__main__":
    main()