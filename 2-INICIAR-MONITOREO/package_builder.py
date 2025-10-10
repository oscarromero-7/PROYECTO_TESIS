#!/usr/bin/env python3
"""
OPTIMON PACKAGE BUILDER
Prepara el sistema OptiMon para distribución en ZIP
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

class OptimomPackageBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.package_name = f"OptiMon-v1.0-{datetime.now().strftime('%Y%m%d')}"
        self.temp_dir = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_package_structure(self):
        """Crear estructura del paquete"""
        self.log("📁 Creando estructura del paquete...")
        
        # Crear directorio temporal
        self.temp_dir = Path(tempfile.mkdtemp(prefix='optimon_package_'))
        package_dir = self.temp_dir / self.package_name
        package_dir.mkdir(parents=True)
        
        # Archivos principales a incluir
        main_files = [
            'optimon_dashboard.py',
            'optimon_smtp_service.py',
            'optimon_auto_starter.py',
            'test_complete_system.py',
            'docker-compose.yml',
            'README.md'
        ]
        
        # Scripts de automatización
        batch_files = [
            'start_optimon_auto.bat',
            'stop_optimon.bat',
            'check_optimon_status.bat'
        ]
        
        # Copiar archivos principales
        for file_name in main_files:
            source = self.script_dir / file_name
            if source.exists():
                shutil.copy2(source, package_dir / file_name)
                self.log(f"✅ Copiado: {file_name}")
            else:
                self.log(f"⚠️ No encontrado: {file_name}", "WARNING")
                
        # Copiar scripts batch
        for file_name in batch_files:
            source = self.script_dir / file_name
            if source.exists():
                shutil.copy2(source, package_dir / file_name)
                self.log(f"✅ Copiado: {file_name}")
            else:
                self.log(f"⚠️ No encontrado: {file_name}", "WARNING")
                
        # Copiar directorios completos
        directories = ['config', 'templates']
        for dir_name in directories:
            source_dir = self.script_dir / dir_name
            if source_dir.exists():
                dest_dir = package_dir / dir_name
                shutil.copytree(source_dir, dest_dir)
                self.log(f"✅ Copiado directorio: {dir_name}")
            else:
                self.log(f"⚠️ No encontrado directorio: {dir_name}", "WARNING")
                
        return package_dir
        
    def create_installation_script(self, package_dir):
        """Crear script de instalación"""
        self.log("📜 Creando script de instalación...")
        
        install_script = '''@echo off
REM ======================================================
REM OPTIMON - INSTALADOR AUTOMATICO
REM ======================================================

echo.
echo ========================================
echo   OPTIMON - INSTALACION AUTOMATICA
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no esta instalado
    echo.
    echo Por favor instale Python 3.8+ desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python disponible

REM Verificar Docker
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker no esta instalado
    echo.
    echo Por favor instale Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker disponible

REM Instalar dependencias Python
echo.
echo 📦 Instalando dependencias Python...
pip install flask requests psutil

echo.
echo 🧪 Ejecutando pruebas del sistema...
python test_complete_system.py

echo.
echo ========================================
echo   OPTIMON INSTALADO CORRECTAMENTE
echo ========================================
echo.
echo Para iniciar OptiMon ejecute:
echo   start_optimon_auto.bat
echo.
echo Para mas informacion consulte:
echo   README.md
echo.
pause
'''
        
        with open(package_dir / 'install.bat', 'w', encoding='utf-8') as f:
            f.write(install_script)
            
        self.log("✅ Script de instalación creado")
        
    def create_requirements_file(self, package_dir):
        """Crear archivo de requerimientos"""
        self.log("📄 Creando archivo de requerimientos...")
        
        requirements = '''# OptiMon Python Requirements
flask>=2.0.0
requests>=2.25.0
psutil>=5.8.0
pathlib2>=2.3.0;python_version<"3.4"
'''
        
        with open(package_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
            
        self.log("✅ Archivo requirements.txt creado")
        
    def create_package_info(self, package_dir):
        """Crear información del paquete"""
        self.log("📋 Creando información del paquete...")
        
        package_info = {
            'name': 'OptiMon',
            'version': '1.0',
            'description': 'Sistema completo de monitoreo automatizado',
            'build_date': datetime.now().isoformat(),
            'components': {
                'prometheus': 'Recolección de métricas',
                'grafana': 'Visualización de datos',
                'alertmanager': 'Gestión de alertas',
                'dashboard': 'Panel de control web',
                'smtp_service': 'Servicio de emails'
            },
            'requirements': {
                'python': '>=3.8',
                'docker': 'Docker Desktop recomendado',
                'memory': '>=1GB disponible',
                'disk': '>=2GB disponible'
            },
            'ports': {
                'dashboard': 8080,
                'prometheus': 9090,
                'grafana': 3000,
                'alertmanager': 9093,
                'smtp': 5555
            }
        }
        
        with open(package_dir / 'package_info.json', 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, ensure_ascii=False)
            
        self.log("✅ Información del paquete creada")
        
    def create_quick_start_guide(self, package_dir):
        """Crear guía de inicio rápido"""
        self.log("📖 Creando guía de inicio rápido...")
        
        quick_start = '''# 🚀 OptiMon - Guía de Inicio Rápido

## ⚡ Instalación en 3 Pasos

### 1️⃣ Descomprimir
Extraer el archivo ZIP en el directorio deseado

### 2️⃣ Instalar (Opcional)
```batch
install.bat
```

### 3️⃣ Iniciar
```batch
start_optimon_auto.bat
```

## 🌐 Acceso Inmediato

- **Panel OptiMon**: http://localhost:8080
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

## 🔧 Requisitos Mínimos

- ✅ Windows 10/11 o Linux
- ✅ Python 3.8+
- ✅ Docker Desktop
- ✅ 1GB RAM disponible
- ✅ 2GB espacio en disco

## 🆘 Problemas Comunes

### Docker no inicia
- Instalar Docker Desktop
- Reiniciar sistema después de instalación

### Puerto ocupado
```batch
stop_optimon.bat
start_optimon_auto.bat
```

### Python no encontrado
- Instalar desde python.org
- Agregar a PATH del sistema

## 📞 Soporte

1. Ejecutar: `check_optimon_status.bat`
2. Revisar: `test_report.json`
3. Consultar: `README.md` completo

¡Listo para monitorear! 🎉
'''
        
        with open(package_dir / 'QUICK_START.md', 'w', encoding='utf-8') as f:
            f.write(quick_start)
            
        self.log("✅ Guía de inicio rápido creada")
        
    def create_zip_package(self, package_dir):
        """Crear archivo ZIP final"""
        self.log("📦 Creando archivo ZIP...")
        
        zip_path = self.script_dir / f"{self.package_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arc_path)
                    
        # Obtener tamaño del archivo
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        
        self.log(f"✅ Paquete creado: {zip_path.name} ({size_mb:.1f} MB)")
        return zip_path
        
    def cleanup(self):
        """Limpiar archivos temporales"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.log("🧹 Archivos temporales eliminados")
            
    def build_package(self):
        """Construir paquete completo"""
        self.log("🚀 INICIANDO CONSTRUCCION DEL PAQUETE OPTIMON")
        self.log("=" * 55)
        
        try:
            # 1. Crear estructura
            package_dir = self.create_package_structure()
            
            # 2. Crear archivos adicionales
            self.create_installation_script(package_dir)
            self.create_requirements_file(package_dir)
            self.create_package_info(package_dir)
            self.create_quick_start_guide(package_dir)
            
            # 3. Crear ZIP
            zip_path = self.create_zip_package(package_dir)
            
            # 4. Resumen final
            self.log("=" * 55)
            self.log("🎉 PAQUETE OPTIMON CREADO EXITOSAMENTE")
            self.log(f"📦 Archivo: {zip_path.name}")
            self.log(f"📍 Ubicación: {zip_path.absolute()}")
            self.log("")
            self.log("📋 Contenido del paquete:")
            self.log("  ✅ Aplicación completa OptiMon")
            self.log("  ✅ Scripts de automatización")
            self.log("  ✅ Configuraciones Docker")
            self.log("  ✅ Templates web")
            self.log("  ✅ Documentación completa")
            self.log("  ✅ Script de instalación")
            self.log("")
            self.log("🚀 Listo para distribuir!")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error construyendo paquete: {str(e)}", "ERROR")
            return False
            
        finally:
            self.cleanup()

def main():
    builder = OptimomPackageBuilder()
    success = builder.build_package()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())