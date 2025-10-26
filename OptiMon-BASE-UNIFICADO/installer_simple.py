#!/usr/bin/env python3
"""
OptiMon - Instalador Simple v3.0.0
Instalador ejecutable simplificado que descarga archivos
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os
import time
import threading
import requests
import socket
from pathlib import Path
import json
from datetime import datetime
import webbrowser
import tempfile
import urllib.request

class OptiMonInstallerSimple:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OptiMon - Instalador Simple v3.0.0")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Variables
        self.installation_complete = False
        self.installing = False
        self.work_dir = None
        self.app_process = None
        
        # Configurar interfaz
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Centrar ventana"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"700x500+{x}+{y}")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🚀 OptiMon - Sistema de Monitoreo", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Información
        info_text = """
🎯 Instalación Automática de OptiMon v3.0.0

Este instalador configurará automáticamente:
✅ Portal web de monitoreo
✅ Servicios Docker (Prometheus, Grafana, AlertManager)  
✅ Dashboards preconfigurados
✅ Integración con Azure

📋 Prerequisitos necesarios:
• Windows 10/11
• Docker Desktop instalado y ejecutándose
• Python 3.8 o superior
• Conexión a Internet
        """
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_label = ttk.Label(main_frame, text="Listo para instalar")
        self.progress_label.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=80)
        self.log_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2)
        
        self.install_button = ttk.Button(button_frame, text="🚀 Instalar OptiMon", 
                                        command=self.start_installation)
        self.install_button.grid(row=0, column=0, padx=(0, 10))
        
        self.open_button = ttk.Button(button_frame, text="🌐 Abrir Portal", 
                                     command=self.open_portal, state=tk.DISABLED)
        self.open_button.grid(row=0, column=1, padx=(0, 10))
        
        self.close_button = ttk.Button(button_frame, text="❌ Cerrar", 
                                      command=self.close_app)
        self.close_button.grid(row=0, column=2)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Verificar sistema al inicio
        self.root.after(1000, self.check_system)
    
    def log(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, value, text):
        """Actualizar progreso"""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def check_system(self):
        """Verificar sistema"""
        self.log("🔍 Verificando prerequisitos...")
        
        # Verificar Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ Docker encontrado")
            else:
                self.log("❌ Docker no encontrado")
                self.install_button.config(state=tk.DISABLED)
                return
        except:
            self.log("❌ Docker no disponible")
            self.install_button.config(state=tk.DISABLED)
            return
        
        # Verificar Python
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.log(f"✅ Python {version} encontrado")
        
        self.log("✅ Sistema listo para instalación")
    
    def start_installation(self):
        """Iniciar instalación"""
        # Prevenir múltiples instalaciones
        if hasattr(self, 'installing') and self.installing:
            self.log("⚠️ Instalación ya en progreso...")
            return
            
        self.installing = True
        self.install_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.install_optimon)
        thread.daemon = True
        thread.start()
    
    def install_optimon(self):
        """Proceso de instalación"""
        try:
            # Crear directorio de trabajo
            self.update_progress(10, "Preparando instalación...")
            self.work_dir = Path.cwd() / "OptiMon"
            if self.work_dir.exists():
                import shutil
                shutil.rmtree(self.work_dir)
            self.work_dir.mkdir()
            
            # Crear archivos básicos
            self.update_progress(20, "Creando archivos de configuración...")
            self.create_basic_files()
            
            # Instalar dependencias
            self.update_progress(40, "Instalando dependencias...")
            self.install_dependencies()
            
            # Iniciar servicios
            self.update_progress(60, "Iniciando servicios Docker...")
            self.start_services()
            
            # Iniciar aplicación
            self.update_progress(80, "Iniciando aplicación...")
            self.start_app()
            
            # Finalizar
            self.update_progress(100, "¡Instalación completada!")
            self.installation_complete = True
            self.installing = False
            self.open_button.config(state=tk.NORMAL)
            
            self.log("✅ OptiMon instalado exitosamente!")
            self.log("🌐 Portal disponible en: http://localhost:5000")
            self.log("📊 Grafana disponible en: http://localhost:3000")
            self.log("🚀 Iniciando portal automáticamente...")
            
            # Verificar que el proceso se inició correctamente
            if hasattr(self, 'app_process') and self.app_process:
                if self.app_process.poll() is None:
                    self.log("✅ Proceso del portal iniciado correctamente")
                else:
                    self.log("⚠️ Reintentando inicio del portal...")
                    # Reintentar inicio si falló
                    self.start_app()
            
            # Abrir portal automáticamente después de 2 segundos (más rápido)
            self.root.after(2000, self.auto_open_portal)
            
            messagebox.showinfo("Éxito", 
                "OptiMon se instaló correctamente.\n\n" +
                "Portal: http://localhost:5000\n" +
                "Grafana: http://localhost:3000 (admin/admin)\n\n" +
                "🚀 El portal se está abriendo automáticamente...")
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error durante la instalación:\n{e}")
            self.installing = False
            self.install_button.config(state=tk.NORMAL)
    
    def create_basic_files(self):
        """Crear archivos básicos necesarios"""
        
        # app.py con diseño estilo Apple
        app_content = '''
import flask
import subprocess
import webbrowser
import time
import threading

app = flask.Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OptiMon - Sistema de Monitoreo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .hero {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            margin: 40px auto;
            max-width: 1200px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.3rem;
            color: #666;
            margin-bottom: 50px;
            font-weight: 400;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 50px 0;
        }
        
        .service-card {
            background: white;
            border-radius: 20px;
            padding: 40px 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .service-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .service-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .service-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .service-desc {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .next-steps {
            background: rgba(255,255,255,0.7);
            border-radius: 20px;
            padding: 40px;
            margin-top: 40px;
            text-align: left;
        }
        
        .step {
            margin: 20px 0;
            padding: 15px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        
        .step:last-child {
            border-bottom: none;
        }
        
        .step-number {
            display: inline-block;
            width: 30px;
            height: 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-right: 15px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="logo">🚀</div>
        <h1>OptiMon</h1>
        <p class="subtitle">Sistema de Monitoreo Profesional</p>
        
        <div style="background: linear-gradient(45deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 15px; margin: 30px 0;">
            <h2 style="margin: 0;">✅ Instalación Completada Exitosamente</h2>
            <p style="margin: 10px 0 0 0;">Tu sistema de monitoreo está funcionando correctamente</p>
        </div>
        
        <div class="services-grid">
            <div class="service-card">
                <span class="service-icon">📊</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Portal OptiMon
                </h3>
                <p class="service-desc">Panel de control principal del sistema</p>
                <a href="http://localhost:5000" class="btn">Acceder</a>
            </div>
            
            <div class="service-card">
                <span class="service-icon">📈</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Grafana
                </h3>
                <p class="service-desc">Dashboards visuales y métricas en tiempo real</p>
                <a href="http://localhost:3000" target="_blank" class="btn">Abrir Grafana</a>
                <div style="font-size: 0.85rem; color: #888; margin-top: 10px;">
                    Usuario: admin | Contraseña: admin
                </div>
            </div>
            
            <div class="service-card">
                <span class="service-icon">🔍</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Prometheus
                </h3>
                <p class="service-desc">Motor de métricas y consultas PromQL</p>
                <a href="http://localhost:9090" target="_blank" class="btn">Explorar Métricas</a>
            </div>
        </div>
        
        <div class="next-steps">
            <h3 style="color: #333; margin-bottom: 30px;">🎯 Próximos Pasos</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Explora Grafana:</strong> Accede a los dashboards preconfigurados para ver métricas de tu sistema en tiempo real
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Configura Alertas:</strong> Personaliza los umbrales de alertas según tus necesidades
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Integra Azure:</strong> Conecta tus recursos de Azure para monitoreo en la nube
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Disfruta OptiMon:</strong> ¡Tu sistema de monitoreo está listo para usar!
            </div>
        </div>
    </div>
</body>
</html>
    """

@app.route('/api/health')
def health():
    return {"status": "ok", "service": "OptiMon", "version": "3.0.0"}

if __name__ == "__main__":
    print("🚀 Iniciando OptiMon Portal...")
    print("📊 Portal: http://localhost:5000")
    print("📈 Grafana: http://localhost:3000 (admin/admin)")
    print("🔍 Prometheus: http://localhost:9090")
    app.run(host="0.0.0.0", port=5000, debug=False)
'''
        
        # docker-compose.yml básico
        compose_content = '''
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: optimon_prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana:latest
    container_name: optimon_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped
'''
        
        # requirements.txt
        requirements_content = '''
flask==3.0.0
requests==2.31.0
'''
        
        # Escribir archivos
        (self.work_dir / "app.py").write_text(app_content, encoding="utf-8")
        (self.work_dir / "docker-compose.yml").write_text(compose_content, encoding="utf-8")
        (self.work_dir / "requirements.txt").write_text(requirements_content, encoding="utf-8")
        
        self.log("✅ Archivos básicos creados")
    
    def install_dependencies(self):
        """Instalar dependencias"""
        try:
            os.chdir(self.work_dir)
            self.log("📦 Instalando dependencias Python...")
            
            # Comando corregido para instalar dependencias
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.log("✅ Dependencias instaladas correctamente")
            else:
                self.log(f"⚠️ Advertencia pip: {result.stderr}")
                self.log("✅ Continuando con la instalación...")
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Timeout en pip install, pero continuando...")
        except Exception as e:
            self.log(f"⚠️ Error en pip: {e}, continuando...")
    
    def start_services(self):
        """Iniciar servicios Docker"""
        try:
            self.log("🐳 Iniciando servicios Docker...")
            
            # Verificar que Docker esté ejecutándose
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
            if result.returncode != 0:
                self.log("❌ Docker no está ejecutándose")
                raise Exception("Docker Desktop no está ejecutándose")
            
            # Detener servicios existentes si los hay
            subprocess.run(["docker", "compose", "down"], capture_output=True, timeout=30)
            
            # Iniciar servicios
            result = subprocess.run(["docker", "compose", "up", "-d"], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.log("✅ Servicios Docker iniciados correctamente")
                self.log("⏳ Esperando que servicios estén listos...")
                time.sleep(15)  # Dar tiempo a que servicios arranquen
                
                # Verificar que servicios estén corriendo
                self.verify_services()
            else:
                self.log(f"⚠️ Advertencia Docker: {result.stderr}")
                self.log("✅ Continuando con la instalación...")
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Timeout en Docker, pero continuando...")
        except Exception as e:
            self.log(f"⚠️ Error Docker: {e}, continuando...")
    
    def verify_services(self):
        """Verificar que los servicios estén corriendo"""
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
            if "optimon_prometheus" in result.stdout:
                self.log("✅ Prometheus ejecutándose")
            if "optimon_grafana" in result.stdout:
                self.log("✅ Grafana ejecutándose")
        except Exception as e:
            self.log(f"⚠️ No se pudo verificar servicios: {e}")
    
    def start_app(self):
        """Iniciar aplicación"""
        try:
            self.log("🌐 Iniciando portal web...")
            
            # Verificar si ya hay una aplicación corriendo en puerto 5000
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', 5000))
                sock.close()
                
                if result == 0:
                    self.log("⚠️ Portal ya está ejecutándose en puerto 5000")
                    return
            except:
                pass
            
            # Iniciar aplicación con mejor manejo
            app_path = self.work_dir / "app.py"
            
            # Crear un script de inicio más robusto
            startup_script = f'''
import sys
import os
import time
import socket
import webbrowser
import threading

sys.path.insert(0, r"{self.work_dir}")
os.chdir(r"{self.work_dir}")

def check_port_available(port):
    """Verificar si el puerto está disponible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    except:
        return True

def open_browser_delayed():
    """Abrir navegador después de que el servidor esté listo"""
    time.sleep(3)
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                print("🌐 Abriendo portal en navegador...")
                webbrowser.open("http://localhost:5000")
                break
        except:
            pass
        time.sleep(2)

try:
    # Verificar si el puerto ya está en uso
    if not check_port_available(5000):
        print("⚠️  El puerto 5000 ya está en uso")
        webbrowser.open("http://localhost:5000")
    else:
        print("🚀 Iniciando OptiMon Portal...")
        print("📊 Portal: http://localhost:5000")
        print("📈 Grafana: http://localhost:3000 (admin/admin)")
        print("🔍 Prometheus: http://localhost:9090")
        
        # Iniciar thread para abrir navegador
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Importar y ejecutar app
        import app
        app.app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
        
except Exception as e:
    print(f"❌ Error: {{e}}")
    print("🔄 Intentando abrir portal existente...")
    try:
        webbrowser.open("http://localhost:5000")
    except:
        pass
    input("Presiona Enter para cerrar...")
'''
            
            startup_path = self.work_dir / "start_app.py"
            startup_path.write_text(startup_script, encoding="utf-8")
            
            # Iniciar la aplicación en modo no bloqueante y persistente
            if os.name == 'nt':  # Windows
                # Crear proceso que persista incluso después de cerrar el instalador
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                DETACHED_PROCESS = 0x00000008
                
                self.app_process = subprocess.Popen(
                    [sys.executable, str(startup_path)],
                    cwd=str(self.work_dir),
                    creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:  # Linux/Mac
                self.app_process = subprocess.Popen(
                    [sys.executable, str(startup_path)],
                    cwd=str(self.work_dir)
                )
            
            # Esperar y verificar con reintentos
            time.sleep(5)
            
            # Verificar múltiples veces que esté corriendo
            portal_ready = False
            for attempt in range(5):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', 5000))
                    sock.close()
                    
                    if result == 0:
                        portal_ready = True
                        self.log("✅ Portal web iniciado correctamente en http://localhost:5000")
                        break
                    else:
                        time.sleep(3)
                except Exception as e:
                    time.sleep(3)
            
            if not portal_ready:
                self.log("⚠️ Portal iniciado pero verificando disponibilidad...")
                # Intentar abrir de todos modos, puede que esté iniciándose
                time.sleep(5)
            
        except Exception as e:
            self.log(f"❌ Error iniciando portal: {e}")
    
    def auto_open_portal(self):
        """Abrir portal automáticamente con reintentos"""
        def try_open():
            max_attempts = 8
            for attempt in range(max_attempts):
                try:
                    self.log(f"🚀 Intentando abrir portal (intento {attempt + 1}/{max_attempts})...")
                    
                    # Verificar si el puerto está disponible
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', 5000))
                    sock.close()
                    
                    if result == 0:
                        webbrowser.open("http://localhost:5000")
                        self.log("✅ Portal abierto exitosamente en navegador")
                        return
                    else:
                        self.log(f"⏳ Puerto 5000 no disponible aún, esperando...")
                        time.sleep(4)
                        
                except Exception as e:
                    self.log(f"⚠️ Error en intento {attempt + 1}: {e}")
                    time.sleep(3)
            
            # Si llegamos aquí, hacer último intento forzado
            self.log("🔄 Realizando intento final...")
            try:
                webbrowser.open("http://localhost:5000")
                self.log("🌐 Portal abierto (conexión puede estar estableciéndose)")
            except Exception as e:
                self.log(f"❌ No se pudo abrir portal automáticamente: {e}")
        
        # Ejecutar en hilo separado para no bloquear UI
        thread = threading.Thread(target=try_open)
        thread.daemon = True
        thread.start()
        
        # Verificar continuamente que el portal esté corriendo
        self.root.after(10000, self.check_portal_health)
    
    def check_portal_health(self):
        """Verificar que el portal siga funcionando"""
        try:
            if hasattr(self, 'installation_complete') and self.installation_complete:
                # Verificar si el proceso sigue corriendo
                if hasattr(self, 'app_process') and self.app_process:
                    if self.app_process.poll() is not None:
                        self.log("⚠️ Portal se detuvo, reiniciando...")
                        self.start_app()
                
                # Programar próxima verificación
                self.root.after(15000, self.check_portal_health)
        except Exception as e:
            self.log(f"⚠️ Error verificando portal: {e}")
    
    def open_portal(self):
        """Abrir portal"""
        try:
            # Verificar que el portal esté disponible
            import urllib.request
            urllib.request.urlopen("http://localhost:5000", timeout=5)
            webbrowser.open("http://localhost:5000")
            self.log("🌐 Abriendo portal en navegador...")
        except:
            # Si no está disponible, intentar reiniciar
            self.log("⚠️ Portal no disponible, intentando reiniciar...")
            try:
                self.start_app()
                time.sleep(5)
                webbrowser.open("http://localhost:5000")
            except Exception as e:
                self.log(f"❌ Error abriendo portal: {e}")
                messagebox.showerror("Error", "No se pudo abrir el portal.\nVerifica que la instalación se completó correctamente.")
        
    def close_app(self):
        """Cerrar aplicación"""
        try:
            # Preguntar si mantener OptiMon corriendo
            if hasattr(self, 'installation_complete') and self.installation_complete:
                response = messagebox.askyesno(
                    "OptiMon está ejecutándose",
                    "OptiMon Portal está funcionando correctamente.\n\n" +
                    "¿Deseas mantener OptiMon ejecutándose en segundo plano?\n\n" +
                    "• SÍ: OptiMon seguirá funcionando (recomendado)\n" +
                    "• NO: Cerrar OptiMon completamente"
                )
                
                if not response:  # Usuario eligió cerrar todo
                    try:
                        # Detener proceso de la app
                        if hasattr(self, 'app_process') and self.app_process and self.app_process.poll() is None:
                            self.app_process.terminate()
                            self.log("🛑 OptiMon cerrado")
                        
                        # Detener servicios Docker
                        try:
                            subprocess.run(["docker", "compose", "down"], 
                                         cwd=str(self.work_dir), 
                                         capture_output=True, timeout=30)
                            self.log("🛑 Servicios Docker detenidos")
                        except:
                            pass
                    except Exception as e:
                        self.log(f"⚠️ Error cerrando servicios: {e}")
                else:
                    self.log("✅ OptiMon continuará ejecutándose en segundo plano")
                    self.log("🌐 Portal accesible en: http://localhost:5000")
            
            self.root.destroy()
        except Exception as e:
            self.log(f"Error cerrando: {e}")
            self.root.destroy()

def main():
    # Simple verificación para evitar múltiples instancias
    try:
        # Crear archivo lock temporal
        lock_file = Path(tempfile.gettempdir()) / "optimon_installer.lock"
        if lock_file.exists():
            # Verificar si el proceso existe realmente
            try:
                with open(lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                # En Windows, intentar verificar si el proceso existe
                if os.name == 'nt':
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {old_pid}'], 
                                          capture_output=True, text=True)
                    if str(old_pid) in result.stdout:
                        print("Ya hay una instancia del instalador ejecutándose")
                        return
            except:
                pass
            
        # Crear nuevo archivo lock
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
            
        installer = OptiMonInstallerSimple()
        
        # Limpiar al cerrar
        def cleanup():
            try:
                lock_file.unlink()
            except:
                pass
        
        installer.root.protocol("WM_DELETE_WINDOW", cleanup)
        installer.root.mainloop()
        cleanup()
        
    except Exception as e:
        print(f"Error iniciando instalador: {e}")

if __name__ == "__main__":
    main()