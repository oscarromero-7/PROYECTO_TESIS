#!/usr/bin/env python3
"""
Generador de Paquete de Distribución OptiMon
Crea un ZIP con todos los archivos necesarios para distribución
"""

import os
import zipfile
import shutil
import json
from pathlib import Path
from datetime import datetime

class DistributionPackageCreator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.version = "2.0.0"
        self.package_name = f"OptiMon-v{self.version}-{datetime.now().strftime('%Y%m%d')}"
        self.temp_dir = self.base_dir / "temp_package"
        self.zip_file = self.base_dir / f"{self.package_name}.zip"
        
        # Archivos esenciales para distribución
        self.essential_files = [
            # SERVICIOS CORE
            "2-INICIAR-MONITOREO/optimon_service_manager.py",
            "2-INICIAR-MONITOREO/optimon_smtp_service.py",
            "2-INICIAR-MONITOREO/optimon_dashboard.py",
            "2-INICIAR-MONITOREO/dashboard_manager.py",
            
            # DOCKER Y CONFIGURACION
            "2-INICIAR-MONITOREO/docker-compose.yml",
            "2-INICIAR-MONITOREO/.env",
            
            # TESTS FUNCIONALES
            "2-INICIAR-MONITOREO/test_recipients.py",
            "2-INICIAR-MONITOREO/test_real_alert.py",
            "2-INICIAR-MONITOREO/test_complete_system.py",
            
            # DEPENDENCIAS
            "requeriments.txt",
            
            # UTILIDADES
            "dashboard_auto_verifier.py",
            "configure_optimon.py",
            "node_exporter_installer.py",
        ]
        
        # Directorios completos a incluir
        self.essential_dirs = [
            "2-INICIAR-MONITOREO/config",
            "2-INICIAR-MONITOREO/templates",
            "1-CREAR-INFRAESTRUCTURA",
            "scripts",
        ]
    
    def log(self, message):
        """Log simple"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def create_temp_directory(self):
        """Crear directorio temporal para el paquete"""
        self.log("Creando directorio temporal...")
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        self.temp_dir.mkdir()
        
        # Crear estructura básica
        (self.temp_dir / "optimon").mkdir()
        (self.temp_dir / "config").mkdir()
        (self.temp_dir / "infrastructure").mkdir()
        (self.temp_dir / "scripts").mkdir()
        (self.temp_dir / "tests").mkdir()
        (self.temp_dir / "docs").mkdir()
        
        return True
    
    def copy_essential_files(self):
        """Copiar archivos esenciales"""
        self.log("Copiando archivos esenciales...")
        
        copied_count = 0
        
        # Copiar archivos individuales
        for file_path in self.essential_files:
            src = self.base_dir / file_path
            if src.exists():
                # Determinar destino según el tipo de archivo
                if file_path.startswith("2-INICIAR-MONITOREO/"):
                    dst = self.temp_dir / "optimon" / src.name
                elif file_path.startswith("scripts/"):
                    dst = self.temp_dir / "scripts" / src.name
                elif file_path.endswith("test_"):
                    dst = self.temp_dir / "tests" / src.name
                else:
                    dst = self.temp_dir / src.name
                
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied_count += 1
                self.log(f"  Copiado: {file_path}")
            else:
                self.log(f"  FALTANTE: {file_path}")
        
        # Copiar directorios completos
        for dir_path in self.essential_dirs:
            src_dir = self.base_dir / dir_path
            if src_dir.exists():
                if dir_path.startswith("2-INICIAR-MONITOREO/"):
                    dst_dir = self.temp_dir / "config" / src_dir.name
                elif dir_path.startswith("1-CREAR-INFRAESTRUCTURA"):
                    dst_dir = self.temp_dir / "infrastructure" / "terraform"
                else:
                    dst_dir = self.temp_dir / src_dir.name
                
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                self.log(f"  Directorio copiado: {dir_path}")
        
        self.log(f"Archivos copiados: {copied_count}")
        return True
    
    def create_installation_script(self):
        """Crear script de instalación"""
        self.log("Creando script de instalación...")
        
        # Script para Windows
        install_bat = self.temp_dir / "INSTALL.bat"
        install_bat_content = """@echo off
echo ===============================================
echo OptiMon v2.0 - Instalacion Automatica
echo ===============================================

echo.
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.8+ primero.
    pause
    exit /b 1
)

echo.
echo Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no encontrado. Instala Docker primero.
    pause
    exit /b 1
)

echo.
echo Instalando dependencias Python...
pip install -r requirements.txt

echo.
echo Verificando configuraciones...
if not exist "config\\email\\recipients.json" (
    copy "config\\email\\recipients.example.json" "config\\email\\recipients.json"
)

echo IMPORTANTE: El archivo .env ya incluye credenciales SMTP funcionales
echo Si necesitas cambiar las credenciales, edita el archivo .env

echo.
echo Iniciando servicios Docker...
cd config\\docker
docker-compose up -d
cd ..\\..

echo.
echo ===============================================
echo INSTALACION COMPLETADA!
echo ===============================================
echo.
echo Servicios disponibles:
echo - Dashboard OptiMon: http://localhost:5000
echo - Grafana: http://localhost:3000 (admin/admin)
echo - Prometheus: http://localhost:9090
echo - AlertManager: http://localhost:9093
echo.
echo Para iniciar OptiMon:
echo   python optimon\\optimon_service_manager.py --daemon
echo.
echo Para ejecutar tests:
echo   python tests\\test_complete_system.py
echo.
pause
"""
        install_bat.write_text(install_bat_content, encoding='utf-8')
        
        # Script para Linux/Mac
        install_sh = self.temp_dir / "install.sh"
        install_sh_content = """#!/bin/bash

echo "==============================================="
echo "OptiMon v2.0 - Instalación Automática"
echo "==============================================="

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no encontrado. Instala Python 3.8+ primero."
    exit 1
fi

# Verificar Docker
echo "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no encontrado. Instala Docker primero."
    exit 1
fi

# Instalar dependencias
echo "Instalando dependencias Python..."
pip3 install -r requirements.txt

# Copiar configuraciones
echo "Verificando configuraciones..."
if [ ! -f "config/email/recipients.json" ]; then
    cp "config/email/recipients.example.json" "config/email/recipients.json"
fi

echo "IMPORTANTE: El archivo .env ya incluye credenciales SMTP funcionales"
echo "Si necesitas cambiar las credenciales, edita el archivo .env"

# Hacer ejecutables
chmod +x optimon/*.py
chmod +x tests/*.py

# Iniciar servicios Docker
echo "Iniciando servicios Docker..."
cd config/docker
docker-compose up -d
cd ../..

echo "==============================================="
echo "INSTALACIÓN COMPLETADA!"
echo "==============================================="
echo ""
echo "Servicios disponibles:"
echo "- Dashboard OptiMon: http://localhost:5000"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- Prometheus: http://localhost:9090"
echo "- AlertManager: http://localhost:9093"
echo ""
echo "Para iniciar OptiMon:"
echo "  python3 optimon/optimon_service_manager.py --daemon"
echo ""
echo "Para ejecutar tests:"
echo "  python3 tests/test_complete_system.py"
echo ""
"""
        install_sh.write_text(install_sh_content, encoding='utf-8')
        
        return True
    
    def create_documentation(self):
        """Crear documentación de distribución"""
        self.log("Creando documentación...")
        
        # README principal
        readme = self.temp_dir / "README.md"
        readme_content = f"""# OptiMon v{self.version} - Sistema de Monitoreo Automatizado

## Descripción

OptiMon es un sistema completo de monitoreo de infraestructura que incluye:

- **Monitoreo automático** de servidores Windows/Linux
- **Sistema de alertas** por email configurable  
- **Dashboard web** con interfaz moderna
- **Gestión inteligente** de dashboards según infraestructura
- **Servicios automatizados** con recuperación ante fallos

## Instalación Rápida

### Windows
```cmd
INSTALL.bat
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

### Instalación Manual

1. **Prerequisitos**
   - Python 3.8+
   - Docker y Docker Compose
   - Git (opcional)

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno (OPCIONAL)**
   ```bash
   # Las credenciales SMTP ya están configuradas
   # Si necesitas cambiarlas, edita .env
   ```

4. **Iniciar servicios Docker**
   ```bash
   cd config/docker
   docker-compose up -d
   cd ../..
   ```

5. **Iniciar OptiMon**
   ```bash
   python optimon/optimon_service_manager.py --daemon
   ```

## Acceso a Servicios

Una vez instalado, accede a:

- **Dashboard OptiMon**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## Configuración

**¡SMTP ya configurado!** El sistema incluye credenciales SMTP funcionales.

### 1. Gestionar Destinatarios de Alertas (REQUERIDO)

Via web: http://localhost:5000/emails

O edita manualmente: `config/email/recipients.json`

### 2. Cambiar Email SMTP (OPCIONAL)

Si necesitas usar tu propio email, edita el archivo `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-password-app
```

### 3. Monitoreo de Nube (Opcional)

Configura credenciales via web: http://localhost:5000/cloud

Los dashboards se crearán automáticamente.

## Testing

```bash
# Test completo del sistema
python tests/test_complete_system.py

# Test de destinatarios de email
python tests/test_recipients.py

# Test de alertas reales
python tests/test_real_alert.py
```

## Estructura del Paquete

```
OptiMon-v{self.version}/
├── optimon/                    # Servicios principales
├── config/                     # Configuraciones
├── infrastructure/             # Terraform (opcional)
├── scripts/                    # Scripts de utilidad
├── tests/                      # Tests del sistema
├── docs/                       # Documentación
├── INSTALL.bat                 # Instalador Windows
├── install.sh                  # Instalador Linux/Mac
└── README.md                   # Esta documentación
```

## Soporte

Para soporte y preguntas:
- GitHub: https://github.com/oscarromero-7/PROYECTO_TESIS
- Documentación: Ver directorio `docs/`

## Licencia

Este proyecto está bajo la Licencia MIT.
"""
        readme.write_text(readme_content, encoding='utf-8')
        
        # Guía de configuración
        config_guide = self.temp_dir / "docs" / "CONFIGURATION.md"
        config_guide.parent.mkdir(exist_ok=True)
        config_guide_content = """# Guía de Configuración OptiMon

## Configuración SMTP

### Gmail
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=tu-email@gmail.com
```

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@outlook.com
SMTP_PASSWORD=tu-password
SMTP_FROM_EMAIL=tu-email@outlook.com
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@yahoo.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=tu-email@yahoo.com
```

## Configuración de Alertas

### Destinatarios
Edita `config/email/recipients.json`:
```json
[
    {
        "name": "Admin Principal",
        "email": "admin@empresa.com",
        "alerts": ["critical", "warning"],
        "active": true
    },
    {
        "name": "Equipo DevOps",
        "email": "devops@empresa.com", 
        "alerts": ["critical"],
        "active": true
    }
]
```

### Umbrales de Alertas
Edita `config/prometheus/alert_rules.yml`:
```yaml
- alert: HighCPUUsage
  expr: cpu_usage > 80
  for: 5m
  
- alert: HighMemoryUsage
  expr: memory_usage > 90
  for: 3m
```

## Configuración de Infraestructura

### AWS (Opcional)
```env
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_REGION=us-east-1
```

### Azure (Opcional)
```env
AZURE_CLIENT_ID=tu-client-id
AZURE_CLIENT_SECRET=tu-client-secret
AZURE_TENANT_ID=tu-tenant-id
AZURE_SUBSCRIPTION_ID=tu-subscription-id
```
"""
        config_guide.write_text(config_guide_content, encoding='utf-8')
        
        return True
    
    def create_requirements_file(self):
        """Crear archivo requirements.txt optimizado"""
        self.log("Creando requirements.txt...")
        
        requirements = self.temp_dir / "requirements.txt"
        requirements_content = """# OptiMon v2.0 Dependencies
# Core dependencies
flask>=2.3.0
requests>=2.31.0
psutil>=5.9.0
schedule>=1.2.0
pyyaml>=6.0

# Monitoring and metrics
prometheus-client>=0.17.0

# Infrastructure (optional)
docker>=6.1.0
boto3>=1.26.0
azure-mgmt-compute>=30.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Email - smtplib viene incluido en Python, no necesita instalación

# Utilities
python-dotenv>=1.0.0
colorama>=0.4.6
"""
        requirements.write_text(requirements_content, encoding='utf-8')
        
        return True
    
    def create_env_example(self):
        """Crear archivo .env.example"""
        self.log("Creando .env.example...")
        
        env_example = self.temp_dir / ".env.example"
        env_example_content = """# OptiMon Configuration - EXAMPLE FILE

# SMTP Configuration (Required for email alerts)
# El archivo .env ya incluye credenciales funcionales
# Este es solo un archivo de ejemplo para referencia

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_TIMEOUT=30

# Configuración del remitente
EMAIL_FROM_NAME=OptiMon Alerts
EMAIL_FROM_DISPLAY=Sistema de Monitoreo OptiMon

# OptiMon Service Configuration
OPTIMON_HOST=0.0.0.0
OPTIMON_PORT=5000
OPTIMON_DEBUG=false

# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090

# AlertManager Configuration
ALERTMANAGER_URL=http://localhost:9093

# Cloud Credentials (Optional - for cloud monitoring)
# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Azure
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/optimon.log
"""
        env_example.write_text(env_example_content, encoding='utf-8')
        
        return True
    
    def create_recipients_example(self):
        """Crear archivo de ejemplo para recipients"""
        self.log("Creando recipients.example.json...")
        
        recipients_dir = self.temp_dir / "config" / "email"
        recipients_dir.mkdir(parents=True, exist_ok=True)
        
        recipients_example = recipients_dir / "recipients.example.json"
        recipients_example_content = """[
    {
        "name": "Administrador Principal",
        "email": "admin@empresa.com",
        "alerts": ["critical", "warning", "info"],
        "active": true
    },
    {
        "name": "Equipo DevOps",
        "email": "devops@empresa.com",
        "alerts": ["critical", "warning"],
        "active": true
    },
    {
        "name": "Gerente TI",
        "email": "gerente@empresa.com",
        "alerts": ["critical"],
        "active": true
    }
]"""
        recipients_example.write_text(recipients_example_content, encoding='utf-8')
        
        return True
    
    def create_zip_package(self):
        """Crear archivo ZIP final"""
        self.log("Creando paquete ZIP...")
        
        if self.zip_file.exists():
            self.zip_file.unlink()
        
        with zipfile.ZipFile(self.zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.temp_dir.rglob('*'):
                if file_path.is_file():
                    # Crear ruta relativa dentro del ZIP
                    arcname = self.package_name + "/" + str(file_path.relative_to(self.temp_dir))
                    zipf.write(file_path, arcname)
        
        # Limpiar directorio temporal
        shutil.rmtree(self.temp_dir)
        
        return True
    
    def generate_distribution_info(self):
        """Generar información de distribución"""
        self.log("Generando información de distribución...")
        
        info = {
            "package_name": self.package_name,
            "version": self.version,
            "created": datetime.now().isoformat(),
            "files_included": len(self.essential_files) + len(self.essential_dirs),
            "zip_size_mb": round(self.zip_file.stat().st_size / (1024*1024), 2),
            "install_commands": {
                "windows": "INSTALL.bat",
                "linux_mac": "./install.sh"
            },
            "services": {
                "optimon_dashboard": "http://localhost:5000",
                "grafana": "http://localhost:3000",
                "prometheus": "http://localhost:9090",
                "alertmanager": "http://localhost:9093"
            }
        }
        
        info_file = self.base_dir / f"{self.package_name}_INFO.json"
        info_file.write_text(json.dumps(info, indent=2), encoding='utf-8')
        
        return info
    
    def create_distribution_package(self):
        """Crear paquete completo de distribución"""
        self.log("="*50)
        self.log("CREANDO PAQUETE DE DISTRIBUCIÓN OptiMon")
        self.log("="*50)
        
        try:
            # Crear directorio temporal
            if not self.create_temp_directory():
                return False
            
            # Copiar archivos esenciales
            if not self.copy_essential_files():
                return False
            
            # Crear scripts de instalación
            if not self.create_installation_script():
                return False
            
            # Crear documentación
            if not self.create_documentation():
                return False
            
            # Crear archivos de configuración
            if not self.create_requirements_file():
                return False
            
            if not self.create_env_example():
                return False
            
            if not self.create_recipients_example():
                return False
            
            # Crear ZIP final
            if not self.create_zip_package():
                return False
            
            # Generar información
            info = self.generate_distribution_info()
            
            self.log("="*50)
            self.log("PAQUETE CREADO EXITOSAMENTE!")
            self.log("="*50)
            
            print(f"""
INFORMACIÓN DEL PAQUETE:
========================
Archivo: {self.zip_file.name}
Tamaño: {info['zip_size_mb']} MB
Versión: {info['version']}
Archivos incluidos: {info['files_included']}

CONTENIDO INCLUIDO:
===================
✓ Servicios OptiMon (optimon_service_manager, smtp_service, dashboard)
✓ Configuraciones Docker (docker-compose.yml)
✓ Tests completos del sistema
✓ Scripts de instalación automática (Windows + Linux)
✓ Documentación completa
✓ Configuraciones de ejemplo
✓ Infraestructura Terraform (opcional)

INSTALACIÓN:
============
1. Extraer {self.zip_file.name}
2. Windows: Ejecutar INSTALL.bat
3. Linux/Mac: Ejecutar ./install.sh

SERVICIOS INCLUIDOS:
===================
- Dashboard OptiMon: http://localhost:5000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090  
- AlertManager: http://localhost:9093

¡Paquete listo para distribución!
""")
            
            return True
            
        except Exception as e:
            self.log(f"Error creando paquete: {e}")
            return False

def main():
    """Función principal"""
    creator = DistributionPackageCreator()
    success = creator.create_distribution_package()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())