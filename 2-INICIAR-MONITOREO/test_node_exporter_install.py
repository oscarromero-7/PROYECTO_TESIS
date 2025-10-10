#!/usr/bin/env python3
"""
Script de prueba para instalación de Node Exporter
Prueba directa de la funcionalidad sin pasar por HTTP
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
import tempfile
from pathlib import Path

def install_node_exporter_direct():
    """Instala Windows Exporter directamente para Windows"""
    try:
        print("🚀 Iniciando instalación de Windows Exporter para Windows...")
        
        # URL del Windows Exporter para Windows
        version = "0.31.3"
        url = f"https://github.com/prometheus-community/windows_exporter/releases/download/v{version}/windows_exporter-{version}-amd64.exe"
        
        print(f"📥 Descargando desde: {url}")
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            exe_path_temp = os.path.join(temp_dir, "windows_exporter.exe")
            
            # Descargar archivo
            urllib.request.urlretrieve(url, exe_path_temp)
            print("✅ Descarga completada")
            
            # Crear directorio de destino
            install_dir = "C:\\optimon\\windows_exporter"
            os.makedirs(install_dir, exist_ok=True)
            
            # Copiar ejecutable
            exe_path_final = os.path.join(install_dir, "windows_exporter.exe")
            
            import shutil
            shutil.copy2(exe_path_temp, exe_path_final)
            print(f"✅ Ejecutable instalado en: {exe_path_final}")
            
            # Probar el ejecutable
            result = subprocess.run([exe_path_final, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Windows Exporter funcional: {result.stdout.strip()}")
                
                # Crear script de inicio
                start_script = os.path.join(install_dir, "start_windows_exporter.bat")
                with open(start_script, 'w') as f:
                    f.write(f'@echo off\n')
                    f.write(f'"{exe_path_final}" --web.listen-address=:9182\n')
                
                print(f"✅ Script de inicio creado: {start_script}")
                print("✅ Para iniciar manualmente: windows_exporter.exe --web.listen-address=:9182")
                print("✅ Métricas disponibles en: http://localhost:9182/metrics")
                
                return True
            else:
                print(f"❌ Error al probar el ejecutable: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error en la instalación: {e}")
        return False

def check_metrics():
    """Verifica métricas del sistema usando psutil"""
    try:
        import psutil
        print("\n📊 Verificando métricas del sistema...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"🖥️ CPU: {cpu_percent}%")
        
        # Memoria
        memory = psutil.virtual_memory()
        print(f"💾 Memoria: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)")
        
        # Disco
        disk = psutil.disk_usage('C:')
        print(f"💽 Disco C:: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)")
        
        # Procesos
        process_count = len(psutil.pids())
        print(f"⚙️ Procesos activos: {process_count}")
        
        print("✅ Métricas del sistema obtenidas correctamente")
        return True
        
    except ImportError:
        print("❌ psutil no está instalado")
        return False
    except Exception as e:
        print(f"❌ Error obteniendo métricas: {e}")
        return False

def main():
    print("🔧 PRUEBA DE FUNCIONALIDAD - Windows Exporter y Métricas")
    print("=" * 60)
    
    # Prueba 1: Métricas del sistema
    print("\n1️⃣ PRUEBA: Métricas del sistema")
    metrics_ok = check_metrics()
    
    # Prueba 2: Instalación de Windows Exporter
    print("\n2️⃣ PRUEBA: Instalación de Windows Exporter")
    install_ok = install_node_exporter_direct()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print(f"Métricas del sistema: {'✅ OK' if metrics_ok else '❌ FALLO'}")
    print(f"Instalación Windows Exporter: {'✅ OK' if install_ok else '❌ FALLO'}")
    
    if metrics_ok and install_ok:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("🌐 El sistema está listo para monitoreo desde el panel web")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
    
    return metrics_ok and install_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)