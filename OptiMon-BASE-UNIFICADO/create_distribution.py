#!/usr/bin/env python3
"""
OptiMon Distribution Package Creator
Crea un paquete ZIP completo para distribución
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

def create_distribution_package():
    """Crear paquete de distribución OptiMon"""
    
    print("🚀 Creando paquete de distribución OptiMon...")
    
    # Configuración
    source_dir = Path(".")
    dist_name = f"OptiMon-Sistema-Unificado-v3.0.0-{datetime.datetime.now().strftime('%Y%m%d')}"
    dist_dir = Path(f"../DISTRIBUCIONES/{dist_name}")
    zip_file = Path(f"../DISTRIBUCIONES/{dist_name}.zip")
    
    # Crear directorio de distribución
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Directorio de distribución: {dist_dir}")
    
    # Archivos principales a incluir
    files_to_copy = [
        "app.py",
        "azure_rest_helper.py", 
        "azure_helper.py",
        "requirements.txt",
        "docker-compose.yml",
        "README.md"
    ]
    
    # Directorios a incluir
    dirs_to_copy = [
        "docker",
        "templates", 
        "static",
        "config",
        "core"
    ]
    
    # Copiar archivos principales
    print("📄 Copiando archivos principales...")
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, dist_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ No encontrado: {file}")
    
    # Copiar directorios
    print("📁 Copiando directorios...")
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, dist_dir / dir_name, dirs_exist_ok=True)
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ⚠️ No encontrado: {dir_name}/")
    
    # Crear README de instalación
    create_installation_readme(dist_dir)
    
    # Crear scripts de instalación
    create_installation_scripts(dist_dir)
    
    # Crear estructura de configuración
    create_config_structure(dist_dir)
    
    # Crear archivo ZIP
    print("📦 Creando archivo ZIP...")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(dist_dir)
                zipf.write(file_path, arc_path)
    
    # Información del paquete
    zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
    
    print("\n" + "="*60)
    print("🎉 PAQUETE DE DISTRIBUCIÓN CREADO EXITOSAMENTE")
    print("="*60)
    print(f"📦 Archivo ZIP: {zip_file}")
    print(f"📏 Tamaño: {zip_size:.2f} MB")
    print(f"📅 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Versión: OptiMon v3.0.0-UNIFIED")
    print("="*60)
    
    return zip_file

def create_installation_readme(dist_dir):
    """Crear README de instalación"""
    readme_content = """# OptiMon Sistema Unificado v3.0.0
## 🚀 Sistema de Monitoreo Cloud Automático

### 📋 REQUISITOS DEL SISTEMA

**Software Requerido:**
- Python 3.11+ (recomendado) o Python 3.13
- Docker Desktop
- PowerShell (Windows) o Bash (Linux/macOS)
- Conexión a Internet

**Hardware Mínimo:**
- RAM: 4GB disponibles
- Disco: 2GB espacio libre
- CPU: 2 cores

### 🛠️ INSTALACIÓN RÁPIDA

#### Windows:
```cmd
1. Extraer el ZIP a una carpeta (ej: C:\\OptiMon)
2. Abrir PowerShell como Administrador
3. Navegar a la carpeta: cd C:\\OptiMon
4. Ejecutar: .\\install-windows.ps1
5. Esperar a que termine la instalación
6. Abrir http://localhost:5000
```

#### Linux/macOS:
```bash
1. Extraer el ZIP: unzip OptiMon-*.zip
2. Navegar: cd OptiMon-*/
3. Dar permisos: chmod +x install-linux.sh
4. Ejecutar: ./install-linux.sh
5. Abrir http://localhost:5000
```

### ⚡ INICIO RÁPIDO

1. **Acceder al Portal**: http://localhost:5000
2. **Configurar Nube**: 
   - AWS: Access Key, Secret Key, Región
   - Azure: Tenant ID, Client ID, Client Secret, Subscription ID
3. **Descubrir VMs**: Clic en "Descubrir Instancias"
4. **Monitorear**: Las VMs aparecen automáticamente en Grafana

### 🔧 FUNCIONALIDADES

✅ **Auto-descubrimiento** de VMs en AWS y Azure
✅ **Instalación automática** de Node Exporter vía SSH  
✅ **Detección automática** de claves SSH
✅ **Dashboards automáticos** en Grafana
✅ **Alertas** configurables
✅ **Compatible** con Python 3.13

### 🌐 PUERTOS UTILIZADOS

- **5000**: Portal Web OptiMon
- **3000**: Grafana (admin/admin)
- **9090**: Prometheus
- **9093**: AlertManager
- **9100**: Node Exporter (VMs remotas)

### 📚 DOCUMENTACIÓN

- **Portal Web**: Interfaz principal de configuración
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Logs**: Ver logs en la terminal donde se ejecuta

### 🐛 RESOLUCIÓN DE PROBLEMAS

**Docker no inicia:**
```bash
# Windows
Start-Service Docker

# Linux
sudo systemctl start docker
```

**Puerto 5000 ocupado:**
```bash
# Cambiar puerto en app.py línea final:
app.run(host='0.0.0.0', port=5001, debug=False)
```

**Errores de Python:**
```bash
# Verificar versión
python --version

# Reinstalar dependencias
pip install -r requirements.txt
```

### 🔑 CONFIGURACIÓN SSH

El sistema busca automáticamente claves SSH en:
- `~/.ssh/`
- `~/Downloads/`
- `./keys/`
- Archivos `.pem` en directorios comunes

**Usuarios SSH probados automáticamente:**
azureuser, ubuntu, ec2-user, admin, root, centos, debian

### 📞 SOPORTE

Para problemas o preguntas:
1. Verificar logs en la terminal
2. Revisar http://localhost:5000/api/health
3. Comprobar que Docker esté ejecutándose

---
**OptiMon v3.0.0-UNIFIED**  
Sistema de Monitoreo Cloud Automático  
© 2025 - Proyecto de Tesis
"""
    
    with open(dist_dir / "LEEME.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  ✅ LEEME.md")

def create_installation_scripts(dist_dir):
    """Crear scripts de instalación"""
    
    # Script Windows
    windows_script = """# OptiMon - Script de Instalación Windows
# Ejecutar como Administrador

Write-Host "🚀 Instalando OptiMon Sistema Unificado v3.0.0..." -ForegroundColor Green

# Verificar Python
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Instale Python 3.11+ desde python.org" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Verificar Docker
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no encontrado. Instale Docker Desktop" -ForegroundColor Red
    Write-Host "💡 Descarga: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    Read-Host "Presione Enter para salir"
    exit 1
}

# Instalar dependencias Python
Write-Host "📦 Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error instalando dependencias Python" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Iniciar Docker si no está ejecutándose
Write-Host "🐳 Iniciando servicios Docker..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error iniciando Docker Compose" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Esperar a que los servicios inicien
Write-Host "⏳ Esperando servicios Docker (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Iniciar OptiMon en background
Write-Host "🚀 Iniciando OptiMon..." -ForegroundColor Yellow
$job = Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    python app.py 
}

Write-Host "✅ OptiMon iniciado en background (Job ID: $($job.Id))" -ForegroundColor Green

# Esperar a que OptiMon inicie
Start-Sleep -Seconds 10

# Verificar que está funcionando
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 10
    Write-Host "✅ OptiMon funcionando correctamente" -ForegroundColor Green
    Write-Host "🌐 Portal disponible en: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "📊 Grafana disponible en: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ OptiMon podría estar iniciando..." -ForegroundColor Yellow
    Write-Host "🌐 Intente acceder a: http://localhost:5000" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Green
Write-Host "🌐 Portal OptiMon: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📊 Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "🔧 Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Green

Read-Host "Presione Enter para abrir el portal"
Start-Process "http://localhost:5000"
"""
    
    with open(dist_dir / "install-windows.ps1", 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    # Script Linux/macOS
    linux_script = """#!/bin/bash
# OptiMon - Script de Instalación Linux/macOS

echo "🚀 Instalando OptiMon Sistema Unificado v3.0.0..."

# Verificar Python
echo "🐍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Python no encontrado. Instale Python 3.11+"
    exit 1
fi

# Verificar Docker
echo "🐳 Verificando Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker encontrado: $DOCKER_VERSION"
else
    echo "❌ Docker no encontrado. Instale Docker"
    echo "💡 Instrucciones: https://docs.docker.com/get-docker/"
    exit 1
fi

# Instalar dependencias Python
echo "📦 Instalando dependencias Python..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias Python"
    exit 1
fi

# Iniciar Docker Compose
echo "🐳 Iniciando servicios Docker..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error iniciando Docker Compose"
    exit 1
fi

# Esperar servicios
echo "⏳ Esperando servicios Docker (30s)..."
sleep 30

# Iniciar OptiMon
echo "🚀 Iniciando OptiMon..."
$PYTHON_CMD app.py &
OPTIMON_PID=$!

# Esperar a que inicie
sleep 10

# Verificar funcionamiento
echo "🔍 Verificando OptiMon..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ OptiMon funcionando correctamente"
else
    echo "⚠️ OptiMon podría estar iniciando..."
fi

echo ""
echo "🎉 INSTALACIÓN COMPLETADA"
echo "================================================="
echo "🌐 Portal OptiMon: http://localhost:5000"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "🔧 Prometheus: http://localhost:9090"
echo "================================================="
echo "OptiMon PID: $OPTIMON_PID"
echo "Para detener: kill $OPTIMON_PID"
"""
    
    with open(dist_dir / "install-linux.sh", 'w', encoding='utf-8') as f:
        f.write(linux_script)
    
    print("  ✅ install-windows.ps1")
    print("  ✅ install-linux.sh")

def create_config_structure(dist_dir):
    """Crear estructura de configuración"""
    
    # Crear directorio config si no existe
    config_dir = dist_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Archivo de configuración ejemplo
    config_example = {
        "aws": {
            "access_key": "TU_ACCESS_KEY_AQUI",
            "secret_key": "TU_SECRET_KEY_AQUI", 
            "region": "us-east-1"
        },
        "azure": {
            "tenant_id": "TU_TENANT_ID_AQUI",
            "client_id": "TU_CLIENT_ID_AQUI",
            "client_secret": "TU_CLIENT_SECRET_AQUI",
            "subscription_id": "TU_SUBSCRIPTION_ID_AQUI"
        }
    }
    
    import json
    with open(config_dir / "cloud_credentials_example.json", 'w') as f:
        json.dump(config_example, f, indent=2)
    
    # Crear .gitignore para config
    gitignore_content = """# Ignorar credenciales reales
cloud_credentials.json
*.key
*.pem
*.private
"""
    
    with open(config_dir / ".gitignore", 'w') as f:
        f.write(gitignore_content)
    
    print("  ✅ config/cloud_credentials_example.json")
    print("  ✅ config/.gitignore")

if __name__ == "__main__":
    create_distribution_package()