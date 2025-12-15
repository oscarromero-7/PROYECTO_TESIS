#!/usr/bin/env python3
"""
OptiMon - Configuración de Servicios de Monitoreo Standalone
Descarga e inicia Prometheus y Grafana sin Docker
"""

import os
import sys
import subprocess
import requests
import zipfile
import time
import threading
from pathlib import Path

def log(message):
    print(f"[OptiMon] {message}")

def download_file(url, filename):
    """Descargar archivo con barra de progreso"""
    log(f"Descargando {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgreso: {percent:.1f}%", end='', flush=True)
    print()
    log(f"✅ {filename} descargado")

def setup_prometheus():
    """Configurar Prometheus standalone"""
    prometheus_dir = Path("monitoring/prometheus")
    prometheus_dir.mkdir(parents=True, exist_ok=True)
    
    # URL para Windows x64
    prometheus_url = "https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.windows-amd64.zip"
    prometheus_zip = "prometheus.zip"
    
    if not Path("monitoring/prometheus/prometheus.exe").exists():
        download_file(prometheus_url, prometheus_zip)
        
        log("Extrayendo Prometheus...")
        with zipfile.ZipFile(prometheus_zip, 'r') as zip_ref:
            zip_ref.extractall("monitoring/")
        
        # Mover archivos
        extracted_dir = Path("monitoring/prometheus-2.45.0.windows-amd64")
        for item in extracted_dir.iterdir():
            item.rename(prometheus_dir / item.name)
        extracted_dir.rmdir()
        os.remove(prometheus_zip)
        
        log("✅ Prometheus configurado")

def setup_grafana():
    """Configurar Grafana standalone"""
    grafana_dir = Path("monitoring/grafana")
    grafana_dir.mkdir(parents=True, exist_ok=True)
    
    # URL para Windows x64
    grafana_url = "https://dl.grafana.com/oss/release/grafana-10.1.0.windows-amd64.zip"
    grafana_zip = "grafana.zip"
    
    if not Path("monitoring/grafana/bin/grafana-server.exe").exists():
        download_file(grafana_url, grafana_zip)
        
        log("Extrayendo Grafana...")
        with zipfile.ZipFile(grafana_zip, 'r') as zip_ref:
            zip_ref.extractall("monitoring/")
        
        # Mover archivos
        extracted_dir = Path("monitoring/grafana-10.1.0")
        for item in extracted_dir.iterdir():
            item.rename(grafana_dir / item.name)
        extracted_dir.rmdir()
        os.remove(grafana_zip)
        
        log("✅ Grafana configurado")

def start_prometheus():
    """Iniciar Prometheus"""
    log("Iniciando Prometheus...")
    prometheus_exe = Path("monitoring/prometheus/prometheus.exe")
    config_file = Path("config/prometheus/prometheus.yml")
    
    if prometheus_exe.exists() and config_file.exists():
        cmd = [
            str(prometheus_exe),
            f"--config.file={config_file.absolute()}",
            "--storage.tsdb.path=monitoring/prometheus/data",
            "--web.console.libraries=monitoring/prometheus/console_libraries",
            "--web.console.templates=monitoring/prometheus/consoles",
            "--web.listen-address=:9090"
        ]
        
        subprocess.Popen(cmd, cwd=Path.cwd())
        log("✅ Prometheus iniciado en http://localhost:9090")
        return True
    else:
        log("❌ No se encontró Prometheus o archivo de configuración")
        return False

def start_grafana():
    """Iniciar Grafana"""
    log("Iniciando Grafana...")
    grafana_exe = Path("monitoring/grafana/bin/grafana-server.exe")
    
    if grafana_exe.exists():
        # Configurar variables de entorno para Grafana
        env = os.environ.copy()
        env["GF_PATHS_DATA"] = str(Path("monitoring/grafana/data").absolute())
        env["GF_PATHS_LOGS"] = str(Path("monitoring/grafana/logs").absolute())
        env["GF_PATHS_PLUGINS"] = str(Path("monitoring/grafana/plugins").absolute())
        env["GF_PATHS_PROVISIONING"] = str(Path("monitoring/grafana/provisioning").absolute())
        
        # Crear directorios necesarios
        Path("monitoring/grafana/data").mkdir(exist_ok=True)
        Path("monitoring/grafana/logs").mkdir(exist_ok=True)
        
        subprocess.Popen([str(grafana_exe)], cwd=Path.cwd(), env=env)
        log("✅ Grafana iniciado en http://localhost:3000 (admin/admin)")
        return True
    else:
        log("❌ No se encontró Grafana")
        return False

def main():
    log("🚀 Configurando servicios de monitoreo standalone...")
    
    try:
        # Verificar si ya están corriendo
        try:
            response = requests.get("http://localhost:9090", timeout=2)
            log("✅ Prometheus ya está corriendo")
            prometheus_running = True
        except:
            prometheus_running = False
            
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            log("✅ Grafana ya está corriendo")
            grafana_running = True
        except:
            grafana_running = False
        
        if prometheus_running and grafana_running:
            log("🎉 Todos los servicios ya están corriendo")
            return
        
        # Configurar y iniciar servicios
        if not prometheus_running:
            setup_prometheus()
            start_prometheus()
            
        if not grafana_running:
            setup_grafana()
            start_grafana()
        
        log("⏳ Esperando 10 segundos para que los servicios inicien...")
        time.sleep(10)
        
        # Verificar que estén corriendo
        services_ok = True
        try:
            requests.get("http://localhost:9090", timeout=5)
            log("✅ Prometheus: http://localhost:9090")
        except:
            log("❌ Prometheus no responde")
            services_ok = False
            
        try:
            requests.get("http://localhost:3000", timeout=5)
            log("✅ Grafana: http://localhost:3000 (admin/admin)")
        except:
            log("❌ Grafana no responde")
            services_ok = False
        
        if services_ok:
            log("🎉 ¡Servicios de monitoreo iniciados exitosamente!")
            log("📊 OptiMon Dashboard: http://localhost:5000")
            log("💰 Optimización de Costos: http://localhost:5000/cost-optimization")
        else:
            log("⚠️  Algunos servicios pueden tardar más en iniciar")
            
    except Exception as e:
        log(f"❌ Error: {e}")
        log("🔧 Considera usar Docker Desktop para una configuración más fácil")

if __name__ == "__main__":
    main()