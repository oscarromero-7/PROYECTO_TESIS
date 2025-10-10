#!/usr/bin/env python3
"""
Gestor de Configuración de OptiMon
"""

import json
import os

def load_config():
    """Cargar configuración actual"""
    config_file = "optimon_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    """Guardar configuración"""
    with open("optimon_config.json", 'w') as f:
        json.dump(config, f, indent=2)

def configure_service():
    """Configurar el servicio interactivamente"""
    print("CONFIGURACION DEL SERVICIO OPTIMON")
    print("=" * 40)
    
    config = load_config() or {
        "verification_interval_minutes": 5,
        "auto_restart_services": True,
        "max_retry_attempts": 3,
        "enabled_checks": {
            "prometheus_health": True,
            "grafana_health": True,
            "dashboard_validation": True,
            "datasource_correction": True,
            "auto_import": True
        }
    }
    
    print(f"Intervalo actual: {config['verification_interval_minutes']} minutos")
    new_interval = input("Nuevo intervalo (minutos, Enter para mantener): ")
    if new_interval.strip():
        config['verification_interval_minutes'] = int(new_interval)
    
    print(f"Auto-reinicio: {config['auto_restart_services']}")
    restart = input("Auto-reiniciar servicios? (s/n, Enter para mantener): ")
    if restart.lower() == 's':
        config['auto_restart_services'] = True
    elif restart.lower() == 'n':
        config['auto_restart_services'] = False
    
    save_config(config)
    print("\nConfiguracion guardada exitosamente!")
    print("Reinicia el servicio para aplicar cambios.")

if __name__ == "__main__":
    configure_service()
