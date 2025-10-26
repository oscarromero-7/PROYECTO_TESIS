#!/usr/bin/env python3
"""
Crear ejecutable simple de OptiMon
"""

import subprocess
import sys
from pathlib import Path

def create_simple_exe():
    """Crear ejecutable simple"""
    
    print("🚀 Creando instalador ejecutable simple...")
    
    # Limpiar builds anteriores
    for path in ["build", "dist"]:
        if Path(path).exists():
            import shutil
            shutil.rmtree(path)
    
    # Crear ejecutable con PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "OptiMon-Installer-Simple-v3.0.0",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "installer_simple.py"
    ]
    
    subprocess.run(cmd, check=True, timeout=180)
    
    # Mover a directorio final
    dist_dir = Path("OptiMon-Simple-Final")
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    exe_path = Path("dist/OptiMon-Installer-Simple-v3.0.0.exe")
    if exe_path.exists():
        import shutil
        shutil.copy2(exe_path, dist_dir / "OptiMon-Installer-Simple-v3.0.0.exe")
        
        # Crear README
        readme = """
# 🚀 OptiMon - Instalador Simple v3.0.0

## 📋 Instrucciones

1. **Doble clic** en OptiMon-Installer-Simple-v3.0.0.exe
2. **Clic en "Instalar OptiMon"**
3. **Esperar** hasta que diga "Instalación completada"
4. **Clic en "Abrir Portal"**

## 📋 Prerequisitos

- Windows 10/11
- Docker Desktop instalado y ejecutándose

## 🌐 Accesos

- Portal: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)

¡Disfruta OptiMon! 🎉
"""
        
        (dist_dir / "README.txt").write_text(readme, encoding="utf-8")
        
        size = exe_path.stat().st_size / (1024 * 1024)
        print(f"""
🎉 ¡INSTALADOR SIMPLE CREADO!

📦 Ubicación: {dist_dir.absolute()}
🚀 Ejecutable: OptiMon-Installer-Simple-v3.0.0.exe  
📏 Tamaño: {size:.2f} MB

💡 VENTAJAS:
- Sin archivos temporales problemáticos
- Instalación más rápida
- Menos conflictos de permisos
- Interfaz más simple
""")
        return True
    
    return False

if __name__ == "__main__":
    success = create_simple_exe()
    if success:
        print("✅ Ejecutable simple creado exitosamente")
    else:
        print("❌ Error creando ejecutable")
    
    input("Presiona Enter para continuar...")