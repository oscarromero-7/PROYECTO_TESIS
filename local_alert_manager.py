#!/usr/bin/env python3
"""
OptiMon - Sistema de Notificaciones Desktop para Windows
Sistema de alertas no críticas para la máquina local
"""

import json
import requests
import time
import subprocess
import os
import sys
from datetime import datetime

# Para notificaciones de Windows
try:
    from plyer import notification
    DESKTOP_NOTIFICATIONS = True
except ImportError:
    DESKTOP_NOTIFICATIONS = False
    print("Para notificaciones desktop, instala: pip install plyer")

class LocalAlertManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.prometheus_url = "http://localhost:9090"
        self.alertmanager_url = "http://localhost:9093"
        self.log_file = os.path.join(self.base_dir, "local_alerts.log")
        
        # Configuración de alertas locales
        self.alert_config = {
            "check_interval": 60,  # segundos
            "notification_cooldown": 300,  # 5 minutos
            "enabled_notifications": {
                "desktop": True,
                "sound": True,
                "email": False,  # Ya manejado por AlertManager
                "log": True
            }
        }
        
        # Historial de alertas para evitar spam
        self.alert_history = {}
    
    def log(self, message):
        """Escribir al log de alertas locales"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        if self.alert_config["enabled_notifications"]["log"]:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_message + "\n")
            except:
                pass
    
    def show_desktop_notification(self, title, message, alert_type="info"):
        """Mostrar notificación desktop en Windows"""
        if not DESKTOP_NOTIFICATIONS:
            self.log("Desktop notifications no disponibles")
            return
        
        # Iconos según tipo de alerta
        icon_map = {
            "critical": "error",
            "warning": "warning", 
            "info": "info"
        }
        
        try:
            notification.notify(
                title=f"OptiMon: {title}",
                message=message,
                timeout=10,
                toast=True
            )
            self.log(f"Notificación desktop enviada: {title}")
        except Exception as e:
            self.log(f"Error enviando notificación desktop: {e}")
    
    def play_alert_sound(self, alert_type="warning"):
        """Reproducir sonido de alerta"""
        if not self.alert_config["enabled_notifications"]["sound"]:
            return
        
        try:
            # Usar sonidos del sistema de Windows
            sound_map = {
                "critical": "SystemHand",  # Error crítico
                "warning": "SystemExclamation",  # Advertencia
                "info": "SystemAsterisk"  # Información
            }
            
            sound = sound_map.get(alert_type, "SystemExclamation")
            subprocess.run([
                "powershell", "-c", 
                f"[System.Media.SystemSounds]::{sound}.Play()"
            ], capture_output=True)
            
            self.log(f"Sonido de alerta reproducido: {alert_type}")
        except Exception as e:
            self.log(f"Error reproduciendo sonido: {e}")
    
    def check_local_windows_metrics(self):
        """Verificar métricas específicas de Windows"""
        alerts = []
        
        try:
            # Consultas específicas para Windows
            queries = {
                "cpu_usage": {
                    "query": '100 - (avg(rate(windows_cpu_time_total{instance="host.docker.internal:9182",mode="idle"}[2m])) * 100)',
                    "threshold": 85,
                    "severity": "warning",
                    "message": "Alto uso de CPU en PC local"
                },
                "memory_usage": {
                    "query": '((windows_cs_physical_memory_bytes{instance="host.docker.internal:9182"} - windows_os_physical_memory_free_bytes{instance="host.docker.internal:9182"}) / windows_cs_physical_memory_bytes{instance="host.docker.internal:9182"}) * 100',
                    "threshold": 90,
                    "severity": "critical",
                    "message": "Alto uso de memoria en PC local"
                },
                "disk_usage": {
                    "query": '((windows_logical_disk_size_bytes{instance="host.docker.internal:9182"} - windows_logical_disk_free_bytes{instance="host.docker.internal:9182"}) / windows_logical_disk_size_bytes{instance="host.docker.internal:9182"}) * 100',
                    "threshold": 85,
                    "severity": "warning",
                    "message": "Poco espacio en disco en PC local"
                }
            }
            
            for metric_name, config in queries.items():
                response = requests.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": config["query"]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success" and data["data"]["result"]:
                        for result in data["data"]["result"]:
                            value = float(result["value"][1])
                            if value > config["threshold"]:
                                alerts.append({
                                    "metric": metric_name,
                                    "value": value,
                                    "threshold": config["threshold"],
                                    "severity": config["severity"],
                                    "message": config["message"],
                                    "instance": result["metric"].get("instance", "local")
                                })
        
        except Exception as e:
            self.log(f"Error verificando métricas locales: {e}")
        
        return alerts
    
    def check_alertmanager_alerts(self):
        """Verificar alertas activas en AlertManager para Windows"""
        local_alerts = []
        
        try:
            response = requests.get(f"{self.alertmanager_url}/api/v1/alerts", timeout=10)
            
            if response.status_code == 200:
                alerts = response.json()["data"]
                
                # Filtrar solo alertas de Windows (locales)
                for alert in alerts:
                    labels = alert.get("labels", {})
                    if labels.get("server_type") == "windows":
                        local_alerts.append({
                            "name": labels.get("alertname", "Unknown"),
                            "severity": labels.get("severity", "info"),
                            "instance": labels.get("instance", "local"),
                            "summary": alert.get("annotations", {}).get("summary", ""),
                            "description": alert.get("annotations", {}).get("description", ""),
                            "status": alert.get("status", {}).get("state", "unknown"),
                            "starts_at": alert.get("startsAt", "")
                        })
        
        except Exception as e:
            self.log(f"Error verificando AlertManager: {e}")
        
        return local_alerts
    
    def should_notify(self, alert_key):
        """Verificar si debemos notificar (evitar spam)"""
        now = time.time()
        last_notification = self.alert_history.get(alert_key, 0)
        
        if now - last_notification > self.alert_config["notification_cooldown"]:
            self.alert_history[alert_key] = now
            return True
        
        return False
    
    def process_local_alerts(self):
        """Procesar alertas locales y enviar notificaciones"""
        self.log("Verificando alertas locales...")
        
        # Verificar métricas directamente
        metric_alerts = self.check_local_windows_metrics()
        
        # Verificar AlertManager
        am_alerts = self.check_alertmanager_alerts()
        
        # Procesar alertas de métricas
        for alert in metric_alerts:
            alert_key = f"{alert['metric']}_{alert['instance']}"
            
            if self.should_notify(alert_key):
                title = f"Alerta Local: {alert['metric'].upper()}"
                message = f"{alert['message']}\nValor: {alert['value']:.1f}% (límite: {alert['threshold']}%)"
                
                # Notificación desktop
                if self.alert_config["enabled_notifications"]["desktop"]:
                    self.show_desktop_notification(title, message, alert['severity'])
                
                # Sonido de alerta
                if self.alert_config["enabled_notifications"]["sound"]:
                    self.play_alert_sound(alert['severity'])
                
                self.log(f"Alerta procesada: {alert['metric']} = {alert['value']:.1f}%")
        
        # Procesar alertas de AlertManager
        for alert in am_alerts:
            alert_key = f"{alert['name']}_{alert['instance']}"
            
            if alert['status'] == 'firing' and self.should_notify(alert_key):
                title = f"Alerta: {alert['name']}"
                message = f"{alert['summary']}\n{alert['description']}"
                
                # Notificación desktop
                if self.alert_config["enabled_notifications"]["desktop"]:
                    self.show_desktop_notification(title, message, alert['severity'])
                
                # Sonido según severidad
                if self.alert_config["enabled_notifications"]["sound"]:
                    self.play_alert_sound(alert['severity'])
                
                self.log(f"Alerta AlertManager procesada: {alert['name']} ({alert['severity']})")
        
        if not metric_alerts and not am_alerts:
            self.log("No hay alertas activas en el sistema local")
        
        return len(metric_alerts) + len(am_alerts)
    
    def test_notifications(self):
        """Probar sistema de notificaciones"""
        self.log("Probando sistema de notificaciones...")
        
        # Prueba de notificación desktop
        if self.alert_config["enabled_notifications"]["desktop"]:
            self.show_desktop_notification(
                "Prueba de Sistema",
                "OptiMon Local Alert Manager funcionando correctamente",
                "info"
            )
        
        # Prueba de sonido
        if self.alert_config["enabled_notifications"]["sound"]:
            self.play_alert_sound("info")
        
        self.log("Prueba de notificaciones completada")
    
    def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        self.log("Iniciando monitoreo local de alertas...")
        self.log(f"Intervalo de verificación: {self.alert_config['check_interval']} segundos")
        
        try:
            while True:
                alerts_count = self.process_local_alerts()
                time.sleep(self.alert_config["check_interval"])
                
        except KeyboardInterrupt:
            self.log("Monitoreo detenido por el usuario")
        except Exception as e:
            self.log(f"Error en monitoreo: {e}")

def main():
    """Función principal"""
    manager = LocalAlertManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            manager.test_notifications()
        elif sys.argv[1] == "--check":
            alerts = manager.process_local_alerts()
            print(f"Alertas procesadas: {alerts}")
        elif sys.argv[1] == "--monitor":
            manager.start_monitoring()
        else:
            print("Uso: python local_alert_manager.py [--test|--check|--monitor]")
    else:
        # Verificación única por defecto
        manager.process_local_alerts()

if __name__ == "__main__":
    main()