#!/usr/bin/env python3
"""
Generador Automático de Dashboards de Grafana para OptiMon
Crea dashboards individuales para cada servidor escaneado
"""

import json
import os
from datetime import datetime
import requests

class GrafanaDashboardGenerator:
    def __init__(self):
        self.output_dir = "2-INICIAR-MONITOREO/config/grafana/dashboards"
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Asegura que el directorio de dashboards existe"""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_dashboard_for_server(self, server_id, server_data, scan_results=None):
        """Genera un dashboard específico para un servidor"""
        
        dashboard_template = self._get_base_dashboard_template()
        
        # Personalizar dashboard según el tipo de servidor
        if server_data['type'] == 'windows':
            dashboard = self._customize_windows_dashboard(dashboard_template, server_id, server_data)
        elif server_data['type'] == 'linux':
            dashboard = self._customize_linux_dashboard(dashboard_template, server_id, server_data)
        elif server_data['type'] == 'docker':
            dashboard = self._customize_docker_dashboard(dashboard_template, server_id, server_data)
        else:
            dashboard = self._customize_generic_dashboard(dashboard_template, server_id, server_data)
        
        # Guardar dashboard
        filename = f"{server_id.replace('-', '_')}_dashboard.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print(f"[OK] Dashboard generado para {server_id}: {filename}")
        return filepath
    
    def _get_base_dashboard_template(self):
        """Template base común para todos los dashboards"""
        return {
            "annotations": {
                "list": [
                    {
                        "builtIn": 1,
                        "datasource": "-- Grafana --",
                        "enable": True,
                        "hide": True,
                        "iconColor": "rgba(0, 211, 255, 1)",
                        "name": "Annotations & Alerts",
                        "type": "dashboard"
                    }
                ]
            },
            "editable": True,
            "gnetId": None,
            "graphTooltip": 0,
            "id": None,
            "links": [],
            "panels": [],
            "schemaVersion": 27,
            "style": "dark",
            "tags": ["optimon", "auto-generated"],
            "templating": {
                "list": []
            },
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "timepicker": {},
            "timezone": "",
            "title": "",
            "uid": "",
            "version": 1
        }
    
    def _customize_windows_dashboard(self, template, server_id, server_data):
        """Personaliza dashboard para servidores Windows"""
        
        template["title"] = f"OptiMon - {server_id.upper()} (Windows Server)"
        template["uid"] = f"optimon-{server_id.replace('-', '_')}-windows"
        
        # Panel de CPU Usage
        cpu_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"}
                    },
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 90}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "id": 1,
            "options": {
                "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "single"}
            },
            "targets": [
                {
                    "expr": f'100 - (avg(rate(node_cpu_seconds_total{{instance="{server_data["ip"]}:{server_data["port"]}", mode="idle"}}[2m])) * 100)',
                    "interval": "",
                    "legendFormat": "CPU Usage %",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - CPU Usage",
            "type": "timeseries"
        }
        
        # Panel de Memory Usage (Linux)
        memory_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"}
                    },
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 85}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "id": 2,
            "options": {
                "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "single"}
            },
            "targets": [
                {
                    "expr": f'((node_memory_MemTotal_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}} - node_memory_MemAvailable_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) / node_memory_MemTotal_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) * 100',
                    "interval": "",
                    "legendFormat": "Memory Usage %",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Memory Usage",
            "type": "timeseries"
        }
        
        # Panel de información del servidor Linux
        info_panel = {
            "datasource": None,
            "fieldConfig": {
                "defaults": {},
                "overrides": []
            },
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 8},
            "id": 3,
            "options": {
                "content": f"""
### Información del Servidor Linux

**ID:** {server_id}
**Tipo:** Linux Server (Node Exporter)
**IP:** {server_data['ip']}:{server_data['port']}
**Descripción:** {server_data.get('description', 'N/A')}
**Agregado:** {server_data.get('added_date', 'N/A')[:10]}

Dashboard generado automáticamente por OptiMon
                """,
                "mode": "markdown"
            },
            "pluginVersion": "8.0.0",
            "title": "Server Information",
            "type": "text"
        }
        
        template["panels"] = [cpu_panel, memory_panel, info_panel]
        return template
    
    def _customize_docker_dashboard(self, template, server_id, server_data):
        """Personaliza dashboard para hosts Docker"""
        
        template["title"] = f"OptiMon - {server_id.upper()} (Docker Host)"
        template["uid"] = f"optimon-{server_id.replace('-', '_')}-docker"
        
        # Dashboard específico para Docker con contenedores
        containers_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "displayMode": "list",
                        "orientation": "horizontal"
                    },
                    "mappings": [
                        {"options": {"0": {"text": "Stopped"}}, "type": "value"},
                        {"options": {"1": {"text": "Running"}}, "type": "value"}
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": None},
                            {"color": "green", "value": 1}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
            "id": 1,
            "options": {
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "orientation": "horizontal",
                "textMode": "auto",
                "colorMode": "background"
            },
            "targets": [
                {
                    "expr": f'container_last_seen{{instance="{server_data["ip"]}:{server_data["port"]}"}}',
                    "interval": "",
                    "legendFormat": "{{name}}",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Container Status",
            "type": "stat"
        }
        
        template["panels"] = [containers_panel]
        return template
    
    def _customize_generic_dashboard(self, template, server_id, server_data):
        """Dashboard genérico para servidores desconocidos"""
        
        template["title"] = f"OptiMon - {server_id.upper()} (Generic)"
        template["uid"] = f"optimon-{server_id.replace('-', '_')}-generic"
        
        # Panel básico de conectividad
        status_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [
                        {"options": {"0": {"color": "red", "index": 0, "text": "DOWN"}}, "type": "value"},
                        {"options": {"1": {"color": "green", "index": 1, "text": "UP"}}, "type": "value"}
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": None},
                            {"color": "green", "value": 1}
                        ]
                    }
                }
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
            "id": 1,
            "options": {
                "colorMode": "background",
                "graphMode": "none",
                "justifyMode": "center",
                "orientation": "horizontal"
            },
            "targets": [
                {
                    "expr": f'up{{instance="{server_data["ip"]}:{server_data["port"]}"}}',
                    "interval": "",
                    "legendFormat": "Status",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Server Status",
            "type": "stat"
        }
        
        template["panels"] = [status_panel]
        return template

    def generate_all_dashboards(self, servers_data):
        """Genera dashboards para todos los servidores"""
        generated_count = 0
        
        for server_id, server_data in servers_data.items():
            try:
                self.generate_dashboard_for_server(server_id, server_data)
                generated_count += 1
            except Exception as e:
                print(f"[ERROR] Error generando dashboard para {server_id}: {e}")
        
        print(f"[OK] {generated_count} dashboards generados exitosamente")
        return generated_count

    def update_provisioning_config(self):
        """Actualiza la configuración de provisioning de Grafana"""
        
        provisioning_dir = "2-INICIAR-MONITOREO/config/grafana/provisioning/dashboards"
        os.makedirs(provisioning_dir, exist_ok=True)
        
        # Configuración para auto-importar dashboards
        dashboards_config = {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "optimon-dashboards",
                    "orgId": 1,
                    "folder": "OptiMon Auto-Generated",
                    "type": "file",
                    "disableDeletion": False,
                    "editable": True,
                    "updateIntervalSeconds": 10,
                    "allowUiUpdates": True,
                    "options": {
                        "path": "/var/lib/grafana/dashboards"
                    }
                }
            ]
        }
        
        config_path = os.path.join(provisioning_dir, "dashboards.yml")
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(dashboards_config, f, default_flow_style=False)
        
        print(f"[OK] Configuración de provisioning actualizada: {config_path}")

def main():
    """Función principal del generador de dashboards"""
    generator = GrafanaDashboardGenerator()
    
    # Cargar inventario de servidores
    if os.path.exists("server_inventory.json"):
        with open("server_inventory.json", 'r') as f:
            servers = json.load(f)
        
        print(f"Generando dashboards para {len(servers)} servidores...")
        generator.generate_all_dashboards(servers)
        generator.update_provisioning_config()
        
        print("\n=== DASHBOARDS GENERADOS ===")
        print("Los dashboards se han creado automáticamente")
        print("Se importarán automáticamente en Grafana al reiniciar")
        print("Ubicación:", generator.output_dir)
    else:
        print("[ERROR] No se encuentra server_inventory.json")
        print("Ejecuta primero el sistema de inventario de servidores")

if __name__ == "__main__":
    main()
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 90}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "id": 1,
            "options": {
                "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "single"}
            },
            "targets": [
                {
                    "expr": f'100 - (avg(rate(windows_cpu_time_total{{instance="{server_data["ip"]}:{server_data["port"]}", mode="idle"}}[2m])) * 100)',
                    "interval": "",
                    "legendFormat": "CPU Usage %",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - CPU Usage",
            "type": "timeseries"
        }
        
        # Panel de Memory Usage
        memory_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"}
                    },
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 85}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "id": 2,
            "options": {
                "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                "tooltip": {"mode": "single"}
            },
            "targets": [
                {
                    "expr": f'((windows_cs_physical_memory_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}} - windows_os_physical_memory_free_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) / windows_cs_physical_memory_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) * 100',
                    "interval": "",
                    "legendFormat": "Memory Usage %",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Memory Usage",
            "type": "timeseries"
        }
        
        # Panel de Disk Space
        disk_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "displayMode": "list",
                        "orientation": "horizontal"
                    },
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 80},
                            {"color": "red", "value": 95}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
            "id": 3,
            "options": {
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "orientation": "horizontal",
                "textMode": "auto",
                "colorMode": "value",
                "graphMode": "area",
                "justifyMode": "auto"
            },
            "pluginVersion": "8.0.0",
            "targets": [
                {
                    "expr": f'((windows_logical_disk_size_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}} - windows_logical_disk_free_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) / windows_logical_disk_size_bytes{{instance="{server_data["ip"]}:{server_data["port"]}"}}) * 100',
                    "interval": "",
                    "legendFormat": "{{volume}} Used %",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Disk Usage by Volume",
            "type": "stat"
        }
        
        # Panel de estado/conectividad
        status_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [
                        {"options": {"0": {"color": "red", "index": 0, "text": "DOWN"}}, "type": "value"},
                        {"options": {"1": {"color": "green", "index": 1, "text": "UP"}}, "type": "value"}
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": None},
                            {"color": "green", "value": 1}
                        ]
                    },
                    "unit": "none"
                }
            },
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 16},
            "id": 4,
            "options": {
                "colorMode": "background",
                "graphMode": "none",
                "justifyMode": "center",
                "orientation": "horizontal",
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "textMode": "auto"
            },
            "pluginVersion": "8.0.0",
            "targets": [
                {
                    "expr": f'up{{instance="{server_data["ip"]}:{server_data["port"]}"}}',
                    "interval": "",
                    "legendFormat": "Status",
                    "refId": "A"
                }
            ],
            "title": f"{server_id} - Server Status",
            "type": "stat"
        }
        
        # Información del servidor
        info_panel = {
            "datasource": None,
            "fieldConfig": {
                "defaults": {},
                "overrides": []
            },
            "gridPos": {"h": 4, "w": 18, "x": 6, "y": 16},
            "id": 5,
            "options": {
                "content": f"""
### Información del Servidor

**ID:** {server_id}
**Tipo:** Windows Server  
**IP:** {server_data['ip']}:{server_data['port']}
**Descripción:** {server_data.get('description', 'N/A')}
**Agregado:** {server_data.get('added_date', 'N/A')[:10]}

Dashboard generado automáticamente por OptiMon
                """,
                "mode": "markdown"
            },
            "pluginVersion": "8.0.0",
            "title": "Server Information",
            "type": "text"
        }
        
        template["panels"] = [cpu_panel, memory_panel, disk_panel, status_panel, info_panel]
        return template
    
    def _customize_linux_dashboard(self, template, server_id, server_data):
        """Personaliza dashboard para servidores Linux"""
        
        template["title"] = f"OptiMon - {server_id.upper()} (Linux Server)"
        template["uid"] = f"optimon-{server_id.replace('-', '_')}-linux"
        
        # Similar estructura pero con métricas de Linux (node_exporter)
        cpu_panel = {
            "datasource": "Prometheus",
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                        "lineInterpolation": "linear",
                        "lineWidth": 2,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": True,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"}
                    },
                    "mappings": [],
                    "