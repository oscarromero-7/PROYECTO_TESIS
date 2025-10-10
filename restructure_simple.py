#!/usr/bin/env python3
"""
OptiMon Project Restructure Tool - Version Simple
Herramienta para reorganizar el proyecto OptiMon (compatible Windows)
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

class ProjectRestructure:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backup_dir = self.base_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def create_backup(self):
        """Crear backup de seguridad"""
        self.log("Creando backup de seguridad...")
        
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup de directorio principal
            src_dir = self.base_dir / "2-INICIAR-MONITOREO"
            if src_dir.exists():
                dst_dir = self.backup_dir / "2-INICIAR-MONITOREO"
                shutil.copytree(src_dir, dst_dir, ignore_errors=True)
                self.log("Backup completado")
                return True
            else:
                self.log("ERROR: Directorio 2-INICIAR-MONITOREO no encontrado")
                return False
                
        except Exception as e:
            self.log(f"ERROR creando backup: {e}")
            return False
    
    def create_new_structure(self):
        """Crear nueva estructura"""
        self.log("Creando nueva estructura...")
        
        try:
            # Crear directorios principales
            dirs = ['core', 'config', 'infrastructure', 'templates', 'tests', 'docs', 'tools']
            
            for dir_name in dirs:
                (self.base_dir / dir_name).mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = [
                'config/docker',
                'config/prometheus', 
                'config/grafana',
                'config/alertmanager',
                'config/email',
                'tests/integration',
                'tests/e2e',
                'infrastructure/terraform',
                'infrastructure/scripts',
                'tools/validators'
            ]
            
            for subdir in subdirs:
                (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            self.log("Estructura creada correctamente")
            return True
            
        except Exception as e:
            self.log(f"ERROR creando estructura: {e}")
            return False
    
    def migrate_core_files(self):
        """Migrar archivos principales"""
        self.log("Migrando archivos principales...")
        
        migrations = [
            ('2-INICIAR-MONITOREO/optimon_service_manager.py', 'core/optimon_manager.py'),
            ('2-INICIAR-MONITOREO/optimon_smtp_service.py', 'core/smtp_service.py'),
            ('2-INICIAR-MONITOREO/optimon_dashboard.py', 'core/web_dashboard.py'),
            ('2-INICIAR-MONITOREO/dashboard_manager.py', 'core/dashboard_manager.py'),
            ('2-INICIAR-MONITOREO/docker-compose.yml', 'config/docker/docker-compose.yml'),
        ]
        
        migrated = 0
        
        for src, dst in migrations:
            try:
                src_path = self.base_dir / src
                dst_path = self.base_dir / dst
                
                if src_path.exists():
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    self.log(f"Migrado: {src} -> {dst}")
                    migrated += 1
                else:
                    self.log(f"No encontrado: {src}")
                    
            except Exception as e:
                self.log(f"Error migrando {src}: {e}")
        
        self.log(f"Archivos migrados: {migrated}")
        return migrated > 0
    
    def migrate_configs(self):
        """Migrar configuraciones"""
        self.log("Migrando configuraciones...")
        
        try:
            # Migrar config de Prometheus
            src = self.base_dir / '2-INICIAR-MONITOREO/config/prometheus'
            dst = self.base_dir / 'config/prometheus'
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.log("Configuracion Prometheus migrada")
            
            # Migrar config de Grafana
            src = self.base_dir / '2-INICIAR-MONITOREO/config/grafana'
            dst = self.base_dir / 'config/grafana'
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.log("Configuracion Grafana migrada")
            
            # Migrar config de AlertManager
            src = self.base_dir / '2-INICIAR-MONITOREO/config/alertmanager'
            dst = self.base_dir / 'config/alertmanager'
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.log("Configuracion AlertManager migrada")
            
            return True
            
        except Exception as e:
            self.log(f"Error migrando configs: {e}")
            return False
    
    def migrate_templates(self):
        """Migrar templates"""
        self.log("Migrando templates...")
        
        try:
            src = self.base_dir / '2-INICIAR-MONITOREO/templates'
            dst = self.base_dir / 'templates'
            
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.log("Templates migrados")
                return True
            else:
                self.log("Templates no encontrados")
                return False
                
        except Exception as e:
            self.log(f"Error migrando templates: {e}")
            return False
    
    def migrate_tests(self):
        """Migrar archivos de test"""
        self.log("Migrando tests...")
        
        test_files = [
            ('2-INICIAR-MONITOREO/test_recipients.py', 'tests/integration/test_recipients.py'),
            ('2-INICIAR-MONITOREO/test_real_alert.py', 'tests/integration/test_real_alert.py'),
            ('2-INICIAR-MONITOREO/test_complete_system.py', 'tests/e2e/test_complete_system.py'),
        ]
        
        migrated = 0
        
        for src, dst in test_files:
            try:
                src_path = self.base_dir / src
                dst_path = self.base_dir / dst
                
                if src_path.exists():
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    self.log(f"Test migrado: {dst}")
                    migrated += 1
                    
            except Exception as e:
                self.log(f"Error migrando test {src}: {e}")
        
        self.log(f"Tests migrados: {migrated}")
        return migrated > 0
    
    def create_core_init(self):
        """Crear __init__.py para core"""
        try:
            init_file = self.base_dir / 'core' / '__init__.py'
            init_file.write_text('"""OptiMon Core Services"""\n', encoding='utf-8')
            self.log("Archivo core/__init__.py creado")
            return True
        except Exception as e:
            self.log(f"Error creando __init__.py: {e}")
            return False
    
    def create_requirements(self):
        """Crear requirements.txt"""
        try:
            requirements_content = """# OptiMon Dependencies
flask>=2.3.0
requests>=2.31.0
psutil>=5.9.0
schedule>=1.2.0
pyyaml>=6.0
docker>=6.1.0
prometheus-client>=0.17.0
"""
            requirements_file = self.base_dir / 'requirements.txt'
            requirements_file.write_text(requirements_content, encoding='utf-8')
            self.log("Archivo requirements.txt creado")
            return True
        except Exception as e:
            self.log(f"Error creando requirements.txt: {e}")
            return False
    
    def create_readme(self):
        """Crear README.md principal"""
        try:
            readme_content = """# OptiMon - Sistema de Monitoreo Automatizado

## Descripcion

OptiMon es un sistema completo de monitoreo de infraestructura que incluye:

- Monitoreo automatico de servidores Windows/Linux
- Sistema de alertas por email configurable  
- Dashboard web con interfaz moderna
- Gestion inteligente de dashboards segun infraestructura
- Servicios automatizados con recuperacion ante fallos

## Inicio Rapido

### Prerequisitos
- Python 3.8+
- Docker y Docker Compose
- Git

### Instalacion

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

- Dashboard OptiMon: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093

## Estructura del Proyecto

```
PROYECTO_TESIS/
├── core/                    # Servicios principales
├── config/                  # Configuraciones
├── infrastructure/          # Terraform/Ansible
├── templates/               # Templates web
├── tests/                   # Testing organizado
├── docs/                    # Documentacion
└── tools/                   # Herramientas
```

## Testing

```bash
# Tests unitarios
python -m pytest tests/unit/

# Tests de integracion  
python -m pytest tests/integration/

# Tests end-to-end
python -m pytest tests/e2e/
```

## Licencia

Este proyecto esta bajo la Licencia MIT.
"""
            readme_file = self.base_dir / 'README.md'
            readme_file.write_text(readme_content, encoding='utf-8')
            self.log("Archivo README.md creado")
            return True
        except Exception as e:
            self.log(f"Error creando README.md: {e}")
            return False
    
    def generate_summary(self):
        """Generar resumen"""
        try:
            summary = f"""
RESUMEN DE RESTRUCTURACION - OptiMon v2.0
================================================

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup: {self.backup_dir}

ESTRUCTURA CREADA:
- core/           (servicios principales)
- config/         (configuraciones)
- infrastructure/ (terraform/ansible)
- templates/      (templates web)
- tests/          (testing organizado)
- docs/           (documentacion)
- tools/          (herramientas)

ARCHIVOS MIGRADOS:
- Servicios principales movidos a core/
- Configuraciones organizadas en config/
- Tests organizados por tipo
- Templates centralizados

PROXIMOS PASOS:
1. Verificar servicios: docker ps
2. Probar dashboard: http://localhost:5000
3. Ejecutar tests: python -m pytest tests/
4. Hacer commit de cambios

RESTRUCTURACION COMPLETADA!
"""
            
            summary_file = self.base_dir / 'RESTRUCTURE_SUMMARY.md'
            summary_file.write_text(summary, encoding='utf-8')
            
            print(summary)
            self.log(f"Resumen guardado en: {summary_file}")
            return True
            
        except Exception as e:
            self.log(f"Error generando resumen: {e}")
            return False
    
    def run_restructure(self):
        """Ejecutar restructuracion completa"""
        self.log("INICIANDO RESTRUCTURACION DE PROYECTO OptiMon")
        self.log("="*50)
        
        try:
            # Ejecutar fases
            if not self.create_backup():
                self.log("Error en backup, abortando")
                return False
            
            if not self.create_new_structure():
                self.log("Error creando estructura")
                return False
            
            if not self.migrate_core_files():
                self.log("Error migrando archivos principales")
            
            if not self.migrate_configs():
                self.log("Error migrando configuraciones")
            
            if not self.migrate_templates():
                self.log("Error migrando templates")
            
            if not self.migrate_tests():
                self.log("Error migrando tests")
            
            if not self.create_core_init():
                self.log("Error creando __init__.py")
            
            if not self.create_requirements():
                self.log("Error creando requirements.txt")
            
            if not self.create_readme():
                self.log("Error creando README.md")
            
            self.generate_summary()
            
            self.log("="*50)
            self.log("RESTRUCTURACION COMPLETADA EXITOSAMENTE!")
            self.log("="*50)
            
            return True
            
        except Exception as e:
            self.log(f"Error critico: {e}")
            return False

def main():
    print("""
OptiMon Project Restructure Tool - Version Simple
==================================================

Este script reorganizara el proyecto OptiMon:
- Creara estructura profesional
- Migrara archivos principales
- Creara backup de seguridad

IMPORTANTE: Se creara backup automatico

Deseas continuar? (s/n): """, end="")
    
    response = input().lower().strip()
    
    if response not in ['s', 'si', 'y', 'yes']:
        print("Restructuracion cancelada")
        return 1
    
    restructure = ProjectRestructure()
    success = restructure.run_restructure()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())