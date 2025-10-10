#!/usr/bin/env python3
"""
Script para generar carga de CPU y disparar alertas reales de OptiMon
"""

import time
import threading
import multiprocessing
import math
import os
import sys

def cpu_stress_worker(duration):
    """Worker function para generar carga de CPU"""
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Operaciones matemáticas intensivas
        for i in range(100000):
            result = math.sqrt(i) * math.sin(i) * math.cos(i)

def generate_cpu_load(duration=90, cpu_percent=90):
    """Generar carga de CPU específica"""
    print(f"Generando {cpu_percent}% de carga de CPU por {duration} segundos...")
    print("Esto debería disparar una alerta de CPU en 2-3 minutos...")
    
    # Número de cores disponibles
    num_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(num_cores * cpu_percent / 100))
    
    print(f"Usando {num_workers} de {num_cores} cores disponibles")
    
    # Crear procesos para generar carga
    processes = []
    
    try:
        for i in range(num_workers):
            p = multiprocessing.Process(target=cpu_stress_worker, args=(duration,))
            p.start()
            processes.append(p)
            print(f"Proceso {i+1} iniciado (PID: {p.pid})")
        
        # Esperar a que terminen los procesos
        for p in processes:
            p.join()
        
        print("Carga de CPU completada")
        
    except KeyboardInterrupt:
        print("\nDeteniendo carga de CPU...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        print("Procesos terminados")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    else:
        duration = 90
    
    generate_cpu_load(duration)