#!/usr/bin/env python3
"""
Generador de Paquete de Distribución OptiMon v3.0.0
Crea un ZIP completo listo para distribución a usuarios finales
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import json

def create_distribution_package():
    """Crear paquete de distribución completo"""
    
    print("🚀" + "=" * 60 + "🚀")
    print("📦 GENERADOR DE PAQUETE OPTIMON v3.0.0")
    print("🎯 Creando distribución para usuario final")
    print("📅 " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🚀" + "=" * 60 + "🚀")
    print()
    
    # Configuración
    source_dir = Path(__file__).parent
    dist_name = "OptiMon-Usuario-Final-v3.0.0"
    dist_dir = source_dir / dist_name
    zip_path = source_dir / f"{dist_name}.zip"
    
    # Limpiar directorio anterior
    if dist_dir.exists():
        print("🧹 Limpiando distribución anterior...")
        shutil.rmtree(dist_dir)
    
    if zip_path.exists():
        zip_path.unlink()
    
    # Crear directorio de distribución
    print("📁 Creando estructura de distribución...")
    dist_dir.mkdir()
    
    # Archivos principales a incluir
    main_files = [
        "app.py",
        "requirements.txt",
        "docker-compose.yml",
        "INSTALAR_FACIL.bat",
        "INSTALAR_OPTIMON.bat",
        "INSTALAR_OPTIMON.ps1",
        "README_USUARIO_FINAL.md",
        ".env.azure"
    ]
    
    # Directorios a incluir
    directories = [
        "config",
        "core", 
        "templates",
        "docker"
    ]
    
    # Copiar archivos principales
    print("📄 Copiando archivos principales...")
    for file in main_files:
        src_path = source_dir / file
        if src_path.exists():
            shutil.copy2(src_path, dist_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (no encontrado)")
    
    # Copiar directorios
    print("📂 Copiando directorios...")
    for directory in directories:
        src_dir = source_dir / directory
        if src_dir.exists() and src_dir.is_dir():
            shutil.copytree(src_dir, dist_dir / directory)
            print(f"  ✅ {directory}/")
        else:
            print(f"  ⚠️ {directory}/ (no encontrado)")
    
    # Crear archivo de versión
    print("📋 Creando información de versión...")
    version_info = {
        "name": "OptiMon Sistema Unificado",
        "version": "3.0.0-UNIFIED",
        "build_date": datetime.now().isoformat(),
        "description": "Sistema completo de monitoreo con integración Azure",
        "components": {
            "flask_app": "Portal web principal",
            "prometheus": "Métricas y monitoreo",
            "grafana": "Dashboards y visualización",
            "alertmanager": "Sistema de alertas",
            "windows_exporter": "Monitoreo local Windows"
        },
        "urls": {
            "portal": "http://localhost:5000",
            "grafana": "http://localhost:3000",
            "prometheus": "http://localhost:9090",
            "alertmanager": "http://localhost:9093"
        }
    }
    
    with open(dist_dir / "VERSION.json", "w", encoding="utf-8") as f:
        json.dump(version_info, f, indent=4, ensure_ascii=False)
    
    # Crear archivo de inicio rápido
    print("🚀 Creando guía de inicio rápido...")
    quick_start = """
# 🚀 INICIO RÁPIDO - OptiMon v3.0.0

## ⚡ Instalación en 10 segundos

### OPCIÓN 1: SÚPER FÁCIL (Recomendado)
1. **Doble clic en:**
   ```
   INSTALAR_FACIL.bat
   ```
2. **Confirmar UAC** cuando aparezca
3. **¡Listo!** Todo se instala automáticamente

### OPCIÓN 2: PowerShell
```powershell
.\INSTALAR_OPTIMON.ps1
```

### OPCIÓN 3: Batch tradicional
```cmd
INSTALAR_OPTIMON.bat
```

## 🎯 ¿Qué se abre automáticamente?

- 🌐 **Portal OptiMon:** http://localhost:5000
- 📊 **Grafana:** http://localhost:3000 (admin/admin)

## 🚀 Primeros Pasos

1. **Portal OptiMon**
   - Configura credenciales Azure
   - Genera infraestructura automáticamente

2. **Grafana** 
   - Ve métricas de tu PC en tiempo real
   - Explora dashboards preconfigurados

## ❓ ¿Problemas?

- **UAC no aparece:** Ejecutar como administrador manualmente
- **Docker no funciona:** Instalar Docker Desktop
- **Puerto ocupado:** Reiniciar y ejecutar otra vez

## 💡 Consejo

**¡Solo hacer doble clic en INSTALAR_FACIL.bat y listo!**

¡Disfruta OptiMon! 🎉
"""
    
    with open(dist_dir / "INICIO_RAPIDO.txt", "w", encoding="utf-8") as f:
        f.write(quick_start)
    
    # Verificar archivos críticos
    print("🔍 Verificando archivos críticos...")
    critical_files = ["app.py", "requirements.txt", "docker-compose.yml"]
    missing_files = []
    
    for file in critical_files:
        if not (dist_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos críticos faltantes: {missing_files}")
        return False
    
    # Crear ZIP
    print("📦 Creando archivo ZIP...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(source_dir)
                zipf.write(file_path, arc_path)
                
    # Obtener tamaño del ZIP
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
    
    # Resumen final
    print()
    print("🎉" + "=" * 60 + "🎉")
    print("✅ PAQUETE DE DISTRIBUCIÓN CREADO EXITOSAMENTE")
    print("🎉" + "=" * 60 + "🎉")
    print()
    print(f"📦 Archivo ZIP: {zip_path.name}")
    print(f"📏 Tamaño: {zip_size:.2f} MB")
    print(f"📁 Directorio: {dist_dir.name}")
    print()
    print("🚀 CONTENIDO DEL PAQUETE:")
    print("   ✅ Scripts de instalación automática")
    print("   ✅ Portal web OptiMon completo")
    print("   ✅ Configuraciones Docker optimizadas")
    print("   ✅ Dashboards Grafana preconfigurados")
    print("   ✅ Documentación de usuario final")
    print("   ✅ Guía de inicio rápido")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("   1️⃣ Distribuir el archivo ZIP")
    print("   2️⃣ Usuario extrae el ZIP")
    print("   3️⃣ Usuario ejecuta INSTALAR_OPTIMON.ps1")
    print("   4️⃣ ¡Sistema listo en 30 segundos!")
    print()
    
    return True

if __name__ == "__main__":
    success = create_distribution_package()
    if success:
        print("🎯 ¡Paquete listo para distribución!")
    else:
        print("❌ Error creando el paquete")
    
    input("\nPresiona Enter para continuar...")