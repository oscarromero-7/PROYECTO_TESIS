#!/usr/bin/env python3
"""
OptiMon - Generador de Paquete de Distribución
Crea un ZIP con todos los archivos necesarios para despliegue
"""

import os
import sys
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

class PackageBuilder:
    def __init__(self):
        self.project_root = Path(".")
        self.package_name = f"optimon-monitoring-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.temp_dir = Path(f"temp_{self.package_name}")
        self.output_file = f"{self.package_name}.zip"
        
    def create_package_structure(self):
        """Crea la estructura del paquete"""
        print("📁 Creando estructura del paquete...")
        
        # Crear directorio temporal
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        self.temp_dir.mkdir()
        
        # Estructura de directorios
        dirs_to_create = [
            "config/prometheus",
            "config/grafana/provisioning/datasources",
            "config/grafana/provisioning/dashboards", 
            "config/grafana/dashboards",
            "config/alertmanager",
            "scripts",
            "docs",
            "logs"
        ]
        
        for dir_path in dirs_to_create:
            (self.temp_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        print("✅ Estructura creada")
    
    def copy_essential_files(self):
        """Copia archivos esenciales al paquete"""
        print("📄 Copiando archivos esenciales...")
        
        # Archivos principales
        main_files = [
            "README.md",
            "requirements.txt",
            "docker-compose.yml",
            "deploy.sh",
            "deploy.ps1",
            "deploy.bat",
            "make.sh",
            "make.ps1", 
            "make.bat",
            "add_server.bat"
        ]
        
        for file_name in main_files:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, self.temp_dir / file_name)
                print(f"  ✅ {file_name}")
            else:
                print(f"  ⚠️  {file_name} no encontrado")
        
        # Hacer scripts ejecutables
        for script in ["deploy.sh"]:
            script_path = self.temp_dir / script
            if script_path.exists():
                script_path.chmod(0o755)
    
    def copy_config_files(self):
        """Copia archivos de configuración"""
        print("⚙️  Copiando configuraciones...")
        
        # Configuraciones de servicios
        config_mappings = {
            "config/credentials.simple.yml": "config/credentials.simple.yml",
            "config/grafana/provisioning/datasources/prometheus.yml": "config/grafana/provisioning/datasources/prometheus.yml",
            "config/grafana/provisioning/dashboards/optimon.yml": "config/grafana/provisioning/dashboards/optimon.yml",
            "config/alertmanager/alertmanager.yml": "config/alertmanager/alertmanager.yml"
        }
        
        for src_path, dst_path in config_mappings.items():
            src = self.project_root / src_path
            dst = self.temp_dir / dst_path
            
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✅ {dst_path}")
            else:
                print(f"  ⚠️  {src_path} no encontrado")
    
    def copy_scripts(self):
        """Copia scripts de automatización"""
        print("🔧 Copiando scripts...")
        
        scripts = [
            "scripts/auto_setup.py",
            "scripts/setup_prometheus.py",
            "scripts/setup_aws_monitoring.py", 
            "scripts/setup_azure_monitoring.py"
        ]
        
        for script_path in scripts:
            src = self.project_root / script_path
            dst = self.temp_dir / script_path
            
            if src.exists():
                shutil.copy2(src, dst)
                # Hacer ejecutable en Unix
                if script_path.endswith('.sh'):
                    dst.chmod(0o755)
                print(f"  ✅ {script_path}")
            else:
                print(f"  ⚠️  {script_path} no encontrado")
    
    def create_additional_scripts(self):
        """Crea scripts adicionales útiles"""
        print("📝 Creando scripts adicionales...")
        
        # Script bash para añadir servidores físicos (ya existe add_server.sh en los archivos principales)
        add_server_script = """#!/bin/bash
# Script para añadir servidores físicos al monitoreo

echo "OptiMon - Añadir Servidor Físico"
echo "================================="

read -p "Nombre del servidor: " SERVER_NAME
read -p "Dirección IP: " SERVER_IP
read -p "Usuario SSH: " SSH_USER
read -p "Puerto SSH (22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

echo "Selecciona método de autenticación:"
echo "1) Clave SSH"
echo "2) Contraseña"
read -p "Opción (1-2): " AUTH_METHOD

if [ "$AUTH_METHOD" = "1" ]; then
    read -p "Ruta a la clave privada: " KEY_FILE
    python3 scripts/add_physical_server.py add --name "$SERVER_NAME" --ip "$SERVER_IP" --user "$SSH_USER" --port "$SSH_PORT" --key "$KEY_FILE" --install
else
    read -s -p "Contraseña SSH: " SSH_PASS
    echo
    python3 scripts/add_physical_server.py add --name "$SERVER_NAME" --ip "$SERVER_IP" --user "$SSH_USER" --port "$SSH_PORT" --password "$SSH_PASS" --install
fi
"""
        
        with open(self.temp_dir / "add_server.sh", 'w') as f:
            f.write(add_server_script)
        (self.temp_dir / "add_server.sh").chmod(0o755)
        
        print("  ✅ add_server.sh")
        print("  ✅ Scripts .bat incluidos automáticamente")
    
    def create_documentation(self):
        """Crea documentación adicional"""
        print("📚 Creando documentación...")
        
        # Guía de inicio rápido
        quick_start = """# OptiMon - Guia de Inicio Rapido

## Instalacion SUPER FACIL en 3 pasos

### Paso 1: Configurar credenciales (SOLO esto)
```bash
# Editar el archivo de credenciales
# Solo necesitas completar las credenciales de tu proveedor de nube

# Para AWS - completar estos campos:
aws:
  access_key_id: "TU_AWS_ACCESS_KEY_ID"
  secret_access_key: "TU_AWS_SECRET_ACCESS_KEY"
  region: "us-east-1"

# Para Azure - completar estos campos:
azure:
  subscription_id: "TU_AZURE_SUBSCRIPTION_ID"
  tenant_id: "TU_AZURE_TENANT_ID"
  client_id: "TU_AZURE_CLIENT_ID"
  client_secret: "TU_AZURE_CLIENT_SECRET"
```

### Paso 2: Ejecutar TODO automaticamente
```bash
# Linux/Mac
./deploy.sh

# Windows
.\deploy.ps1
```

### Paso 3: Acceder y monitorear
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093

## ESO ES TODO!

El sistema automaticamente:
- Detecta todas tus VMs/instancias
- Encuentra las claves SSH correctas  
- Instala Node Exporter en cada servidor
- Configura Prometheus y Grafana
- Inicia el monitoreo completo

## Que hace automaticamente

### Deteccion inteligente:
- Encuentra todas las VMs en ejecucion
- Detecta el usuario SSH correcto por tipo de OS
- Busca claves SSH en ubicaciones comunes
- Determina IPs publicas/privadas disponibles

### Instalacion automatica:
- Instala Node Exporter en paralelo
- Configura servicios systemd
- Actualiza configuracion de Prometheus
- Crea dashboards personalizados

### Sin configuracion manual:
- No necesitas especificar IPs
- No necesitas configurar SSH
- No necesitas usuarios o puertos
- No necesitas claves SSH manuales

## Solucion de Problemas

### Si no detecta instancias:
- Verifica credenciales de nube
- Verifica que las VMs esten ejecutandose
- Verifica permisos IAM/RBAC

### Si no se conecta por SSH:
- El sistema probara usuarios comunes automaticamente
- Buscara claves SSH en ubicaciones estandar
- Intentara multiples metodos de conexion

### Ver que esta pasando:
```bash
# Ver logs detallados
docker-compose logs -f

# Ver targets de Prometheus
http://localhost:9090/targets

# Probar conectividad manual
ssh usuario@ip_instancia
```
"""
        
        with open(self.temp_dir / "docs" / "QUICK_START.md", 'w') as f:
            f.write(quick_start)
        
        # Archivo de troubleshooting
        troubleshooting = """# OptiMon - Solucion de Problemas

## Problemas Comunes

### 1. Docker no inicia servicios
```bash
# Verificar estado de Docker
docker info

# Verificar logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### 2. No se conecta a VMs en la nube
- Verificar credenciales en archivos de configuracion
- Verificar permisos IAM/RBAC
- Verificar grupos de seguridad/NSG permiten SSH (puerto 22)

### 3. Node Exporter no se instala
- Verificar conectividad SSH a las maquinas
- Verificar permisos sudo del usuario SSH
- Verificar que las maquinas son Linux (Windows no soportado)

### 4. Grafana no muestra datos
- Verificar que Prometheus este ejecutandose: http://localhost:9090
- Verificar targets en Prometheus: http://localhost:9090/targets
- Verificar que Node Exporter este respondiendo en puerto 9100

### 5. Alertas no funcionan
- Verificar configuracion en config/alertmanager/alertmanager.yml
- Verificar reglas en config/prometheus/alert.rules.yml
- Verificar conectividad SMTP/webhook segun configuracion

## Comandos Utiles

### Ver todos los logs
```bash
docker-compose logs -f
```

### Reiniciar un servicio especifico
```bash
docker-compose restart prometheus
docker-compose restart grafana
```

### Reconstruir configuracion
```bash
python scripts/setup_prometheus.py
docker-compose restart prometheus
```

### Verificar conectividad a un servidor
```bash
ssh -o ConnectTimeout=10 usuario@ip_servidor
```

### Probar Node Exporter remoto
```bash
curl http://ip_servidor:9100/metrics
```

## Archivos de Log

Los logs se guardan en:
- `logs/optimon.log` - Log principal
- `logs/errors.log` - Solo errores
- `logs/access.log` - Accesos HTTP

## Contacto

Para soporte adicional:
- GitHub Issues: [Reportar problema](https://github.com/oscarromero-7/PROYECTO_TESIS/issues)
- Email: support@optimon.com
"""
        
        with open(self.temp_dir / "docs" / "TROUBLESHOOTING.md", 'w') as f:
            f.write(troubleshooting)
        
        print("  ✅ QUICK_START.md")
        print("  ✅ TROUBLESHOOTING.md")
    
    def create_example_dashboards(self):
        """Copia los dashboards personalizados de OptiMon"""
        print("📊 Copiando dashboards personalizados...")
        
        # Directorio de dashboards de origen
        source_dashboard_dir = Path("config/grafana/dashboards")
        target_dashboard_dir = self.temp_dir / "config" / "grafana" / "dashboards"
        
        if source_dashboard_dir.exists():
            # Copiar todos los archivos .json de dashboards
            dashboard_files = list(source_dashboard_dir.glob("*.json"))
            
            for dashboard_file in dashboard_files:
                target_file = target_dashboard_dir / dashboard_file.name
                shutil.copy2(dashboard_file, target_file)
                print(f"  ✅ {dashboard_file.name}")
            
            if dashboard_files:
                print(f"  📊 {len(dashboard_files)} dashboards personalizados copiados")
            else:
                print("  ⚠️ No se encontraron dashboards personalizados")
                # Crear dashboard básico como fallback
                self._create_fallback_dashboard()
        else:
            print("  ⚠️ Directorio de dashboards no encontrado")
            # Crear dashboard básico como fallback
            self._create_fallback_dashboard()
    
    def _create_fallback_dashboard(self):
        """Crea un dashboard básico como fallback"""
        basic_dashboard = {
            "id": None,
            "title": "OptiMon - Infrastructure Overview",
            "tags": ["optimon", "infrastructure"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "CPU Usage",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                            "legendFormat": "{{instance}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 70},
                                    {"color": "red", "value": 90}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "30s",
            "uid": "optimon-infrastructure",
            "version": 1
        }
        
        import json
        target_dashboard_dir = self.temp_dir / "config" / "grafana" / "dashboards"
        with open(target_dashboard_dir / "infrastructure-overview.json", 'w') as f:
            json.dump(basic_dashboard, f, indent=2)
        
        print("  ✅ Dashboard básico creado como fallback")
    
    def create_zip_package(self):
        """Crea el archivo ZIP final"""
        print("📦 Creando paquete ZIP...")
        
        with zipfile.ZipFile(self.output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, self.temp_dir)
                    zipf.write(file_path, arc_path)
        
        # Limpiar directorio temporal
        shutil.rmtree(self.temp_dir)
        
        print(f"✅ Paquete creado: {self.output_file}")
        
        # Mostrar tamaño del archivo
        size_mb = os.path.getsize(self.output_file) / (1024 * 1024)
        print(f"📏 Tamaño: {size_mb:.2f} MB")
    
    def show_summary(self):
        """Muestra resumen del paquete creado"""
        print("\n🎉 Paquete OptiMon creado exitosamente!")
        print("=" * 50)
        print(f"📦 Archivo: {self.output_file}")
        print("\n📋 Contenido incluido:")
        print("  ✅ Scripts de despliegue automático")
        print("  ✅ Configuraciones de Docker Compose")
        print("  ✅ Configuraciones de Prometheus, Grafana, AlertManager")
        print("  ✅ Scripts de configuración para AWS y Azure")
        print("  ✅ Dashboards de ejemplo")
        print("  ✅ Documentación completa")
        print("\n🚀 Instrucciones de uso:")
        print("  1. Envía el ZIP al usuario final")
        print("  2. El usuario descomprime el archivo")
        print("  3. Configura credenciales en config/")
        print("  4. Ejecuta deploy.sh (Linux/Mac) o deploy.ps1 (Windows)")
        print("  5. Accede a Grafana en http://localhost:3000")
        print("\n📖 Documentación incluida:")
        print("  - README.md: Información general")
        print("  - docs/QUICK_START.md: Guía de inicio rápido")
        print("  - docs/TROUBLESHOOTING.md: Solución de problemas")
    
    def run(self):
        """Ejecuta el proceso completo de empaquetado"""
        print("📦 OptiMon - Generador de Paquete")
        print("=" * 40)
        
        try:
            self.create_package_structure()
            self.copy_essential_files()
            self.copy_config_files()
            self.copy_scripts()
            self.create_additional_scripts()
            self.create_documentation()
            self.create_example_dashboards()
            self.create_zip_package()
            self.show_summary()
            
        except Exception as e:
            print(f"❌ Error creando paquete: {e}")
            # Limpiar en caso de error
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            sys.exit(1)

if __name__ == "__main__":
    try:
        builder = PackageBuilder()
        builder.run()
    except KeyboardInterrupt:
        print("\n❌ Empaquetado interrumpido por el usuario")
        sys.exit(1)