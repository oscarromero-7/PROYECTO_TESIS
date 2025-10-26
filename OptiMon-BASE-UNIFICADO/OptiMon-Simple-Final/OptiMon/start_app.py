
import sys
import os
import time
import socket
import webbrowser
import threading

sys.path.insert(0, r"C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO\OptiMon-Simple-Final\OptiMon")
os.chdir(r"C:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\OptiMon-BASE-UNIFICADO\OptiMon-Simple-Final\OptiMon")

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
    print(f"❌ Error: {e}")
    print("🔄 Intentando abrir portal existente...")
    try:
        webbrowser.open("http://localhost:5000")
    except:
        pass
    input("Presiona Enter para cerrar...")
