#!/usr/bin/env python3
"""
OptiMon Sistema Unificado - Generador de Distribución
Versión: 3.0.0-UNIFIED
Autor: OptiMon Team
Descripción: Crea paquete ZIP completo para distribución final
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
import tempfile

class DistributionCreator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_dir = os.path.join(self.base_dir, "OptiMon-BASE-UNIFICADO")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dist_name = f"OptiMon-Sistema-Unificado-v3.0.0-{self.timestamp}"
        self.dist_dir = os.path.join(self.base_dir, "DISTRIBUCION", self.dist_name)
        
    def create_directory_structure(self):
        """Crea la estructura de directorios para distribución"""
        print("📁 Creando estructura de directorios...")
        
        directories = [
            self.dist_dir,
            os.path.join(self.dist_dir, "core"),
            os.path.join(self.dist_dir, "docker", "prometheus"),
            os.path.join(self.dist_dir, "docker", "grafana", "dashboards"),
            os.path.join(self.dist_dir, "docker", "grafana", "provisioning", "dashboards"),
            os.path.join(self.dist_dir, "docker", "grafana", "provisioning", "datasources"),
            os.path.join(self.dist_dir, "docker", "alertmanager"),
            os.path.join(self.dist_dir, "config"),
            os.path.join(self.dist_dir, "templates"),
            os.path.join(self.dist_dir, "static", "css"),
            os.path.join(self.dist_dir, "static", "js"),
            os.path.join(self.dist_dir, "logs"),
            os.path.join(self.dist_dir, "scripts")
        ]
        
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)
            
        print(f"✅ Estructura creada en: {self.dist_dir}")
        
    def copy_core_files(self):
        """Copia archivos principales del sistema"""
        print("📄 Copiando archivos principales...")
        
        # Archivos principales
        core_files = [
            "app.py",
            "docker-compose.yml", 
            "requirements.txt",
            "README.md",
            ".env.example"
        ]
        
        for file_name in core_files:
            source_path = os.path.join(self.source_dir, file_name)
            dest_path = os.path.join(self.dist_dir, file_name)
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ {file_name}")
            else:
                print(f"  ⚠️  {file_name} no encontrado")
                
        # Directorio core completo
        core_source = os.path.join(self.source_dir, "core")
        core_dest = os.path.join(self.dist_dir, "core")
        
        if os.path.exists(core_source):
            shutil.copytree(core_source, core_dest, dirs_exist_ok=True)
            print("  ✅ Directorio core/")
            
        # Directorio templates
        templates_source = os.path.join(self.source_dir, "templates")
        templates_dest = os.path.join(self.dist_dir, "templates")
        
        if os.path.exists(templates_source):
            shutil.copytree(templates_source, templates_dest, dirs_exist_ok=True)
            print("  ✅ Directorio templates/")
            
        # Directorio static
        static_source = os.path.join(self.source_dir, "static")
        static_dest = os.path.join(self.dist_dir, "static")
        
        if os.path.exists(static_source):
            shutil.copytree(static_source, static_dest, dirs_exist_ok=True)
            print("  ✅ Directorio static/")
            
    def copy_docker_configs(self):
        """Copia configuraciones de Docker"""
        print("🐳 Copiando configuraciones Docker...")
        
        # Directorio docker completo
        docker_source = os.path.join(self.source_dir, "docker")
        docker_dest = os.path.join(self.dist_dir, "docker")
        
        if os.path.exists(docker_source):
            shutil.copytree(docker_source, docker_dest, dirs_exist_ok=True)
            print("  ✅ Configuraciones Docker copiadas")
        else:
            print("  ⚠️  Directorio docker/ no encontrado")
            
    def create_installation_scripts(self):
        """Crea scripts de instalación automática"""
        print("🔧 Creando scripts de instalación...")
        
        # Script Windows
        windows_script = """@echo off
title OptiMon Sistema Unificado - Instalador
color 0A

echo.
echo ==========================================
echo   OptiMon Sistema Unificado v3.0.0
echo   Instalador Automatico Windows
echo ==========================================
echo.

echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker no encontrado
    echo.
    echo Por favor instalar Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)
echo ✅ Docker encontrado

echo.
echo [2/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no encontrado
    echo Por favor instalar Python 3.11+ desde:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [3/6] Instalando dependencias Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Fallo instalación dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo [4/6] Iniciando servicios Docker...
docker compose up -d
if %errorlevel% neq 0 (
    echo ❌ ERROR: Fallo inicio Docker services
    pause
    exit /b 1
)
echo ✅ Servicios Docker iniciados

echo.
echo [5/6] Configurando archivo .env...
if not exist ".env" (
    copy ".env.example" ".env"
    echo ✅ Archivo .env creado
) else (
    echo ✅ Archivo .env ya existe
)

echo.
echo [6/6] Iniciando OptiMon Portal...
echo.
echo ==========================================
echo   ✅ INSTALACION COMPLETADA
echo.
echo   Accesos del sistema:
echo   📱 Portal Principal: http://localhost:5000
echo   📊 Grafana:         http://localhost:3000
echo   📈 Prometheus:      http://localhost:9090
echo   🚨 AlertManager:    http://localhost:9093
echo.
echo   Iniciando aplicacion...
echo ==========================================
echo.

start "" http://localhost:5000
python app.py

pause
"""

        # Script Linux/macOS
        linux_script = """#!/bin/bash

# Colores para output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "  OptiMon Sistema Unificado v3.0.0"
echo "  Instalador Automatico Linux/macOS"
echo "=========================================="
echo -e "${NC}"

# Verificar Docker
echo -e "${YELLOW}[1/6] Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker no encontrado${NC}"
    echo -e "${YELLOW}Por favor instalar Docker desde: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker encontrado${NC}"

# Verificar Python
echo -e "${YELLOW}[2/6] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: Python3 no encontrado${NC}"
    echo -e "${YELLOW}Por favor instalar Python 3.11+ desde: https://www.python.org/downloads/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python encontrado${NC}"

# Instalar dependencias
echo -e "${YELLOW}[3/6] Instalando dependencias Python...${NC}"
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Fallo instalación dependencias${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Iniciar servicios Docker
echo -e "${YELLOW}[4/6] Iniciando servicios Docker...${NC}"
docker compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Fallo inicio Docker services${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Servicios Docker iniciados${NC}"

# Configurar .env
echo -e "${YELLOW}[5/6] Configurando archivo .env...${NC}"
if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# Iniciar aplicación
echo -e "${YELLOW}[6/6] Iniciando OptiMon Portal...${NC}"

echo -e "${BLUE}"
echo "=========================================="
echo "  ✅ INSTALACION COMPLETADA"
echo ""
echo "  Accesos del sistema:"
echo "  📱 Portal Principal: http://localhost:5000"
echo "  📊 Grafana:         http://localhost:3000"  
echo "  📈 Prometheus:      http://localhost:9090"
echo "  🚨 AlertManager:    http://localhost:9093"
echo ""
echo "  Iniciando aplicacion..."
echo "=========================================="
echo -e "${NC}"

# Abrir navegador (si está disponible)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000 &
elif command -v open &> /dev/null; then
    open http://localhost:5000 &
fi

python3 app.py
"""

        # Escribir scripts
        with open(os.path.join(self.dist_dir, "install-windows.bat"), 'w', encoding='utf-8') as f:
            f.write(windows_script)
        print("  ✅ install-windows.bat")
        
        with open(os.path.join(self.dist_dir, "install-linux.sh"), 'w', encoding='utf-8') as f:
            f.write(linux_script)
        os.chmod(os.path.join(self.dist_dir, "install-linux.sh"), 0o755)
        print("  ✅ install-linux.sh")
        
    def create_env_example(self):
        """Crea archivo .env.example"""
        print("⚙️  Creando archivo .env.example...")
        
        env_content = """# OptiMon Sistema Unificado - Configuración de Ambiente
# Versión: 3.0.0-UNIFIED

# ==========================================
# CONFIGURACION SMTP (Email Alerts)
# ==========================================
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu-email@outlook.com
SMTP_PASSWORD=tu-password-aqui
SMTP_FROM=tu-email@outlook.com

# ==========================================
# CONFIGURACION SISTEMA
# ==========================================
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=optimon-secret-key-change-in-production

# ==========================================
# CONFIGURACION PUERTOS
# ==========================================
OPTIMON_PORT=5000
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
ALERTMANAGER_PORT=9093
NODE_EXPORTER_PORT=9100
WINDOWS_EXPORTER_PORT=9182

# ==========================================
# CONFIGURACION LOGGING
# ==========================================
LOG_LEVEL=INFO
LOG_FILE=logs/optimon.log

# ==========================================
# CONFIGURACION CLOUD (Opcional)
# ==========================================
# AWS_ACCESS_KEY_ID=tu-access-key
# AWS_SECRET_ACCESS_KEY=tu-secret-key
# AWS_REGION=us-east-1

# AZURE_TENANT_ID=tu-tenant-id
# AZURE_CLIENT_ID=tu-client-id  
# AZURE_CLIENT_SECRET=tu-client-secret
# AZURE_SUBSCRIPTION_ID=tu-subscription-id

# ==========================================
# CONFIGURACION SSH (Auto-detecta)
# ==========================================
SSH_TIMEOUT=10
SSH_RETRY_ATTEMPTS=3
SSH_KEY_SCAN_PATHS=~/.ssh,~/Downloads,~/Desktop,./keys

# ==========================================
# CONFIGURACION MONITOREO
# ==========================================
SCRAPE_INTERVAL=15s
EVALUATION_INTERVAL=15s
RETENTION_TIME=15d
"""

        with open(os.path.join(self.dist_dir, ".env.example"), 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("  ✅ .env.example creado")
        
    def create_documentation(self):
        """Crea documentación adicional"""
        print("📚 Creando documentación...")
        
        # Manual de usuario
        user_manual = """# OptiMon Sistema Unificado - Manual de Usuario
Versión: 3.0.0-UNIFIED

## 🚀 Instalación Rápida

### Windows
1. Extraer OptiMon-Sistema-Unificado-*.zip
2. Ejecutar como administrador: `install-windows.bat`
3. Abrir navegador en: http://localhost:5000

### Linux/macOS
1. Extraer OptiMon-Sistema-Unificado-*.zip
2. Ejecutar: `chmod +x install-linux.sh && ./install-linux.sh`
3. Abrir navegador en: http://localhost:5000

## 📋 Requisitos Previos

### Software Necesario
- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **Python 3.11+**: https://www.python.org/downloads/
- **PowerShell** (Windows) o **Bash** (Linux/macOS)

### Hardware Mínimo
- **RAM**: 4GB disponibles
- **Disco**: 2GB espacio libre
- **CPU**: 2 cores mínimo
- **Red**: Conexión a Internet para contenedores

## 🌐 Accesos del Sistema

| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| **Portal OptiMon** | http://localhost:5000 | - | - |
| **Grafana** | http://localhost:3000 | admin | admin |
| **Prometheus** | http://localhost:9090 | - | - |
| **AlertManager** | http://localhost:9093 | - | - |

## ⚙️ Configuración Inicial

### 1. Configurar Emails (Opcional)
1. Acceder al Portal: http://localhost:5000
2. Click en "Email Configuration"
3. Ingresar credenciales SMTP
4. Agregar destinatarios
5. Click "Guardar Configuración"

### 2. Configurar Cloud (Opcional)
1. Acceder al Portal: http://localhost:5000
2. Click en "Cloud Configuration" 
3. Agregar credenciales AWS y/o Azure
4. Click "Guardar Credenciales"
5. Click "Descubrir VMs"

### 3. Verificar Sistema Local
1. El sistema se configura automáticamente
2. Windows Exporter se instala solo
3. Dashboard local disponible inmediatamente

## 🔧 Configuración Avanzada

### SSH Keys Auto-Detection
El sistema busca automáticamente claves SSH en:
- `~/.ssh/` - Directorio SSH estándar
- `~/Downloads/` - Carpeta de descargas
- `~/Desktop/` - Escritorio
- `./keys/` - Directorio local

### Usuarios SSH Probados
- **Cloud**: azureuser, ec2-user, ubuntu
- **Estándar**: admin, root, user
- **Distribuciones**: centos, debian, fedora
- **Especiales**: bitnami, oracle, deploy

### Configurar Alertas Personalizadas
1. Editar: `docker/prometheus/alert.rules.yml`
2. Reiniciar: `docker compose restart prometheus`
3. Verificar en AlertManager

## 🐛 Solución de Problemas

### Docker no inicia
```bash
# Windows
Restart-Service Docker

# Linux
sudo systemctl restart docker
```

### Puerto ocupado
```bash
# Encontrar proceso
netstat -ano | findstr :5000

# Terminar proceso
taskkill /PID <PID> /F
```

### Python no encontrado
```bash
# Verificar instalación
python --version
python3 --version

# Si no existe, descargar desde:
# https://www.python.org/downloads/
```

### Servicios no inician
```bash
# Verificar Docker Compose
docker compose ps

# Reiniciar servicios
docker compose down
docker compose up -d
```

## 📊 Dashboards Disponibles

### Sistema Local
- CPU, RAM, Disk en tiempo real
- Alertas configuradas automáticamente
- Histórico de métricas

### Cloud Infrastructure  
- AWS EC2 instances
- Azure Virtual Machines
- Estado de Node Exporters

### Alertas Activas
- CPU > 80%
- RAM > 85% 
- Disk > 90%
- Servicios caídos

## 🔐 Seguridad

- Credenciales almacenadas localmente
- Conexiones SSH cifradas
- No transmisión de claves privadas
- APIs cloud con autenticación oficial

## 📞 Soporte

- **Portal**: http://localhost:5000/help
- **Status**: http://localhost:5000/api/health
- **SSH Keys**: http://localhost:5000/api/ssh-keys
- **Email**: Proyecto20251985@hotmail.com

---
OptiMon Sistema Unificado v3.0.0-UNIFIED
© 2025 - Proyecto Académico
"""

        # Guía de troubleshooting
        troubleshooting = """# OptiMon - Guía de Solución de Problemas

## 🚨 Problemas Comunes

### 1. Error "Docker no encontrado"
**Síntoma**: `docker: command not found`
**Solución**:
1. Instalar Docker Desktop
2. Asegurarse que Docker está ejecutándose
3. Reiniciar terminal/PowerShell

### 2. Error "Puerto 5000 ocupado"
**Síntoma**: `Address already in use`
**Solución**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:5000 | xargs kill -9
```

### 3. Error "Python no encontrado"
**Síntoma**: `python: command not found`
**Solución**:
1. Instalar Python 3.11+
2. Agregar Python al PATH
3. Usar `python3` en lugar de `python`

### 4. Servicios Docker no inician
**Síntoma**: Containers en estado "Exited"
**Solución**:
```bash
docker compose down
docker compose up -d
docker compose logs
```

### 5. Windows Exporter no funciona
**Síntoma**: No aparecen métricas locales
**Solución**:
1. Ejecutar como administrador
2. Verificar puerto 9182
3. Reiniciar sistema si es necesario

## 🔧 Comandos de Diagnóstico

### Verificar Estado del Sistema
```bash
# Estado Docker
docker compose ps

# Logs de servicios
docker compose logs prometheus
docker compose logs grafana

# Estado de puertos
netstat -ano | findstr "5000 3000 9090 9093"

# Verificar Python
python --version
pip list | findstr "flask prometheus psutil"
```

### Verificar Conectividad
```bash
# Portal OptiMon
curl http://localhost:5000/api/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

## 📊 Logs Importantes

### Ubicaciones de Logs
- **OptiMon**: `logs/optimon.log`
- **Docker Compose**: `docker compose logs`
- **Windows**: Event Viewer > Applications
- **Linux**: `/var/log/syslog`

### Comandos de Log
```bash
# Ver logs OptiMon
tail -f logs/optimon.log

# Ver logs Docker en tiempo real
docker compose logs -f

# Ver logs específico
docker compose logs prometheus
```

## 🌐 Problemas de Red

### Proxy/Firewall
Si estás detrás de proxy corporativo:
1. Configurar Docker con proxy
2. Configurar pip con proxy
3. Abrir puertos en firewall

### DNS Issues
```bash
# Verificar resolución DNS
nslookup docker.io
ping 8.8.8.8
```

## 💾 Recuperación de Datos

### Backup de Configuración
```bash
# Respaldar configuraciones
cp -r docker/prometheus ./backup/
cp -r docker/grafana ./backup/
cp config/*.json ./backup/
```

### Restaurar Sistema
```bash
# Limpiar todo
docker compose down -v
docker system prune -af

# Restaurar y reiniciar
docker compose up -d
```

## 🔄 Actualización del Sistema

### Actualizar OptiMon
1. Descargar nueva versión
2. Backup configuraciones
3. Extraer nueva versión
4. Copiar configuraciones antiguas
5. Ejecutar instalador

### Actualizar Docker Images
```bash
docker compose pull
docker compose up -d
```

## 📞 Obtener Ayuda

### Información del Sistema
1. Acceder a: http://localhost:5000/api/health
2. Capturar screenshot del error
3. Copiar logs relevantes
4. Incluir versión del OS

### Reportar Problemas
- **Email**: Proyecto20251985@hotmail.com
- **Incluir**: OS, Python version, Docker version
- **Adjuntar**: Logs y screenshots

---
Última actualización: $(date)
"""

        # Escribir documentación
        with open(os.path.join(self.dist_dir, "MANUAL-USUARIO.md"), 'w', encoding='utf-8') as f:
            f.write(user_manual)
        print("  ✅ MANUAL-USUARIO.md")
        
        with open(os.path.join(self.dist_dir, "TROUBLESHOOTING.md"), 'w', encoding='utf-8') as f:
            f.write(troubleshooting)
        print("  ✅ TROUBLESHOOTING.md")
        
    def create_version_info(self):
        """Crea archivo de información de versión"""
        print("📝 Creando información de versión...")
        
        version_info = {
            "version": "3.0.0-UNIFIED",
            "build_date": datetime.now().isoformat(),
            "build_timestamp": self.timestamp,
            "description": "OptiMon Sistema Unificado - Distribución Final",
            "features": [
                "Portal web unificado",
                "Auto-descubrimiento AWS y Azure",
                "SSH key auto-detection", 
                "Node Exporter auto-instalación",
                "Windows Exporter automático",
                "Email alerts configurables",
                "Dashboards Grafana pre-configurados",
                "Sistema de alertas avanzado"
            ],
            "requirements": {
                "python": "3.11+",
                "docker": "latest",
                "memory": "4GB",
                "disk": "2GB"
            },
            "services": {
                "optimon_portal": "http://localhost:5000",
                "grafana": "http://localhost:3000",
                "prometheus": "http://localhost:9090", 
                "alertmanager": "http://localhost:9093"
            },
            "compatibility": {
                "windows": "10/11",
                "linux": "Ubuntu 18.04+, CentOS 7+",
                "macos": "10.14+"
            }
        }
        
        with open(os.path.join(self.dist_dir, "VERSION_INFO.json"), 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        print("  ✅ VERSION_INFO.json")
        
    def create_quick_start(self):
        """Crea guía de inicio rápido"""
        print("⚡ Creando guía de inicio rápido...")
        
        quick_start = """# 🚀 OptiMon - Inicio Rápido (5 minutos)

## ✅ Verificación Previa (1 minuto)

### ¿Tienes Docker?
```bash
docker --version
```
❌ **Si no**: Descargar desde https://www.docker.com/products/docker-desktop

### ¿Tienes Python?
```bash
python --version
```
❌ **Si no**: Descargar desde https://www.python.org/downloads/

## 🎯 Instalación Express (2 minutos)

### Windows
```cmd
# Extraer ZIP y ejecutar:
install-windows.bat
```

### Linux/macOS  
```bash
# Extraer ZIP y ejecutar:
chmod +x install-linux.sh
./install-linux.sh
```

## 🌐 Acceso Inmediato (30 segundos)

Abrir navegador en:
- **🎛️ Portal Principal**: http://localhost:5000
- **📊 Grafana**: http://localhost:3000 (admin/admin)

## ⚙️ Configuración Opcional (2 minutos)

### Email Alerts
1. Portal → Email Config
2. Ingresar SMTP (Outlook recomendado)
3. Agregar destinatarios

### Cloud Monitoring
1. Portal → Cloud Config  
2. Agregar credenciales AWS/Azure
3. Click "Descubrir VMs"

## ✅ ¡Listo!

Tu sistema ya está monitoreando:
- ✅ PC local (automático)
- ✅ Dashboards disponibles
- ✅ Alertas configuradas
- ✅ Cloud (si configuraste)

---
**¿Problemas?** Ver TROUBLESHOOTING.md
**¿Preguntas?** Ver MANUAL-USUARIO.md
"""

        with open(os.path.join(self.dist_dir, "INICIO-RAPIDO.md"), 'w', encoding='utf-8') as f:
            f.write(quick_start)
        print("  ✅ INICIO-RAPIDO.md")
        
    def create_zip_package(self):
        """Crea el paquete ZIP final"""
        print("📦 Creando paquete ZIP final...")
        
        zip_path = os.path.join(self.base_dir, "DISTRIBUCION", f"{self.dist_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(self.dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.dist_dir)
                    zipf.write(file_path, arcname)
                    
        # Obtener tamaño del ZIP
        zip_size = os.path.getsize(zip_path)
        zip_size_mb = zip_size / (1024 * 1024)
        
        print(f"  ✅ ZIP creado: {zip_path}")
        print(f"  📏 Tamaño: {zip_size_mb:.2f} MB")
        
        return zip_path, zip_size_mb
        
    def cleanup_temp_directory(self):
        """Limpia directorio temporal"""
        print("🧹 Limpiando archivos temporales...")
        
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
            print("  ✅ Directorio temporal eliminado")
            
    def generate_distribution(self):
        """Genera la distribución completa"""
        print("🎯 Iniciando generación de distribución OptiMon...")
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"📁 Directorio fuente: {self.source_dir}")
        print("-" * 60)
        
        try:
            # Verificar directorio fuente
            if not os.path.exists(self.source_dir):
                print(f"❌ ERROR: Directorio fuente no encontrado: {self.source_dir}")
                return False
                
            # Pasos de generación
            self.create_directory_structure()
            self.copy_core_files()
            self.copy_docker_configs()
            self.create_installation_scripts()
            self.create_env_example()
            self.create_documentation()
            self.create_version_info()
            self.create_quick_start()
            
            # Crear ZIP final
            zip_path, zip_size = self.create_zip_package()
            
            # Cleanup
            self.cleanup_temp_directory()
            
            # Resumen final
            print("\n" + "=" * 60)
            print("🎉 DISTRIBUCIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print(f"📦 Archivo: {os.path.basename(zip_path)}")
            print(f"📏 Tamaño: {zip_size:.2f} MB")
            print(f"📍 Ubicación: {os.path.dirname(zip_path)}")
            print(f"🕐 Tiempo: {datetime.now().strftime('%H:%M:%S')}")
            print("\n🚀 READY FOR DISTRIBUTION!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR durante la generación: {str(e)}")
            return False

if __name__ == "__main__":
    creator = DistributionCreator()
    success = creator.generate_distribution()
    
    if success:
        print("\n✅ Distribución lista para entrega al usuario final")
    else:
        print("\n❌ Error en la generación de distribución")
        exit(1)