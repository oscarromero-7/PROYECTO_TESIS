#!/usr/bin/env python3
"""
Programador automatico para verificacion de dashboards
Ejecuta verificacion cada N minutos
"""

import time
import sys
import os

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_auto_verifier_simple import DashboardAutoFixerSimple

def run_scheduled_verification():
    """Ejecutar verificacion programada"""
    auto_fixer = DashboardAutoFixerSimple()
    
    print("INICIANDO MONITOREO AUTOMATICO DE DASHBOARDS")
    print("Verificacion cada 5 minutos")
    print("Presiona Ctrl+C para detener")
    
    try:
        while True:
            print(f"\n{'='*50}")
            print(f"VERIFICACION AUTOMATICA - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            
            auto_fixer.run_automated_verification()
            
            print("\nEsperando 5 minutos hasta la siguiente verificacion...")
            time.sleep(300)  # 5 minutos
            
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")
    except Exception as e:
        print(f"\nError en monitoreo: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        run_scheduled_verification()
    else:
        auto_fixer = DashboardAutoFixerSimple()
        auto_fixer.run_automated_verification()
