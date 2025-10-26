#!/usr/bin/env python3
"""
Script para crear ejecutable de OptiMon Installer
Convierte el instalador GUI en un ejecutable .exe
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True, timeout=120)
            print("✅ PyInstaller instalado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error instalando PyInstaller: {e}")
            return False

def create_spec_file():
    """Crear archivo .spec personalizado para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['installer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('requirements.txt', '.'),
        ('docker-compose.yml', '.'),
        ('config', 'config'),
        ('core', 'core'),
        ('templates', 'templates'),
        ('.env.azure', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'requests',
        'subprocess',
        'socket',
        'threading',
        'webbrowser',
        'json',
        'pathlib',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OptiMon-Installer-v3.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("installer.spec", "w", encoding="utf-8") as f:
        f.write(spec_content.strip())
    
    print("✅ Archivo .spec creado")

def build_executable():
    """Construir el ejecutable usando PyInstaller"""
    print("🔨 Construyendo ejecutable...")
    
    try:
        # Limpiar builds anteriores
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")
        
        # Construir con PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "OptiMon-Installer-v3.0.0",
            "--add-data", "app.py;.",
            "--add-data", "requirements.txt;.",
            "--add-data", "docker-compose.yml;.",
            "--add-data", "config;config",
            "--add-data", "core;core", 
            "--add-data", "templates;templates",
            "--add-data", ".env.azure;.",
            "--hidden-import", "tkinter",
            "--hidden-import", "tkinter.ttk",
            "--hidden-import", "requests",
            "installer_gui.py"
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
        
        print("✅ Ejecutable creado exitosamente")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout construyendo ejecutable")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo ejecutable: {e}")
        print(f"Salida: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def create_installer_package():
    """Crear paquete final del instalador"""
    print("📦 Creando paquete final...")
    
    # Directorio de distribución
    dist_dir = Path("OptiMon-Installer-Final")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Copiar ejecutable
    exe_path = Path("dist/OptiMon-Installer-v3.0.0.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "OptiMon-Installer-v3.0.0.exe")
        print("✅ Ejecutable copiado")
    else:
        print("❌ Ejecutable no encontrado")
        return False
    
    # Crear README para el instalador
    readme_content = """
# 🚀 OptiMon - Instalador Ejecutable v3.0.0

## 📋 Instrucciones de Uso

### ⚡ Instalación Súper Fácil

1. **Doble clic** en `OptiMon-Installer-v3.0.0.exe`
2. **Seguir** las instrucciones en pantalla
3. **¡Listo!** OptiMon se instalará automáticamente

### 📋 Prerequisitos

- **Windows 10/11**
- **Docker Desktop** instalado
- **Conexión a Internet**

### 🎯 ¿Qué hace el instalador?

✅ Verifica prerequisitos automáticamente
✅ Instala dependencias Python necesarias  
✅ Configura servicios Docker (Prometheus, Grafana, AlertManager)
✅ Inicia portal web OptiMon
✅ Abre navegadores automáticamente

### 🌐 Accesos Después de Instalar

- **Portal OptiMon:** http://localhost:5000
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **AlertManager:** http://localhost:9093

### ❓ ¿Problemas?

- **Docker no funciona:** Instalar Docker Desktop
- **Permisos:** Ejecutar como administrador
- **Puertos ocupados:** Reiniciar y ejecutar otra vez

### 💡 Características

🖥️ **Monitoreo local** de tu computadora Windows
☁️ **Integración Azure** para infraestructura en la nube
📊 **Dashboards avanzados** con Grafana
🔔 **Sistema de alertas** configurado
🎯 **Interfaz gráfica** fácil de usar

---

**¡Disfruta OptiMon!** 🎉
"""
    
    with open(dist_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content.strip())
    
    print("✅ README creado")
    
    # Obtener tamaño del ejecutable
    exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    
    print(f"""
🎉 ¡INSTALADOR EJECUTABLE CREADO EXITOSAMENTE!

📦 Ubicación: {dist_dir.absolute()}
🚀 Ejecutable: OptiMon-Installer-v3.0.0.exe
📏 Tamaño: {exe_size:.2f} MB

💡 PARA DISTRIBUIR:
1. Comprimir la carpeta {dist_dir.name}
2. Distribuir el ZIP a usuarios finales
3. Usuario extrae y ejecuta el .exe

🎯 EXPERIENCIA DE USUARIO:
- Un solo doble clic para instalar todo
- Interfaz gráfica amigable
- Verificación automática de prerequisitos
- Instalación paso a paso con progreso visual
- Apertura automática de servicios
""")
    
    return True

def main():
    """Función principal para crear el ejecutable"""
    print("🚀" + "=" * 60 + "🚀")
    print("📦 GENERADOR DE INSTALADOR EJECUTABLE OPTIMON")
    print("🎯 Creando instalador .exe para usuario final")
    print("🚀" + "=" * 60 + "🚀")
    print()
    
    # Verificar archivos necesarios
    required_files = ["installer_gui.py", "app.py", "requirements.txt", "docker-compose.yml"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Paso 2: Construir ejecutable
    if not build_executable():
        return False
    
    # Paso 3: Crear paquete final
    if not create_installer_package():
        return False
    
    print("\n🎉 ¡Proceso completado exitosamente!")
    print("🚀 El instalador ejecutable está listo para distribución")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Error creando el instalador ejecutable")
        input("Presiona Enter para salir...")
        sys.exit(1)
    else:
        input("\nPresiona Enter para continuar...")