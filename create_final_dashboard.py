#!/usr/bin/env python3
"""
Crear dashboard final funcional para Windows Local
"""

import requests
import json

def create_final_dashboard():
    """Crear dashboard final y funcional"""
    print("[INFO] Creando dashboard final de Windows Local...")
    
    # Obtener UID del datasource
    response = requests.get("http://localhost:3000/api/datasources", auth=('admin', 'admin'))
    datasource_uid = None
    if response.status_code == 200:
        for ds in response.json():
            if ds['type'] == 'prometheus':
                datasource_uid = ds['uid']
                break
    
    if not datasource_uid:
        print("[ERROR] No se pudo obtener UID del datasource")
        return False, None
    
    final_dashboard = {
        "dashboard": {
            "id": None,
            "title": "Windows Local Dashboard - OptiMon (Working)",
            "uid": "windows-local-working",
            "tags": ["windows", "local", "optimon", "working"],
            "timezone": "",
            "panels": [
                # Row header
                {
                    "collapsed": False,
                    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0},
                    "id": 100,
                    "panels": [],
                    "title": "System Overview - Windows Local Computer",
                    "type": "row"
                },
                # System Status
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 1,
                    "title": "System Status",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 0, "y": 1},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "up{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "mappings": [
                                {"options": {"0": {"text": "DOWN"}}, "type": "value"},
                                {"options": {"1": {"text": "UP"}}, "type": "value"}
                            ],
                            "thresholds": {
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "green", "value": 1}
                                ]
                            }
                        }
                    },
                    "options": {
                        "colorMode": "background",
                        "graphMode": "none",
                        "justifyMode": "center",
                        "orientation": "auto",
                        "reduceOptions": {
                            "calcs": ["lastNotNull"],
                            "fields": "",
                            "values": False
                        },
                        "textMode": "auto"
                    }
                },
                # Load Average
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 2,
                    "title": "Load Average (1m)",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 6, "y": 1},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_load1{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "decimals": 2,
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 1},
                                    {"color": "red", "value": 2}
                                ]
                            }
                        }
                    },
                    "options": {
                        "colorMode": "value",
                        "graphMode": "area",
                        "justifyMode": "center",
                        "orientation": "auto",
                        "reduceOptions": {
                            "calcs": ["lastNotNull"],
                            "fields": "",
                            "values": False
                        },
                        "textMode": "auto"
                    }
                },
                # Uptime
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 3,
                    "title": "Uptime",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 12, "y": 1},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "time() - node_boot_time_seconds{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "unit": "s",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            }
                        }
                    },
                    "options": {
                        "colorMode": "value",
                        "graphMode": "area",
                        "justifyMode": "center",
                        "orientation": "auto",
                        "reduceOptions": {
                            "calcs": ["lastNotNull"],
                            "fields": "",
                            "values": False
                        },
                        "textMode": "auto"
                    }
                },
                # Total Memory
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 4,
                    "title": "Total Memory",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 6, "x": 18, "y": 1},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_memory_MemTotal_bytes{instance=\"local-computer\"}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "thresholds"},
                            "unit": "bytes",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            }
                        }
                    },
                    "options": {
                        "colorMode": "value",
                        "graphMode": "area",
                        "justifyMode": "center",
                        "orientation": "auto",
                        "reduceOptions": {
                            "calcs": ["lastNotNull"],
                            "fields": "",
                            "values": False
                        },
                        "textMode": "auto"
                    }
                },
                # Time series row
                {
                    "collapsed": False,
                    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 7},
                    "id": 101,
                    "panels": [],
                    "title": "System Metrics - Time Series",
                    "type": "row"
                },
                # Load Average Time Series
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 5,
                    "title": "Load Average Over Time",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_load1{instance=\"local-computer\"}",
                            "refId": "A",
                            "legendFormat": "Load 1m"
                        },
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_load5{instance=\"local-computer\"}",
                            "refId": "B",
                            "legendFormat": "Load 5m"
                        },
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_load15{instance=\"local-computer\"}",
                            "refId": "C",
                            "legendFormat": "Load 15m"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "palette-classic"},
                            "custom": {
                                "axisPlacement": "auto",
                                "barAlignment": 0,
                                "drawStyle": "line",
                                "fillOpacity": 10,
                                "gradientMode": "none",
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "vis": False
                                },
                                "lineInterpolation": "linear",
                                "lineWidth": 2,
                                "pointSize": 5,
                                "scaleDistribution": {"type": "linear"},
                                "showPoints": "never",
                                "spanNulls": False,
                                "stacking": {"group": "A", "mode": "none"},
                                "thresholdsStyle": {"mode": "off"}
                            },
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            }
                        }
                    },
                    "options": {
                        "legend": {
                            "calcs": [],
                            "displayMode": "list",
                            "placement": "bottom"
                        },
                        "tooltip": {"mode": "single", "sort": "none"}
                    }
                },
                # Memory Usage Time Series
                {
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "id": 6,
                    "title": "Memory Usage",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                    "targets": [
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_memory_MemTotal_bytes{instance=\"local-computer\"}",
                            "refId": "A",
                            "legendFormat": "Total Memory"
                        },
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_memory_MemAvailable_bytes{instance=\"local-computer\"}",
                            "refId": "B",
                            "legendFormat": "Available Memory"
                        },
                        {
                            "datasource": {"type": "prometheus", "uid": datasource_uid},
                            "expr": "node_memory_MemTotal_bytes{instance=\"local-computer\"} - node_memory_MemAvailable_bytes{instance=\"local-computer\"}",
                            "refId": "C",
                            "legendFormat": "Used Memory"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "color": {"mode": "palette-classic"},
                            "custom": {
                                "axisPlacement": "auto",
                                "barAlignment": 0,
                                "drawStyle": "line",
                                "fillOpacity": 10,
                                "gradientMode": "none",
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "vis": False
                                },
                                "lineInterpolation": "linear",
                                "lineWidth": 2,
                                "pointSize": 5,
                                "scaleDistribution": {"type": "linear"},
                                "showPoints": "never",
                                "spanNulls": False,
                                "stacking": {"group": "A", "mode": "none"},
                                "thresholdsStyle": {"mode": "off"}
                            },
                            "unit": "bytes",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            }
                        }
                    },
                    "options": {
                        "legend": {
                            "calcs": [],
                            "displayMode": "list",
                            "placement": "bottom"
                        },
                        "tooltip": {"mode": "single", "sort": "none"}
                    }
                }
            ],
            "time": {"from": "now-30m", "to": "now"},
            "timepicker": {},
            "timezone": "",
            "refresh": "10s",
            "schemaVersion": 30,
            "style": "dark",
            "fiscalYearStartMonth": 0,
            "graphTooltip": 0,
            "liveNow": False,
            "links": [],
            "templating": {"list": []},
            "annotations": {
                "list": [
                    {
                        "builtIn": 1,
                        "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                        "enable": True,
                        "hide": True,
                        "iconColor": "rgba(0, 211, 255, 1)",
                        "name": "Annotations & Alerts",
                        "type": "dashboard"
                    }
                ]
            },
            "editable": True
        },
        "overwrite": True,
        "message": "Final working Windows Local Dashboard"
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/dashboards/db",
            json=final_dashboard,
            headers={'Content-Type': 'application/json'},
            auth=('admin', 'admin')
        )
        
        if response.status_code == 200:
            result = response.json()
            dashboard_url = f"http://localhost:3000/d/{result.get('uid', 'windows-local-working')}"
            print(f"[OK] Dashboard final creado: {dashboard_url}")
            return True, dashboard_url
        else:
            print(f"[ERROR] Error creando dashboard: {response.status_code}")
            print(f"[RESPONSE] {response.text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False, None

if __name__ == "__main__":
    print("CREANDO DASHBOARD FINAL DE WINDOWS LOCAL")
    print("=" * 50)
    
    success, url = create_final_dashboard()
    
    if success:
        print(f"\n[SUCCESS] Dashboard final creado exitosamente!")
        print(f"[ACCESS] Abre: {url}")
        print("\n[FEATURES] Dashboard incluye:")
        print("  - System Status (UP/DOWN con colores)")
        print("  - Load Average con umbrales")
        print("  - Uptime del sistema")
        print("  - Total Memory")
        print("  - Load Average Time Series (1m, 5m, 15m)")
        print("  - Memory Usage Time Series")
        print("\n[CONFIG]")
        print("  - Refresh: 10 segundos")
        print("  - Time range: Ultimos 30 minutos")
        print("  - Datasource: Configurado correctamente")
        print("  - Tema: Oscuro")
    else:
        print("\n[ERROR] Error creando dashboard final")