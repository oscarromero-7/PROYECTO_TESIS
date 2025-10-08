#!/usr/bin/env python3
"""
Script para arreglar problemas de codificación en archivos .bat
Reemplaza emojis y caracteres UTF-8 con equivalentes ASCII
"""

import os
import re

def fix_bat_file(filepath):
    """Arregla los problemas de codificación en un archivo .bat"""
    
    # Mapping de emojis a texto ASCII
    replacements = {
        '🚀': '[OptiMon]',
        '📋': '[INFO]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '📦': '[INFO]',
        '🔐': '[INFO]',
        '⚙️': '[INFO]',
        '🐳': '[INFO]',
        '🔍': '[INFO]',
        '🤖': '[INFO]',
        '🔄': '[INFO]',
        '🎉': '[SUCCESS]',
        '📊': '[INFO]',
        '🛠️': '[INFO]',
        '📖': '[INFO]',
        '🆘': '[INFO]',
        '🔒': '[INFO]',
        '📁': '[INFO]',
        '💡': '[TIP]',
        '🌐': '[INFO]',
        '💻': '[INFO]',
        # Caracteres especiales
        '•': '-',
        '─': '-',
        '║': '|',
        '╚': '+',
        '╝': '+',
        '╗': '+',
        '╔': '+',
        '═': '=',
        '│': '|',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
        '┌': '+',
        '┐': '+',
        '└': '+',
        '┘': '+',
        # Acentos y tildes
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        '¿': '', '¡': '', 
        # Otros caracteres problemáticos
        ''': "'", ''': "'", '"': '"', '"': '"',
        '–': '-', '—': '-',
    }
    
    print(f"Arreglando {filepath}...")
    
    try:
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Hacer reemplazos
        for emoji, replacement in replacements.items():
            content = content.replace(emoji, replacement)
        
        # Escribir archivo con codificación ASCII
        with open(filepath, 'w', encoding='cp1252', errors='ignore') as f:
            f.write(content)
            
        print(f"✓ {filepath} arreglado")
        
    except Exception as e:
        print(f"✗ Error procesando {filepath}: {e}")

def fix_python_file(filepath):
    """Arregla los problemas de codificación en un archivo .py"""
    
    # Mapping de emojis a texto ASCII para Python
    replacements = {
        '🚀': '[OptiMon]',
        '📋': '[INFO]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '📦': '[INFO]',
        '🔐': '[INFO]',
        '⚙️': '[INFO]',
        '🐳': '[INFO]',
        '🔍': '[INFO]',
        '🤖': '[INFO]',
        '🔄': '[INFO]',
        '🎉': '[SUCCESS]',
        '📊': '[INFO]',
        '🛠️': '[INFO]',
        '📖': '[INFO]',
        '🆘': '[INFO]',
        '🔒': '[INFO]',
        '📁': '[INFO]',
        '💡': '[TIP]',
        '🌐': '[INFO]',
        '💻': '[INFO]',
        '☁️': '[CLOUD]',
        '🖥️': '[SERVER]',
        '🏗️': '[BUILD]',
        '🔧': '[CONFIG]',
        '⚡': '[FAST]',
        '🚨': '[ALERT]',
        # Caracteres especiales
        '•': '-',
        '─': '-',
        '║': '|',
        # Acentos y tildes
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        '¿': '', '¡': '', 
        # Otros caracteres problemáticos
        ''': "'", ''': "'", '"': '"', '"': '"',
        '–': '-', '—': '-',
    }
    
    print(f"Arreglando {filepath}...")
    
    try:
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Hacer reemplazos
        for emoji, replacement in replacements.items():
            content = content.replace(emoji, replacement)
        
        # Escribir archivo con codificación UTF-8 (para Python)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✓ {filepath} arreglado")
        
    except Exception as e:
        print(f"✗ Error procesando {filepath}: {e}")

def main():
    """Función principal"""
    
    # Archivos .bat a procesar
    bat_files = [
        'deploy.bat',
        'make.bat', 
        'add_server.bat'
    ]
    
    # Archivos Python a procesar
    python_files = [
        'scripts/auto_setup.py',
        'scripts/setup_aws_monitoring.py',
        'scripts/setup_azure_monitoring.py',
        'scripts/setup_prometheus.py'
    ]
    
    print("🔧 Arreglando problemas de codificación en archivos .bat y .py")
    print("=" * 60)
    
    for bat_file in bat_files:
        if os.path.exists(bat_file):
            fix_bat_file(bat_file)
        else:
            print(f"⚠ {bat_file} no encontrado")
    
    for py_file in python_files:
        if os.path.exists(py_file):
            fix_python_file(py_file)
        else:
            print(f"⚠ {py_file} no encontrado")
    
    print("\n✅ Proceso completado")
    print("\nLos archivos .bat ahora deberían mostrar texto correctamente en CMD")
    print("Los archivos .py ahora deberían ejecutarse sin errores de codificación")

if __name__ == "__main__":
    main()