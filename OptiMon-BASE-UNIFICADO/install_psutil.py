#!/usr/bin/env python3
"""
Script para instalar psutil si no está disponible
"""

import subprocess
import sys

def install_psutil():
    """Instalar psutil usando pip"""
    try:
        import psutil
        print("✅ psutil ya está instalado")
        return True
    except ImportError:
        print("⚠️ psutil no encontrado. Instalando...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            print("✅ psutil instalado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando psutil: {e}")
            return False

if __name__ == "__main__":
    install_psutil()