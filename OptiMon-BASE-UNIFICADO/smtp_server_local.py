#!/usr/bin/env python3
"""
Servidor SMTP local simple para pruebas de OptiMon
"""

import socket
import threading
import time
from datetime import datetime

class SimpleEmailLogger:
    """Logger simple para emails de OptiMon"""
    
    def __init__(self):
        self.email_count = 0
        
    def log_email(self, data):
        """Registrar email recibido"""
        self.email_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n📧 EMAIL #{self.email_count} - {timestamp}")
        print("=" * 60)
        
        # Extraer información básica
        lines = data.split('\n')
        for line in lines[:15]:  # Mostrar primeras líneas
            if line.strip():
                if line.startswith('From:'):
                    print(f"� {line}")
                elif line.startswith('To:'):
                    print(f"� {line}")
                elif line.startswith('Subject:'):
                    print(f"📋 {line}")
        
        print("✅ Email de OptiMon recibido correctamente")
        print("=" * 60)

def handle_smtp_connection(conn, addr, logger):
    """Manejar conexión SMTP"""
    try:
        # Respuesta inicial SMTP
        conn.send(b"220 OptiMon SMTP Server Ready\r\n")
        
        while True:
            data = conn.recv(1024).decode('utf-8', errors='ignore')
            if not data:
                break
                
            command = data.strip().upper()
            
            if command.startswith('HELO') or command.startswith('EHLO'):
                conn.send(b"250 Hello\r\n")
            elif command.startswith('MAIL FROM'):
                conn.send(b"250 OK\r\n")
            elif command.startswith('RCPT TO'):
                conn.send(b"250 OK\r\n")
            elif command == 'DATA':
                conn.send(b"354 Start mail input\r\n")
                # Recibir el contenido del email
                email_data = ""
                while True:
                    chunk = conn.recv(1024).decode('utf-8', errors='ignore')
                    email_data += chunk
                    if '\r\n.\r\n' in email_data or '\n.\n' in email_data:
                        break
                
                logger.log_email(email_data)
                conn.send(b"250 Message accepted\r\n")
            elif command == 'QUIT':
                conn.send(b"221 Bye\r\n")
                break
            else:
                conn.send(b"250 OK\r\n")
                
    except Exception as e:
        print(f"❌ Error en conexión SMTP: {e}")
    finally:
        conn.close()

def start_smtp_server():
    """Iniciar servidor SMTP en puerto 1025"""
    logger = SimpleEmailLogger()
    
    print("🚀 Iniciando servidor SMTP local para OptiMon...")
    print("📧 Puerto: 1025")
    print("🔄 Estado: Escuchando emails de OptiMon...")
    print("⏹️  Para detener: Ctrl+C")
    print("=" * 60)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('localhost', 1025))
        server_socket.listen(5)
        
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_smtp_connection, 
                args=(conn, addr, logger)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor SMTP detenido")
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_smtp_server()