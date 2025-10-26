#!/usr/bin/env python3
"""
OptiMon - Instalador Gráfico v3.0.0
Instalador ejecutable con interfaz gráfica para usuario final
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
import zipfile
import shutil

class OptiMonInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OptiMon - Instalador v3.0.0")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Variables de estado
        self.install_path = Path.cwd()
        self.installation_complete = False
        self.services_running = False
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
    
    def setup_style(self):
        """Configurar el estilo de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2E86AB')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#A23B72')
        style.configure('Success.TLabel', font=('Arial', 10, 'bold'), foreground='#28A745')
        style.configure('Error.TLabel', font=('Arial', 10, 'bold'), foreground='#DC3545')
        style.configure('Warning.TLabel', font=('Arial', 10, 'bold'), foreground='#FFC107')
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🚀 OptiMon - Sistema Unificado de Monitoreo", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Instalación Automática v3.0.0", style='Header.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="📋 Información del Sistema", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Información del sistema
        self.system_info = ttk.Label(info_frame, text="Verificando sistema...")
        self.system_info.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress_frame = ttk.LabelFrame(main_frame, text="🔄 Progreso de Instalación", padding="10")
        self.progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Listo para instalar")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="📄 Log de Instalación", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        self.install_button = ttk.Button(button_frame, text="🚀 Instalar OptiMon", command=self.start_installation)
        self.install_button.grid(row=0, column=0, padx=(0, 10))
        
        self.open_portal_button = ttk.Button(button_frame, text="🌐 Abrir Portal", command=self.open_portal, state=tk.DISABLED)
        self.open_portal_button.grid(row=0, column=1, padx=(0, 10))
        
        self.open_grafana_button = ttk.Button(button_frame, text="📊 Abrir Grafana", command=self.open_grafana, state=tk.DISABLED)
        self.open_grafana_button.grid(row=0, column=2, padx=(0, 10))
        
        self.close_button = ttk.Button(button_frame, text="❌ Cerrar", command=self.close_application)
        self.close_button.grid(row=0, column=3)
        
        # Configurar grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Verificar sistema al inicio
        self.root.after(1000, self.check_system)
    
    def log(self, message, level="INFO"):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, value, text):
        """Actualizar barra de progreso"""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def check_system(self):
        """Verificar prerequisitos del sistema"""
        self.log("🔍 Verificando prerequisitos del sistema...")
        
        checks = []
        
        # Verificar Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                checks.append(("✅", f"Docker: {version}"))
                self.log(f"Docker encontrado: {version}")
            else:
                checks.append(("❌", "Docker: No encontrado"))
                self.log("Docker no encontrado", "ERROR")
        except Exception as e:
            checks.append(("❌", "Docker: Error"))
            self.log(f"Error verificando Docker: {e}", "ERROR")
        
        # Verificar Python
        try:
            version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            checks.append(("✅", f"Python: {version}"))
            self.log(f"Python encontrado: {version}")
        except Exception as e:
            checks.append(("❌", "Python: Error"))
            self.log(f"Error verificando Python: {e}", "ERROR")
        
        # Verificar puertos
        ports_to_check = [5000, 3000, 9090, 9093]
        for port in ports_to_check:
            if self.check_port(port):
                checks.append(("⚠️", f"Puerto {port}: En uso"))
                self.log(f"Puerto {port} está en uso", "WARNING")
            else:
                checks.append(("✅", f"Puerto {port}: Disponible"))
        
        # Actualizar información del sistema
        info_text = "\n".join([f"{status} {desc}" for status, desc in checks])
        self.system_info.config(text=info_text)
        
        # Verificar si podemos instalar
        docker_ok = any("Docker" in desc and "✅" in status for status, desc in checks)
        python_ok = any("Python" in desc and "✅" in status for status, desc in checks)
        
        if docker_ok and python_ok:
            self.install_button.config(state=tk.NORMAL)
            self.log("✅ Sistema listo para instalación")
        else:
            self.install_button.config(state=tk.DISABLED)
            self.log("❌ Sistema no cumple los prerequisitos", "ERROR")
    
    def check_port(self, port):
        """Verificar si un puerto está en uso"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def start_installation(self):
        """Iniciar el proceso de instalación"""
        self.install_button.config(state=tk.DISABLED)
        self.log("🚀 Iniciando instalación de OptiMon...")
        
        # Ejecutar instalación en hilo separado
        thread = threading.Thread(target=self.install_optimon)
        thread.daemon = True
        thread.start()
    
    def install_optimon(self):
        """Proceso principal de instalación"""
        try:
            # Paso 1: Instalar dependencias Python
            self.update_progress(10, "Instalando dependencias Python...")
            self.install_dependencies()
            
            # Paso 2: Limpiar servicios previos
            self.update_progress(30, "Limpiando servicios previos...")
            self.cleanup_services()
            
            # Paso 3: Iniciar servicios Docker
            self.update_progress(50, "Iniciando servicios Docker...")
            self.start_docker_services()
            
            # Paso 4: Esperar servicios
            self.update_progress(70, "Esperando servicios...")
            self.wait_for_services()
            
            # Paso 5: Iniciar portal web
            self.update_progress(85, "Iniciando portal web...")
            self.start_web_portal()
            
            # Paso 6: Verificación final
            self.update_progress(95, "Verificación final...")
            self.verify_installation()
            
            # Completado
            self.update_progress(100, "¡Instalación completada!")
            self.installation_complete = True
            self.enable_action_buttons()
            
            self.log("🎉 ¡Instalación completada exitosamente!")
            messagebox.showinfo("Éxito", "OptiMon se ha instalado correctamente.\n\nPuede acceder al portal en http://localhost:5000")
            
        except Exception as e:
            self.log(f"❌ Error durante la instalación: {e}", "ERROR")
            messagebox.showerror("Error", f"Error durante la instalación:\n{e}")
            self.install_button.config(state=tk.NORMAL)
    
    def install_dependencies(self):
        """Instalar dependencias Python"""
        self.log("📦 Instalando dependencias Python...")
        
        try:
            # Actualizar pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                          check=True, capture_output=True, timeout=60)
            
            # Instalar requirements
            if Path("requirements.txt").exists():
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, timeout=120)
            else:
                # Instalar dependencias básicas
                deps = ["flask", "requests", "paramiko", "azure-mgmt-compute", 
                       "azure-mgmt-network", "azure-mgmt-resource", "azure-identity"]
                subprocess.run([sys.executable, "-m", "pip", "install"] + deps, 
                              check=True, capture_output=True, timeout=120)
            
            self.log("✅ Dependencias instaladas correctamente")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout instalando dependencias")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error instalando dependencias: {e}")
    
    def cleanup_services(self):
        """Limpiar servicios previos"""
        self.log("🧹 Limpiando servicios previos...")
        
        try:
            # Detener containers Docker
            subprocess.run(["docker", "compose", "down", "--remove-orphans"], 
                          capture_output=True, timeout=30)
            
            # Terminar procesos Python previos
            try:
                subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *app.py*"], 
                              capture_output=True, timeout=10)
            except:
                pass
            
            self.log("✅ Servicios previos limpiados")
            
        except Exception as e:
            self.log(f"⚠️ Advertencia limpiando servicios: {e}", "WARNING")
    
    def start_docker_services(self):
        """Iniciar servicios Docker"""
        self.log("🐳 Iniciando servicios Docker...")
        
        try:
            if not Path("docker-compose.yml").exists():
                raise Exception("Archivo docker-compose.yml no encontrado")
            
            result = subprocess.run(["docker", "compose", "up", "-d"], 
                                  check=True, capture_output=True, timeout=120)
            
            self.log("✅ Servicios Docker iniciados")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout iniciando servicios Docker")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error iniciando servicios Docker: {e}")
    
    def wait_for_services(self):
        """Esperar a que los servicios estén listos"""
        self.log("⏳ Esperando a que los servicios estén listos...")
        
        services = [
            ("Prometheus", "http://localhost:9090/-/healthy"),
            ("Grafana", "http://localhost:3000/api/health"),
            ("AlertManager", "http://localhost:9093/-/healthy")
        ]
        
        max_attempts = 30
        for name, url in services:
            self.log(f"🔄 Verificando {name}...")
            
            for attempt in range(max_attempts):
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.log(f"✅ {name} está listo")
                        break
                except:
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                    else:
                        self.log(f"⚠️ {name} no responde, pero continuando...", "WARNING")
    
    def start_web_portal(self):
        """Iniciar portal web OptiMon"""
        self.log("🌐 Iniciando portal web OptiMon...")
        
        try:
            if not Path("app.py").exists():
                raise Exception("Archivo app.py no encontrado")
            
            # Iniciar portal en proceso separado
            subprocess.Popen([sys.executable, "app.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Esperar a que el portal inicie
            time.sleep(5)
            
            self.log("✅ Portal web iniciado")
            
        except Exception as e:
            raise Exception(f"Error iniciando portal web: {e}")
    
    def verify_installation(self):
        """Verificar que todo esté funcionando"""
        self.log("🔍 Verificando instalación...")
        
        # Verificar portal OptiMon
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ Portal OptiMon funcionando")
                self.services_running = True
            else:
                self.log("⚠️ Portal OptiMon no responde correctamente", "WARNING")
        except:
            self.log("❌ Portal OptiMon no accesible", "ERROR")
    
    def enable_action_buttons(self):
        """Habilitar botones de acción"""
        if self.services_running:
            self.open_portal_button.config(state=tk.NORMAL)
            self.open_grafana_button.config(state=tk.NORMAL)
    
    def open_portal(self):
        """Abrir portal OptiMon en navegador"""
        webbrowser.open("http://localhost:5000")
        self.log("🌐 Portal OptiMon abierto en navegador")
    
    def open_grafana(self):
        """Abrir Grafana en navegador"""
        webbrowser.open("http://localhost:3000")
        self.log("📊 Grafana abierto en navegador")
    
    def close_application(self):
        """Cerrar aplicación"""
        if messagebox.askokcancel("Salir", "¿Desea cerrar el instalador?"):
            self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

def extract_embedded_files():
    """Extraer archivos embebidos del ejecutable"""
    import tempfile
    import sys
    
    # Obtener directorio donde está el ejecutable
    if getattr(sys, 'frozen', False):
        # Ejecutándose como ejecutable
        bundle_dir = sys._MEIPASS
        exe_dir = Path(sys.executable).parent
    else:
        # Ejecutándose como script
        bundle_dir = Path(__file__).parent
        exe_dir = Path.cwd()
    
    # Crear directorio temporal para OptiMon
    optimon_dir = exe_dir / "OptiMon-Temp"
    if optimon_dir.exists():
        shutil.rmtree(optimon_dir)
    
    optimon_dir.mkdir()
    
    # Copiar archivos desde el bundle
    files_to_copy = [
        "app.py",
        "requirements.txt", 
        "docker-compose.yml",
        ".env.azure"
    ]
    
    dirs_to_copy = [
        "config",
        "core",
        "templates"
    ]
    
    # Copiar archivos
    for file in files_to_copy:
        src = Path(bundle_dir) / file
        if src.exists():
            shutil.copy2(src, optimon_dir / file)
    
    # Copiar directorios
    for dir_name in dirs_to_copy:
        src_dir = Path(bundle_dir) / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, optimon_dir / dir_name)
    
    return optimon_dir

def main():
    """Función principal"""
    try:
        # Extraer archivos embebidos
        work_dir = extract_embedded_files()
        
        # Cambiar al directorio de trabajo
        os.chdir(work_dir)
        
        # Verificar que los archivos están disponibles
        if not Path("app.py").exists():
            messagebox.showerror("Error", 
                               "Error extrayendo archivos del instalador.\n"
                               "Contacte al soporte técnico.")
            return
        
        # Crear y ejecutar instalador
        installer = OptiMonInstaller()
        installer.run()
        
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error iniciando instalador:\n{e}")

if __name__ == "__main__":
    main()