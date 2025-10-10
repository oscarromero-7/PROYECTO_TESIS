#!/usr/bin/env python3
"""
🧹 OPTIMON - SCRIPT DE LIMPIEZA Y EMPAQUETADO
=============================================

Este script limpia el proyecto y crea un ZIP listo para distribución:
- Elimina archivos temporales y logs
- Elimina Windows Exporter instalado
- Mantiene credenciales SMTP pero limpia destinatarios
- Crea ZIP con estructura completa y limpia

Autor: OptiMon Team
Versión: 1.0
Fecha: Octubre 2025
"""

import os
import shutil
import zipfile
import json
from pathlib import Path
import subprocess
import sys

class OptiMonCleaner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.project_name = "OptiMon-v2.0-Clean"
        self.zip_name = f"{self.project_name}-{self.get_date()}.zip"
        
    def get_date(self):
        """Obtener fecha actual para el nombre del ZIP"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d")
    
    def log(self, message, level="INFO"):
        """Log con formato"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "📝")
        print(f"{icon} {message}")
    
    def stop_optimon_processes(self):
        """Detener todos los procesos de OptiMon"""
        self.log("Deteniendo procesos de OptiMon...")
        
        processes_to_kill = [
            "windows_exporter.exe",
            "python.exe"  # Solo los que contienen optimon
        ]
        
        try:
            # Obtener lista de procesos Python que contienen 'optimon'
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip() and 'python.exe' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            # Verificar si es proceso OptiMon
                            try:
                                cmd_result = subprocess.run(
                                    ['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/format:csv'],
                                    capture_output=True, text=True
                                )
                                if 'optimon' in cmd_result.stdout.lower():
                                    subprocess.run(['taskkill', '/PID', pid, '/F'], check=False)
                                    self.log(f"Proceso OptiMon terminado: PID {pid}")
                            except:
                                pass
            
            # Terminar Windows Exporter específicamente
            subprocess.run(['taskkill', '/IM', 'windows_exporter.exe', '/F'], check=False)
            
        except Exception as e:
            self.log(f"Error deteniendo procesos: {e}", "WARNING")
    
    def remove_windows_exporter(self):
        """Eliminar Windows Exporter del sistema"""
        self.log("Eliminando Windows Exporter del sistema...")
        
        paths_to_remove = [
            Path("C:/optimon"),
            Path("C:/Program Files/windows_exporter"),
            Path("C:/Windows/System32/windows_exporter.exe")
        ]
        
        for path in paths_to_remove:
            if path.exists():
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                    self.log(f"Eliminado: {path}")
                except Exception as e:
                    self.log(f"No se pudo eliminar {path}: {e}", "WARNING")
    
    def clean_email_recipients(self):
        """Limpiar destinatarios de email manteniendo estructura"""
        self.log("Limpiando destinatarios de email...")
        
        recipients_files = [
            self.project_root / "2-INICIAR-MONITOREO/config/optimon/email_recipients.json",
            self.project_root / "config/optimon/email_recipients.json"
        ]
        
        clean_config = {
            "recipients": [
                {
                    "email": "admin@ejemplo.com",
                    "name": "Administrador",
                    "active": true,
                    "added_date": "2025-10-09T00:00:00.000000"
                }
            ],
            "default_recipient": "admin@ejemplo.com"
        }
        
        for file_path in recipients_files:
            if file_path.exists():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(clean_config, f, indent=2, ensure_ascii=False)
                    self.log(f"Destinatarios limpiados en: {file_path}")
                except Exception as e:
                    self.log(f"Error limpiando {file_path}: {e}", "WARNING")
    
    def clean_temporary_files(self):
        """Eliminar archivos temporales y logs"""
        self.log("Limpiando archivos temporales...")
        
        patterns_to_remove = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.log",
            "**/logs/*",
            "**/.pytest_cache",
            "**/node_modules",
            "**/*.tmp",
            "**/temp/*"
        ]
        
        for pattern in patterns_to_remove:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    self.log(f"Eliminado: {path.name}")
                except Exception as e:
                    self.log(f"No se pudo eliminar {path}: {e}", "WARNING")
    
    def create_clean_zip(self):
        """Crear ZIP con proyecto limpio"""
        self.log("Creando ZIP del proyecto limpio...")
        
        # Crear directorio temporal para el ZIP
        temp_dir = Path("temp_optimon")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        temp_dir.mkdir()
        
        # Copiar estructura principal
        folders_to_include = [
            "1-CREAR-INFRAESTRUCTURA",
            "2-INICIAR-MONITOREO", 
            "docker",
            "grafana",
            "prometheus",
            "scripts"
        ]
        
        files_to_include = [
            "*.py",
            "*.txt", 
            "*.md",
            "*.bat",
            "*.sh"
        ]
        
        # Copiar carpetas
        for folder in folders_to_include:
            src_folder = self.project_root / folder
            if src_folder.exists():
                dst_folder = temp_dir / self.project_name / folder
                shutil.copytree(src_folder, dst_folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.log'))
                self.log(f"Copiado: {folder}")
        
        # Copiar archivos individuales de la raíz
        for pattern in files_to_include:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    dst_file = temp_dir / self.project_name / file_path.name
                    shutil.copy2(file_path, dst_file)
                    self.log(f"Copiado: {file_path.name}")
        
        # Crear README de instalación
        readme_content = self.create_installation_readme()
        readme_path = temp_dir / self.project_name / "INSTALACION.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Crear ZIP
        zip_path = self.project_root / self.zip_name
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Limpiar directorio temporal
        shutil.rmtree(temp_dir)
        
        self.log(f"ZIP creado: {zip_path}", "SUCCESS")
        return zip_path
    
    def create_installation_readme(self):
        """Crear README con instrucciones de instalación"""
        return '''# 🎯 OPTIMON v2.0 - INSTALACIÓN LIMPIA

## 📋 Requisitos Previos
- Python 3.8+ instalado
- Docker Desktop instalado y ejecutándose  
- Puerto 3000, 5000, 5555, 9090, 9093, 9182 disponibles

## 🚀 Instalación Rápida

### 1. Extraer archivos
Extraer todos los archivos en un directorio de tu elección.

### 2. Configurar credenciales SMTP (OBLIGATORIO)
Editar el archivo: `2-INICIAR-MONITOREO/optimon_smtp_service.py`
```python
# Líneas 45-50 aproximadamente
SMTP_USERNAME = 'tu_email@gmail.com'
SMTP_PASSWORD = 'tu_app_password'  # App Password de Gmail
```

### 3. Configurar destinatarios de alertas
Editar: `2-INICIAR-MONITOREO/config/optimon/email_recipients.json`
```json
{
  "recipients": [
    {
      "email": "admin@tuempresa.com",
      "name": "Administrador",
      "active": true,
      "added_date": "2025-10-09T00:00:00.000000"
    }
  ]
}
```

### 4. Ejecutar sistema completo
```bash
cd 2-INICIAR-MONITOREO
python start_optimon_complete.py
```

## 🌐 Interfaces Disponibles
- **Dashboard OptiMon**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## 🔧 Características
- ✅ Instalación automática de Windows Exporter
- ✅ Configuración automática de Prometheus
- ✅ Dashboard web completo
- ✅ Sistema de alertas por email
- ✅ Ejecución en segundo plano

## 📧 Soporte
Para dudas o problemas, revisar logs en la consola durante la instalación.

---
**OptiMon v2.0** - Sistema de Monitoreo Completo para Windows
'''
    
    def verify_system_stopped(self):
        """Verificar que todos los servicios están detenidos"""
        self.log("Verificando que el sistema esté detenido...")
        
        ports_to_check = [5000, 5555, 9182]
        
        for port in ports_to_check:
            try:
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout.strip():
                    self.log(f"Puerto {port} aún en uso", "WARNING")
                else:
                    self.log(f"Puerto {port} liberado")
            except:
                pass
    
    def run_complete_cleanup(self):
        """Ejecutar limpieza completa"""
        self.log("=" * 60)
        self.log("🧹 INICIANDO LIMPIEZA COMPLETA DE OPTIMON")
        self.log("=" * 60)
        
        steps = [
            ("Detener procesos", self.stop_optimon_processes),
            ("Eliminar Windows Exporter", self.remove_windows_exporter),
            ("Limpiar destinatarios", self.clean_email_recipients),
            ("Limpiar archivos temporales", self.clean_temporary_files),
            ("Verificar sistema detenido", self.verify_system_stopped),
            ("Crear ZIP limpio", self.create_clean_zip)
        ]
        
        for step_name, step_func in steps:
            self.log(f"Ejecutando: {step_name}")
            try:
                result = step_func()
                if step_name == "Crear ZIP limpio" and result:
                    zip_path = result
            except Exception as e:
                self.log(f"Error en {step_name}: {e}", "ERROR")
        
        self.log("=" * 60) 
        self.log("🎉 LIMPIEZA COMPLETA FINALIZADA", "SUCCESS")
        self.log(f"📦 ZIP creado: {getattr(self, 'zip_name', 'OptiMon-Clean.zip')}")
        self.log("=" * 60)
        self.log("💡 El ZIP está listo para distribución con:")
        self.log("  ✅ Sistema completamente limpio")
        self.log("  ✅ Sin Windows Exporter instalado")
        self.log("  ✅ Credenciales SMTP mantenidas")
        self.log("  ✅ Destinatarios limpiados")
        self.log("  ✅ Documentación incluida")

def main():
    """Función principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🧹 OPTIMON - LIMPIEZA Y EMPAQUETADO          ║
║                                                              ║
║  Este script realizará:                                      ║
║  • Detener todos los procesos OptiMon                       ║
║  • Eliminar Windows Exporter del sistema                    ║
║  • Limpiar destinatarios de email                           ║
║  • Crear ZIP limpio para distribución                       ║
║                                                              ║
║  ⚠️  MANTIENE: Credenciales SMTP para envío               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    response = input("¿Continuar con la limpieza? (s/N): ")
    if response.lower() not in ['s', 'si', 'y', 'yes']:
        print("❌ Operación cancelada")
        return 1
    
    cleaner = OptiMonCleaner()
    try:
        cleaner.run_complete_cleanup()
        return 0
    except KeyboardInterrupt:
        print("\n⏹️ Proceso interrumpido por el usuario")
        return 130
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1

if __name__ == "__main__":
    exit(main())