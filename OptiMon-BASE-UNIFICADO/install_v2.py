#!/usr/bin/env python3
"""
OptiMon Sistema Unificado - Instalador Automático v3.0.0
Instala y configura todo el sistema de monitoreo automáticamente
"""

import os
import sys
import json
import time
import shutil
import subprocess
import platform
import urllib.request
from pathlib import Path

class OptiMonInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.is_windows = platform.system().lower() == 'windows'
        self.python_cmd = 'python' if self.is_windows else 'python3'
        
        print("=" * 70)
        print("🚀 OptiMon Sistema Unificado - Instalador Automático v3.0.0")
        print("=" * 70)
        print("📦 Este instalador configurará automáticamente:")
        print("   ✅ Dependencias Python")
        print("   ✅ Docker y servicios (Prometheus, Grafana, AlertManager)")
        print("   ✅ Windows Exporter (monitoreo local)")
        print("   ✅ Sistema de alertas por email")
        print("   ✅ Dashboard web unificado")
        print("=" * 70)
        
    def check_requirements(self):
        """Verificar requisitos del sistema"""
        print("\n🔍 Verificando requisitos del sistema...")
        
        # Check Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
                raise Exception(f"Python 3.7+ requerido. Versión actual: {python_version.major}.{python_version.minor}")
            print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        except Exception as e:
            print(f"   ❌ Error Python: {e}")
            return False
            
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {result.stdout.strip()}")
            else:
                raise Exception("Docker no encontrado")
        except Exception as e:
            print(f"   ❌ Docker no disponible: {e}")
            print("   📋 Instale Docker Desktop desde: https://www.docker.com/products/docker-desktop")
            return False
            
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {result.stdout.strip()}")
            else:
                # Try old docker-compose
                result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ {result.stdout.strip()}")
                else:
                    raise Exception("Docker Compose no encontrado")
        except Exception as e:
            print(f"   ❌ Docker Compose no disponible: {e}")
            return False
            
        print("   ✅ Todos los requisitos cumplidos")
        return True
        
    def install_python_dependencies(self):
        """Instalar dependencias Python"""
        print("\n📦 Instalando dependencias Python...")
        
        requirements_file = self.base_dir / 'requirements.txt'
        if not requirements_file.exists():
            print("   ❌ Archivo requirements.txt no encontrado")
            return False
            
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Dependencias Python instaladas correctamente")
                return True
            else:
                print(f"   ❌ Error instalando dependencias: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
            
    def setup_directories(self):
        """Crear estructura de directorios"""
        print("\n📁 Configurando estructura de directorios...")
        
        directories = [
            'config',
            'core',
            'templates',
            'static',
            'docker/prometheus',
            'docker/grafana',
            'docker/alertmanager',
            'logs',
            'data'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")
            
        return True
        
    def download_windows_exporter(self):
        """Descargar e instalar Windows Exporter"""
        if not self.is_windows:
            print("\n⏭️  Saltando Windows Exporter (no es Windows)")
            return True
            
        print("\n⬇️  Configurando Windows Exporter...")
        
        exporter_dir = self.base_dir / 'exporters'
        exporter_dir.mkdir(exist_ok=True)
        
        exporter_exe = exporter_dir / 'windows_exporter.exe'
        
        if exporter_exe.exists():
            print("   ✅ Windows Exporter ya existe")
            return True
            
        try:
            # URL del Windows Exporter oficial
            url = "https://github.com/prometheus-community/windows_exporter/releases/latest/download/windows_exporter-0.25.1-amd64.exe"
            
            print("   📥 Descargando Windows Exporter...")
            urllib.request.urlretrieve(url, exporter_exe)
            
            print("   ✅ Windows Exporter descargado")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Error descargando Windows Exporter: {e}")
            print("   📋 Descargue manualmente desde: https://github.com/prometheus-community/windows_exporter/releases")
            return True  # No es crítico
            
    def start_docker_services(self):
        """Iniciar servicios Docker"""
        print("\n🐳 Iniciando servicios Docker...")
        
        compose_file = self.base_dir / 'docker-compose.yml'
        if not compose_file.exists():
            print("   ❌ docker-compose.yml no encontrado")
            return False
            
        try:
            # Stop any existing services
            subprocess.run(['docker', 'compose', 'down'], cwd=self.base_dir, capture_output=True)
            
            # Start services
            result = subprocess.run(['docker', 'compose', 'up', '-d'], 
                                  cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Servicios Docker iniciados")
                
                # Wait for services to be ready
                print("   ⏳ Esperando servicios...")
                time.sleep(10)
                
                # Check services
                self.check_docker_services()
                return True
            else:
                print(f"   ❌ Error iniciando Docker: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
            
    def check_docker_services(self):
        """Verificar estado de servicios Docker"""
        print("\n🔍 Verificando servicios...")
        
        services = {
            'Prometheus': 'http://localhost:9090',
            'Grafana': 'http://localhost:3000',
            'AlertManager': 'http://localhost:9093'
        }
        
        for service, url in services.items():
            try:
                import urllib.request
                response = urllib.request.urlopen(url, timeout=5)
                if response.status == 200:
                    print(f"   ✅ {service}: {url}")
                else:
                    print(f"   ⚠️  {service}: {url} (status: {response.status})")
            except Exception:
                print(f"   ❌ {service}: {url} (no responde)")
                
    def start_windows_exporter(self):
        """Iniciar Windows Exporter"""
        if not self.is_windows:
            return True
            
        print("\n📊 Iniciando Windows Exporter...")
        
        exporter_exe = self.base_dir / 'exporters' / 'windows_exporter.exe'
        
        if not exporter_exe.exists():
            print("   ⚠️  Windows Exporter no encontrado, saltando...")
            return True
            
        try:
            # Check if already running
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq windows_exporter.exe'], 
                                  capture_output=True, text=True)
            
            if 'windows_exporter.exe' in result.stdout:
                print("   ✅ Windows Exporter ya está ejecutándose")
                return True
                
            # Start Windows Exporter
            subprocess.Popen([str(exporter_exe)], cwd=exporter_exe.parent)
            
            print("   ✅ Windows Exporter iniciado (puerto 9182)")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Error iniciando Windows Exporter: {e}")
            return True  # No es crítico
            
    def start_web_portal(self):
        """Iniciar portal web"""
        print("\n🌐 Iniciando portal web OptiMon...")
        
        app_file = self.base_dir / 'app.py'
        if not app_file.exists():
            print("   ❌ app.py no encontrado")
            return False
            
        try:
            print("   🚀 Portal web iniciándose en http://localhost:5000")
            print("   📋 Para detener: Ctrl+C")
            print("=" * 70)
            
            # Start Flask app
            env = os.environ.copy()
            env['FLASK_APP'] = str(app_file)
            env['FLASK_ENV'] = 'production'
            
            subprocess.run([sys.executable, str(app_file)], cwd=self.base_dir, env=env)
            
        except KeyboardInterrupt:
            print("\n👋 Portal web detenido")
            return True
        except Exception as e:
            print(f"   ❌ Error iniciando portal: {e}")
            return False
            
    def show_final_info(self):
        """Mostrar información final"""
        print("\n" + "=" * 70)
        print("🎉 ¡OptiMon instalado correctamente!")
        print("=" * 70)
        print("🌐 Accesos:")
        print("   • Portal OptiMon:    http://localhost:5000")
        print("   • Grafana:           http://localhost:3000 (admin/admin)")
        print("   • Prometheus:        http://localhost:9090")
        print("   • AlertManager:      http://localhost:9093")
        if self.is_windows:
            print("   • Windows Exporter:  http://localhost:9182/metrics")
        print("\n📋 Para reiniciar el sistema:")
        if self.is_windows:
            print("   INSTALL.bat")
        else:
            print("   python3 install.py")
        print("\n📋 Para detener servicios:")
        print("   docker compose down")
        print("=" * 70)
        
    def run(self):
        """Ejecutar instalación completa"""
        try:
            if not self.check_requirements():
                return False
                
            if not self.install_python_dependencies():
                return False
                
            if not self.setup_directories():
                return False
                
            if not self.download_windows_exporter():
                return False
                
            if not self.start_docker_services():
                return False
                
            if not self.start_windows_exporter():
                return False
                
            self.show_final_info()
            
            # Start web portal (blocking)
            return self.start_web_portal()
            
        except KeyboardInterrupt:
            print("\n👋 Instalación cancelada por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error durante la instalación: {e}")
            return False

def main():
    installer = OptiMonInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()