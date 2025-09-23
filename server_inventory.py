#!/usr/bin/env python3
"""
Sistema de Inventario y Escaneo Multi-Servidor para OptiMon
Permite configurar y escanear múltiples servidores simultáneamente
"""

import json
import os
import asyncio
import concurrent.futures
import subprocess
import time
from datetime import datetime
import requests
import socket

class ServerInventory:
    def __init__(self):
        self.inventory_file = "server_inventory.json"
        self.servers = {}
        self.load_inventory()
    
    def load_inventory(self):
        """Carga el inventario de servidores desde archivo JSON"""
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r') as f:
                    self.servers = json.load(f)
                print(f"[INFO] Inventario cargado: {len(self.servers)} servidores")
            except Exception as e:
                print(f"[ERROR] Error cargando inventario: {e}")
                self.servers = {}
        else:
            print("[INFO] No existe inventario previo, iniciando configuración")
            self.servers = {}
    
    def save_inventory(self):
        """Guarda el inventario actual en archivo JSON"""
        try:
            with open(self.inventory_file, 'w') as f:
                json.dump(self.servers, f, indent=2)
            print(f"[OK] Inventario guardado: {len(self.servers)} servidores")
        except Exception as e:
            print(f"[ERROR] Error guardando inventario: {e}")
    
    def add_server_interactive(self):
        """Añade un servidor de forma interactiva"""
        print("\n=== Agregar Nuevo Servidor ===")
        
        server_id = input("ID del servidor (ej: web-01, db-prod): ").strip()
        if not server_id or server_id in self.servers:
            print(f"[ERROR] ID '{server_id}' está vacío o ya existe")
            return False
        
        print("\nTipo de servidor:")
        print("[1] Windows (Windows Exporter en puerto 9182)")
        print("[2] Linux (Node Exporter en puerto 9100)")
        print("[3] Docker Host (Múltiples exporters)")
        
        server_type = input("Selecciona tipo (1-3): ").strip()
        
        if server_type == "1":
            type_name = "windows"
            default_port = 9182
            exporter = "windows_exporter"
        elif server_type == "2":
            type_name = "linux"  
            default_port = 9100
            exporter = "node_exporter"
        elif server_type == "3":
            type_name = "docker"
            default_port = 9100
            exporter = "multiple"
        else:
            print("[ERROR] Tipo inválido")
            return False
        
        ip = input(f"IP o hostname: ").strip()
        if not ip:
            print("[ERROR] IP no puede estar vacía")
            return False
        
        port = input(f"Puerto del exporter [{default_port}]: ").strip()
        if not port:
            port = default_port
        else:
            try:
                port = int(port)
            except:
                print("[ERROR] Puerto inválido")
                return False
        
        description = input("Descripción (opcional): ").strip()
        
        # Verificar conectividad
        if self.test_connectivity(ip, port):
            connectivity = "online"
            print(f"[OK] Servidor {ip}:{port} responde correctamente")
        else:
            print(f"[WARNING] No se puede conectar a {ip}:{port}")
            confirm = input("¿Agregar de todas formas? (y/N): ").lower()
            if confirm != 'y':
                return False
            connectivity = "offline"
        
        # Crear entrada del servidor
        self.servers[server_id] = {
            "id": server_id,
            "type": type_name,
            "ip": ip,
            "port": port,
            "exporter": exporter,
            "description": description,
            "connectivity": connectivity,
            "added_date": datetime.now().isoformat(),
            "last_scan": None,
            "dashboard_generated": False
        }
        
        self.save_inventory()
        print(f"[OK] Servidor '{server_id}' agregado exitosamente")
        return True
    
    def test_connectivity(self, ip, port, timeout=5):
        """Prueba la conectividad con un servidor"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            return result == 0
        except:
            return False
    
    def list_servers(self):
        """Lista todos los servidores del inventario"""
        if not self.servers:
            print("No hay servidores configurados")
            return
        
        print(f"\n=== Inventario de Servidores ({len(self.servers)}) ===")
        print(f"{'ID':<15} {'Tipo':<10} {'IP:Puerto':<20} {'Estado':<10} {'Descripción'}")
        print("-" * 75)
        
        for server_id, server in self.servers.items():
            status = "🟢 Online" if server.get('connectivity') == 'online' else "🔴 Offline"
            print(f"{server_id:<15} {server['type']:<10} {server['ip']}:{server['port']:<15} {status:<10} {server.get('description', '')}")
    
    def scan_all_servers(self):
        """Escanea todos los servidores en paralelo"""
        if not self.servers:
            print("No hay servidores para escanear")
            return {}
        
        print(f"\n=== Iniciando Escaneo de {len(self.servers)} Servidores ===")
        
        scan_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Crear tareas de escaneo
            future_to_server = {
                executor.submit(self.scan_single_server, server_id, server_data): server_id 
                for server_id, server_data in self.servers.items()
            }
            
            # Recoger resultados
            for future in concurrent.futures.as_completed(future_to_server):
                server_id = future_to_server[future]
                try:
                    result = future.result()
                    scan_results[server_id] = result
                    
                    # Actualizar estado en inventario
                    self.servers[server_id]['last_scan'] = datetime.now().isoformat()
                    self.servers[server_id]['connectivity'] = result.get('status', 'offline')
                    
                except Exception as e:
                    print(f"[ERROR] Error escaneando {server_id}: {e}")
                    scan_results[server_id] = {'status': 'error', 'error': str(e)}
        
        self.save_inventory()
        return scan_results
    
    def scan_single_server(self, server_id, server_data):
        """Escanea un servidor individual"""
        print(f"[INFO] Escaneando {server_id} ({server_data['ip']}:{server_data['port']})")
        
        result = {
            'server_id': server_id,
            'server_data': server_data,
            'metrics': {},
            'status': 'offline',
            'scan_time': datetime.now().isoformat()
        }
        
        try:
            # Verificar conectividad
            if not self.test_connectivity(server_data['ip'], server_data['port']):
                result['status'] = 'offline'
                print(f"[WARNING] {server_id} no responde")
                return result
            
            # Intentar obtener métricas
            metrics_url = f"http://{server_data['ip']}:{server_data['port']}/metrics"
            response = requests.get(metrics_url, timeout=10)
            
            if response.status_code == 200:
                # Parsear métricas básicas
                metrics_text = response.text
                result['metrics'] = self.parse_basic_metrics(metrics_text, server_data['type'])
                result['status'] = 'online'
                print(f"[OK] {server_id} escaneado exitosamente")
            else:
                result['status'] = 'error'
                result['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"[ERROR] Error escaneando {server_id}: {e}")
        
        return result
    
    def parse_basic_metrics(self, metrics_text, server_type):
        """Parsea métricas básicas del texto de Prometheus"""
        basic_metrics = {}
        
        try:
            lines = metrics_text.split('\n')
            
            if server_type == 'windows':
                # Métricas Windows
                for line in lines:
                    if line.startswith('windows_cpu_time_total{mode="idle"}'):
                        # Extraer valor de CPU idle (simplificado)
                        value = line.split(' ')[-1]
                        basic_metrics['cpu_idle'] = float(value)
                    elif line.startswith('windows_os_physical_memory_free_bytes'):
                        value = line.split(' ')[-1]
                        basic_metrics['memory_free_bytes'] = float(value)
                    elif line.startswith('windows_cs_physical_memory_bytes'):
                        value = line.split(' ')[-1] 
                        basic_metrics['memory_total_bytes'] = float(value)
            
            elif server_type == 'linux':
                # Métricas Linux
                for line in lines:
                    if line.startswith('node_cpu_seconds_total{mode="idle"'):
                        value = line.split(' ')[-1]
                        basic_metrics['cpu_idle'] = float(value)
                    elif line.startswith('node_memory_MemAvailable_bytes'):
                        value = line.split(' ')[-1]
                        basic_metrics['memory_available_bytes'] = float(value)
                    elif line.startswith('node_memory_MemTotal_bytes'):
                        value = line.split(' ')[-1]
                        basic_metrics['memory_total_bytes'] = float(value)
            
            # Calcular porcentajes si tenemos datos
            if 'memory_free_bytes' in basic_metrics and 'memory_total_bytes' in basic_metrics:
                memory_used_pct = ((basic_metrics['memory_total_bytes'] - basic_metrics['memory_free_bytes']) / basic_metrics['memory_total_bytes']) * 100
                basic_metrics['memory_used_percent'] = round(memory_used_pct, 2)
            
            elif 'memory_available_bytes' in basic_metrics and 'memory_total_bytes' in basic_metrics:
                memory_used_pct = ((basic_metrics['memory_total_bytes'] - basic_metrics['memory_available_bytes']) / basic_metrics['memory_total_bytes']) * 100
                basic_metrics['memory_used_percent'] = round(memory_used_pct, 2)
                
        except Exception as e:
            print(f"[WARNING] Error parseando métricas: {e}")
        
        return basic_metrics

def main():
    """Función principal del sistema de inventario"""
    inventory = ServerInventory()
    
    while True:
        print("\n" + "="*50)
        print("OptiMon - Sistema de Inventario Multi-Servidor")
        print("="*50)
        print("[1] Ver servidores configurados")
        print("[2] Agregar nuevo servidor")
        print("[3] Escanear todos los servidores")
        print("[4] Probar conectividad de todos")
        print("[5] Generar configuración Prometheus")
        print("[0] Salir")
        
        opcion = input("\nSelecciona opción: ").strip()
        
        if opcion == "1":
            inventory.list_servers()
            
        elif opcion == "2":
            inventory.add_server_interactive()
            
        elif opcion == "3":
            results = inventory.scan_all_servers()
            print(f"\n=== Resumen de Escaneo ===")
            online = sum(1 for r in results.values() if r.get('status') == 'online')
            offline = sum(1 for r in results.values() if r.get('status') == 'offline') 
            error = sum(1 for r in results.values() if r.get('status') == 'error')
            print(f"Online: {online}, Offline: {offline}, Error: {error}")
            
        elif opcion == "4":
            print("\n=== Probando Conectividad ===")
            for server_id, server_data in inventory.servers.items():
                status = "🟢 OK" if inventory.test_connectivity(server_data['ip'], server_data['port']) else "🔴 FAIL"
                print(f"{server_id:<15} {server_data['ip']}:{server_data['port']:<15} {status}")
                
        elif opcion == "5":
            # Generar configuración de Prometheus
            print("\n=== Generando Configuración Prometheus ===")
            prometheus_config = generate_prometheus_config(inventory.servers)
            with open("prometheus_multi_server.yml", "w") as f:
                f.write(prometheus_config)
            print("Archivo 'prometheus_multi_server.yml' generado")
            
        elif opcion == "0":
            break
            
        else:
            print("[ERROR] Opción inválida")

def generate_prometheus_config(servers):
    """Genera configuración de Prometheus para múltiples servidores"""
    config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

"""
    
    # Agrupar servidores por tipo
    windows_servers = []
    linux_servers = []
    docker_servers = []
    
    for server_id, server in servers.items():
        target = f"{server['ip']}:{server['port']}"
        if server['type'] == 'windows':
            windows_servers.append(target)
        elif server['type'] == 'linux':
            linux_servers.append(target)
        elif server['type'] == 'docker':
            docker_servers.append(target)
    
    # Generar jobs por tipo
    if windows_servers:
        config += f"""  - job_name: "windows_servers"
    static_configs:
      - targets: {json.dumps(windows_servers)}
    scrape_interval: 30s
    scrape_timeout: 10s

"""
    
    if linux_servers:
        config += f"""  - job_name: "linux_servers"
    static_configs:
      - targets: {json.dumps(linux_servers)}
    scrape_interval: 30s
    scrape_timeout: 10s

"""
    
    if docker_servers:
        config += f"""  - job_name: "docker_hosts"
    static_configs:
      - targets: {json.dumps(docker_servers)}
    scrape_interval: 30s
    scrape_timeout: 10s

"""
    
    return config

if __name__ == "__main__":
    main()