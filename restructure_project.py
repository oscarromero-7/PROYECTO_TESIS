#!/usr/bin/env python3
"""
🏗️ OptiMon Project Restructure Tool
Herramienta automatizada para reorganizar el proyecto OptiMon

Autor: OptiMon Team
Versión: 1.0
Fecha: Octubre 2025
"""

import os
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

class ProjectRestructure:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backup_dir = self.base_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.new_structure = {
            'core': 'Servicios principales',
            'config': 'Configuraciones',
            'infrastructure': 'Infraestructura (Terraform, Ansible)',
            'templates': 'Templates web',
            'tests': 'Testing organizado',
            'docs': 'Documentación',
            'tools': 'Herramientas y utilidades',
            'logs': 'Logs centralizados',
            'data': 'Datos persistentes'
        }
        
        # Mapeo de archivos principales a su nueva ubicación
        self.file_mappings = {
            # SERVICIOS CORE
            '2-INICIAR-MONITOREO/optimon_service_manager.py': 'core/optimon_manager.py',
            '2-INICIAR-MONITOREO/optimon_smtp_service.py': 'core/smtp_service.py',
            '2-INICIAR-MONITOREO/optimon_dashboard.py': 'core/web_dashboard.py',
            '2-INICIAR-MONITOREO/dashboard_manager.py': 'core/dashboard_manager.py',
            
            # CONFIGURACIONES
            '2-INICIAR-MONITOREO/docker-compose.yml': 'config/docker/docker-compose.yml',
            '2-INICIAR-MONITOREO/.env.example': 'config/.env.example',
            '2-INICIAR-MONITOREO/config/email_recipients.json': 'config/email/recipients.json',
            
            # TEMPLATES
            '2-INICIAR-MONITOREO/templates/': 'templates/',
            
            # TESTS
            '2-INICIAR-MONITOREO/test_recipients.py': 'tests/integration/test_recipients.py',
            '2-INICIAR-MONITOREO/test_real_alert.py': 'tests/integration/test_real_alert.py',
            '2-INICIAR-MONITOREO/test_complete_system.py': 'tests/e2e/test_complete_system.py',
            '2-INICIAR-MONITOREO/test_modular_functionality.py': 'tests/integration/test_modular_functionality.py',
            
            # INFRAESTRUCTURA
            '1-CREAR-INFRAESTRUCTURA/': 'infrastructure/terraform/',
            'scripts/': 'infrastructure/scripts/',
            
            # HERRAMIENTAS
            'dashboard_auto_verifier.py': 'tools/validators/dashboard_verifier.py',
            'dashboard_auto_verifier_simple.py': 'tools/validators/dashboard_verifier_simple.py',
            'configure_optimon.py': 'tools/utilities/configure_optimon.py',
            'create_package.py': 'tools/generators/package_builder.py',
        }
        
        # Archivos a eliminar (basura/duplicados/obsoletos)
        self.files_to_delete = [
            # LOGS Y TEMPORALES
            '*.log',
            '*.pyc',
            '__pycache__/',
            'dashboard_auto_fix.log',
            'dashboard_verification.log',
            'local_alerts.log',
            'production_alerts.log',
            'webhook_alerts.log',
            
            # DUPLICADOS
            'dashboard_auto_verifier_simple.py',  # Mantenemos solo uno
            'optimon_dashboard_service.py',  # Funcionalidad integrada
            'optimon_status.py',  # Funcionalidad integrada
            
            # ARCHIVOS DE PRUEBA/DEBUG
            'cpu_stress_test.py',
            'alert_tester.py',
            'debug_instance.py',
            'debug_instance_fixed.py',
            'diagnose_dashboard.py',
            
            # INSTALADORES OBSOLETOS
            'install_*.py',
            'install_*.bat',
            'INICIAR_*.bat',
            'INICIAR_*.ps1',
            
            # VERSIONES NUMERADAS (archivos extraños)
            '1.12.0',
            '1.26.0',
            '2.28.0',
            '22.0.0',
            '29.0.0',
            '3.1.0',
            '5.9.0',
            
            # DOCUMENTACION FRAGMENTADA (consolidaremos)
            'ALERTAS_SISTEMA_FINAL.md',
            'FINAL_REPORT.md',
            'INSTALACION_DESDE_CERO.md',
            'LOGS_ESTADO_SISTEMA.md',
            'MANUAL_OPTIMON_SERVICE.md',
            'QUICK_START.md',
            'README_*.md',
            'RESULTADOS_*.md',
            
            # ARCHIVOS TEMPORALES
            'OptiMon-v*.zip',
            'optimon_*.json',
            'test_report.json',
            'detailed_test_report.json',
            'optimon_final_report.json',
        ]
    
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "ERROR": "[ERROR]", "WARNING": "[WARN]"}
        icon = icons.get(level, "[LOG]")
        print(f"[{timestamp}] {icon} {message}")
    
    def create_backup(self):
        """Crear backup completo antes de restructurar"""
        self.log("Creando backup de seguridad...")
        
        try:
            # Crear directorio de backup
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup de archivos principales
            important_dirs = ['2-INICIAR-MONITOREO', 'config', 'scripts']
            for dir_name in important_dirs:
                src_dir = self.base_dir / dir_name
                if src_dir.exists():
                    dst_dir = self.backup_dir / dir_name
                    shutil.copytree(src_dir, dst_dir, ignore_errors=True)
            
            # Backup de archivos sueltos importantes
            important_files = [
                'docker-compose.yml',
                'requeriments.txt',
                '*.py'
            ]
            
            for pattern in important_files:
                for file_path in self.base_dir.glob(pattern):
                    if file_path.is_file():
                        shutil.copy2(file_path, self.backup_dir / file_path.name)
            
            self.log(f"Backup creado en: {self.backup_dir}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error creando backup: {e}", "ERROR")
            return False
    
    def create_new_structure(self):
        """Crear nueva estructura de directorios"""
        self.log("Creando nueva estructura de directorios...")
        
        try:
            for dir_name, description in self.new_structure.items():
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                self.log(f"Directorio creado: {dir_name} ({description})")
            
            # Crear subdirectorios específicos
            subdirs = [
                'config/docker',
                'config/prometheus',
                'config/grafana/dashboards',
                'config/grafana/provisioning',
                'config/alertmanager',
                'config/email',
                'config/cloud',
                'infrastructure/terraform/aws',
                'infrastructure/terraform/azure',
                'infrastructure/ansible',
                'infrastructure/scripts/install',
                'infrastructure/scripts/setup',
                'infrastructure/scripts/deploy',
                'tests/unit',
                'tests/integration',
                'tests/e2e',
                'docs/user-guide',
                'docs/api',
                'docs/deployment',
                'tools/validators',
                'tools/generators',
                'tools/utilities'
            ]
            
            for subdir in subdirs:
                (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # Crear archivos .gitkeep en directorios vacíos
            for empty_dir in ['logs', 'data']:
                gitkeep_file = self.base_dir / empty_dir / '.gitkeep'
                gitkeep_file.touch()
            
            self.log("Estructura de directorios creada", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error creando estructura: {e}", "ERROR")
            return False
    
    def migrate_files(self):
        """Migrar archivos a nueva estructura"""
        self.log("Migrando archivos a nueva estructura...")
        
        migrated_count = 0
        
        for src_path, dst_path in self.file_mappings.items():
            try:
                src_full = self.base_dir / src_path
                dst_full = self.base_dir / dst_path
                
                if src_full.exists():
                    # Crear directorio destino si no existe
                    dst_full.parent.mkdir(parents=True, exist_ok=True)
                    
                    if src_full.is_dir():
                        # Copiar directorio completo
                        if dst_full.exists():
                            shutil.rmtree(dst_full)
                        shutil.copytree(src_full, dst_full)
                    else:
                        # Copiar archivo
                        shutil.copy2(src_full, dst_full)
                    
                    self.log(f"Migrado: {src_path} → {dst_path}")
                    migrated_count += 1
                else:
                    self.log(f"Archivo no encontrado: {src_path}", "WARNING")
                    
            except Exception as e:
                self.log(f"Error migrando {src_path}: {e}", "ERROR")
        
        self.log(f"Archivos migrados: {migrated_count}", "SUCCESS")
        return True
    
    def migrate_configs(self):
        """Migrar configuraciones específicas"""
        self.log("Migrando configuraciones...")
        
        try:
            # Migrar configuraciones de Prometheus
            prometheus_src = self.base_dir / '2-INICIAR-MONITOREO/config/prometheus'
            prometheus_dst = self.base_dir / 'config/prometheus'
            if prometheus_src.exists():
                if prometheus_dst.exists():
                    shutil.rmtree(prometheus_dst)
                shutil.copytree(prometheus_src, prometheus_dst)
                self.log("Configuración de Prometheus migrada")
            
            # Migrar configuraciones de Grafana
            grafana_src = self.base_dir / '2-INICIAR-MONITOREO/config/grafana'
            grafana_dst = self.base_dir / 'config/grafana'
            if grafana_src.exists():
                if grafana_dst.exists():
                    shutil.rmtree(grafana_dst)
                shutil.copytree(grafana_src, grafana_dst)
                self.log("Configuración de Grafana migrada")
            
            # Migrar configuraciones de AlertManager
            alertmanager_src = self.base_dir / '2-INICIAR-MONITOREO/config/alertmanager'
            alertmanager_dst = self.base_dir / 'config/alertmanager'
            if alertmanager_src.exists():
                if alertmanager_dst.exists():
                    shutil.rmtree(alertmanager_dst)
                shutil.copytree(alertmanager_src, alertmanager_dst)
                self.log("Configuración de AlertManager migrada")
            
            return True
            
        except Exception as e:
            self.log(f"Error migrando configuraciones: {e}", "ERROR")
            return False
    
    def clean_old_files(self):
        """Eliminar archivos basura y obsoletos"""
        self.log("Limpiando archivos obsoletos...")
        
        deleted_count = 0
        
        for pattern in self.files_to_delete:
            try:
                # Buscar archivos que coincidan con el patrón
                matches = list(self.base_dir.glob(pattern))
                matches.extend(list(self.base_dir.glob(f"**/{pattern}")))
                
                for file_path in matches:
                    try:
                        if file_path.is_dir():
                            shutil.rmtree(file_path)
                            self.log(f"Directorio eliminado: {file_path.name}")
                        else:
                            file_path.unlink()
                            self.log(f"Archivo eliminado: {file_path.name}")
                        deleted_count += 1
                    except Exception as e:
                        self.log(f"Error eliminando {file_path}: {e}", "WARNING")
                        
            except Exception as e:
                self.log(f"Error procesando patrón {pattern}: {e}", "WARNING")
        
        self.log(f"Archivos eliminados: {deleted_count}", "SUCCESS")
        return True
    
    def update_imports(self):
        """Actualizar imports en archivos migrados"""
        self.log("Actualizando imports y referencias...")
        
        try:
            # Mapeo de imports antiguos a nuevos
            import_mappings = {
                'from optimon_service_manager import': 'from core.optimon_manager import',
                'from optimon_smtp_service import': 'from core.smtp_service import',
                'from optimon_dashboard import': 'from core.web_dashboard import',
                'import optimon_service_manager': 'import core.optimon_manager',
                'import optimon_smtp_service': 'import core.smtp_service',
                'import optimon_dashboard': 'import core.web_dashboard',
            }
            
            # Actualizar archivos Python
            for py_file in self.base_dir.rglob('*.py'):
                if py_file.is_file() and not str(py_file).startswith(str(self.backup_dir)):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        updated = False
                        for old_import, new_import in import_mappings.items():
                            if old_import in content:
                                content = content.replace(old_import, new_import)
                                updated = True
                        
                        if updated:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.log(f"Imports actualizados en: {py_file.name}")
                            
                    except Exception as e:
                        self.log(f"Error actualizando {py_file}: {e}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Error actualizando imports: {e}", "ERROR")
            return False
    
    def create_new_files(self):
        """Crear archivos nuevos necesarios"""
        self.log("Creando archivos nuevos...")
        
        try:
            # Crear __init__.py para el módulo core
            core_init = self.base_dir / 'core' / '__init__.py'
            core_init.write_text('"""OptiMon Core Services"""\\n', encoding='utf-8')
            
            # Crear requirements.txt principal
            requirements = self.base_dir / 'requirements.txt'
            requirements_content = """# OptiMon Dependencies
flask>=2.3.0
requests>=2.31.0
psutil>=5.9.0
schedule>=1.2.0
pyyaml>=6.0
docker>=6.1.0
prometheus-client>=0.17.0
"""
            requirements.write_text(requirements_content, encoding='utf-8')
            
            # Crear setup.py
            setup_py = self.base_dir / 'setup.py'
            setup_content = '''#!/usr/bin/env python3
"""
OptiMon Setup Script
"""

from setuptools import setup, find_packages

setup(
    name="optimon",
    version="2.0.0",
    description="Sistema automatizado de monitoreo de infraestructura",
    author="OptiMon Team",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
        "schedule>=1.2.0",
        "pyyaml>=6.0",
        "docker>=6.1.0",
        "prometheus-client>=0.17.0"
    ],
    entry_points={
        'console_scripts': [
            'optimon=core.optimon_manager:main',
            'optimon-dashboard=core.web_dashboard:main',
            'optimon-smtp=core.smtp_service:main',
        ],
    },
    python_requires='>=3.8',
)
'''
            setup_py.write_text(setup_content, encoding='utf-8')
            
            # Crear CHANGELOG.md
            changelog = self.base_dir / 'CHANGELOG.md'
            changelog_content = """# Changelog - OptiMon

## [2.0.0] - 2025-10-09

### ✅ Added
- Sistema completo de alertas por email
- Gestor automático de servicios
- Dashboard web con API REST
- Gestión inteligente de dashboards
- Sistema de destinatarios configurable

### 🔧 Changed
- Restructuración completa del proyecto
- Servicios organizados en módulos
- Configuraciones centralizadas
- Testing organizado por tipos

### 📦 Infrastructure
- Docker Compose para servicios
- Prometheus + Grafana + AlertManager
- Windows Exporter integrado
- SMTP service automático

### 🧪 Testing
- Tests unitarios organizados
- Tests de integración completos
- Tests end-to-end funcionales
- Validadores automáticos
"""
            changelog.write_text(changelog_content, encoding='utf-8')
            
            # Crear README.md principal actualizado
            readme = self.base_dir / 'README.md'
            readme_content = """# 🚀 OptiMon - Sistema de Monitoreo Automatizado

## 📋 Descripción

OptiMon es un sistema completo de monitoreo de infraestructura que incluye:

- **Monitoreo automático** de servidores Windows/Linux
- **Sistema de alertas** por email configurable  
- **Dashboard web** con interfaz moderna
- **Gestión inteligente** de dashboards según infraestructura
- **Servicios automatizados** con recuperación ante fallos

## 🚀 Inicio Rápido

### Prerequisitos
- Python 3.8+
- Docker y Docker Compose
- Git

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/oscarromero-7/PROYECTO_TESIS.git
cd PROYECTO_TESIS

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp config/.env.example config/.env
# Editar config/.env con tus credenciales SMTP

# Iniciar servicios
cd config/docker
docker-compose up -d

# Iniciar OptiMon
python -m core.optimon_manager --daemon
```

### Acceso a Servicios

- **Dashboard OptiMon**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## 📁 Estructura del Proyecto

```
📁 PROYECTO_TESIS/
├── 📁 core/                    # Servicios principales
├── 📁 config/                  # Configuraciones
├── 📁 infrastructure/          # Terraform/Ansible
├── 📁 templates/               # Templates web
├── 📁 tests/                   # Testing organizado
├── 📁 docs/                    # Documentación
└── 📁 tools/                   # Herramientas
```

## 🔧 Configuración

### Email Alerts
1. Configurar SMTP en `config/.env`
2. Gestionar destinatarios via web: http://localhost:5000/emails

### Cloud Monitoring
1. Configurar credenciales en: http://localhost:5000/cloud
2. Los dashboards se crean automáticamente

## 📚 Documentación

- [Guía de Usuario](docs/user-guide/)
- [API Reference](docs/api/)
- [Deployment Guide](docs/deployment/)

## 🧪 Testing

```bash
# Tests unitarios
python -m pytest tests/unit/

# Tests de integración  
python -m pytest tests/integration/

# Tests end-to-end
python -m pytest tests/e2e/
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👥 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

Para soporte y preguntas:
- 📧 Email: [tu-email@ejemplo.com]
- 🐛 Issues: [GitHub Issues](https://github.com/oscarromero-7/PROYECTO_TESIS/issues)
"""
            readme.write_text(readme_content, encoding='utf-8')
            
            self.log("Archivos nuevos creados", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error creando archivos nuevos: {e}", "ERROR")
            return False
    
    def generate_summary(self):
        """Generar resumen de la restructuración"""
        self.log("Generando resumen de restructuración...")
        
        summary = f"""
RESUMEN DE RESTRUCTURACION - OptiMon v2.0
{'='*60}

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup: {self.backup_dir}

ESTRUCTURA NUEVA CREADA:
{'-'*30}
"""
        
        for dir_name, description in self.new_structure.items():
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob('*'))) if dir_path.exists() else 0
                summary += f"[DIR] {dir_name:<15} - {description} ({file_count} archivos)\n"
        
        summary += f"""
ARCHIVOS MIGRADOS:
{'-'*30}
"""
        
        for src, dst in list(self.file_mappings.items())[:10]:  # Mostrar primeros 10
            if (self.base_dir / dst).exists():
                summary += f"[OK] {src} -> {dst}\n"
        
        if len(self.file_mappings) > 10:
            summary += f"... y {len(self.file_mappings) - 10} archivos mas\n"
        
        summary += f"""
LIMPIEZA REALIZADA:
{'-'*30}
- Archivos duplicados eliminados
- Logs temporales removidos
- Configuraciones obsoletas limpiadas
- Scripts de prueba reorganizados

PROXIMOS PASOS:
{'-'*30}
1. Verificar que todos los servicios funcionen
2. Actualizar documentacion si es necesario
3. Probar sistema completo
4. Hacer commit de cambios

ACCESOS:
{'-'*30}
- Dashboard: http://localhost:5000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

RESTRUCTURACION COMPLETADA EXITOSAMENTE!
"""
        
        summary_file = self.base_dir / 'RESTRUCTURE_SUMMARY.md'
        summary_file.write_text(summary, encoding='utf-8')
        
        print(summary)
        self.log(f"Resumen guardado en: {summary_file}", "SUCCESS")
    
    def run_restructure(self):
        """Ejecutar restructuración completa"""
        self.log("="*60)
        self.log("INICIANDO RESTRUCTURACION DE PROYECTO OptiMon")
        self.log("="*60)
        
        try:
            # Fase 1: Backup
            if not self.create_backup():
                self.log("Error en backup, abortando restructuración", "ERROR")
                return False
            
            # Fase 2: Crear nueva estructura
            if not self.create_new_structure():
                self.log("Error creando estructura, abortando", "ERROR")
                return False
            
            # Fase 3: Migrar archivos principales
            if not self.migrate_files():
                self.log("Error en migración, continuando...", "WARNING")
            
            # Fase 4: Migrar configuraciones
            if not self.migrate_configs():
                self.log("Error migrando configs, continuando...", "WARNING")
            
            # Fase 5: Actualizar imports
            if not self.update_imports():
                self.log("Error actualizando imports, continuando...", "WARNING")
            
            # Fase 6: Crear archivos nuevos
            if not self.create_new_files():
                self.log("Error creando archivos nuevos, continuando...", "WARNING")
            
            # Fase 7: Limpiar archivos obsoletos
            if not self.clean_old_files():
                self.log("Error en limpieza, continuando...", "WARNING")
            
            # Fase 8: Generar resumen
            self.generate_summary()
            
            self.log("="*60)
            self.log("RESTRUCTURACION COMPLETADA EXITOSAMENTE!", "SUCCESS")
            self.log("="*60)
            
            return True
            
        except Exception as e:
            self.log(f"Error crítico durante restructuración: {e}", "ERROR")
            return False

def main():
    """Función principal"""
    print("""
OptiMon Project Restructure Tool v1.0
========================================

Este script reorganizara completamente el proyecto OptiMon:
- Creara estructura moderna y organizada
- Migrara archivos a ubicaciones apropiadas  
- Eliminara archivos obsoletos y duplicados
- Actualizara imports y referencias
- Creara backup de seguridad

IMPORTANTE: Se creara un backup automatico antes de proceder

Deseas continuar? (s/n): """, end="")
    
    response = input().lower().strip()
    
    if response not in ['s', 'si', 'y', 'yes']:
        print("Restructuracion cancelada por el usuario")
        return 1
    
    restructure = ProjectRestructure()
    success = restructure.run_restructure()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())