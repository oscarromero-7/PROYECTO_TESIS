#!/usr/bin/env python3
"""
OptiMon - Generador de Alertas de Prueba
Sistema para probar el funcionamiento de las alertas diferenciadas
"""

import requests
import json
import time
import subprocess
import sys
import os
from datetime import datetime

class AlertTester:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.prometheus_url = "http://localhost:9090"
        self.alertmanager_url = "http://localhost:9093"
        self.webhook_url = "http://localhost:8080"
        
    def log(self, message):
        """Escribir mensaje con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def check_services_status(self):
        """Verificar que todos los servicios estén funcionando"""
        self.log("Verificando estado de servicios...")
        
        services = {
            "Prometheus": self.prometheus_url,
            "AlertManager": self.alertmanager_url
        }
        
        all_ok = True
        
        for service_name, url in services.items():
            try:
                if service_name == "Prometheus":
                    response = requests.get(f"{url}/-/healthy", timeout=5)
                else:
                    response = requests.get(f"{url}/-/healthy", timeout=5)
                
                if response.status_code == 200:
                    self.log(f"[OK] {service_name}: OK")
                else:
                    self.log(f"[ERROR] {service_name}: Error {response.status_code}")
                    all_ok = False
            except Exception as e:
                self.log(f"[ERROR] {service_name}: No disponible - {e}")
                all_ok = False
        
        # Verificar webhook server
        try:
            response = requests.get(f"{self.webhook_url}/webhook/status", timeout=5)
            if response.status_code == 200:
                self.log("[OK] Webhook Server: OK")
            else:
                self.log("[WARNING] Webhook Server: No disponible (opcional)")
        except:
            self.log("[WARNING] Webhook Server: No disponible (opcional)")
        
        return all_ok
    
    def get_current_alerts(self):
        """Obtener alertas actuales"""
        try:
            response = requests.get(f"{self.alertmanager_url}/api/v1/alerts", timeout=10)
            if response.status_code == 200:
                alerts = response.json()["data"]
                
                self.log(f"Alertas actuales en AlertManager: {len(alerts)}")
                
                for alert in alerts:
                    labels = alert.get("labels", {})
                    status = alert.get("status", {}).get("state", "unknown")
                    self.log(f"  - {labels.get('alertname', 'Unknown')} ({labels.get('server_type', 'unknown')}) = {status}")
                
                return alerts
            else:
                self.log(f"Error obteniendo alertas: {response.status_code}")
                return []
        except Exception as e:
            self.log(f"Error conectando a AlertManager: {e}")
            return []
    
    def simulate_cpu_load_windows(self, duration=120):
        """Simular carga de CPU en Windows para disparar alerta"""
        self.log(f"Simulando carga de CPU por {duration} segundos...")
        self.log("Esto debería disparar una alerta de CPU local...")
        
        try:
            # Script PowerShell para generar carga de CPU
            powershell_script = f"""
            $duration = {duration}
            $endTime = (Get-Date).AddSeconds($duration)
            
            Write-Host "Generando carga de CPU por $duration segundos..."
            
            # Crear trabajos en paralelo para usar múltiples cores
            $jobs = @()
            for ($i = 1; $i -le 4; $i++) {{
                $job = Start-Job -ScriptBlock {{
                    $endTime = $args[0]
                    while ((Get-Date) -lt $endTime) {{
                        # Operaciones matemáticas intensivas
                        $result = 0
                        for ($j = 0; $j -lt 100000; $j++) {{
                            $result += [Math]::Sqrt($j) * [Math]::Sin($j)
                        }}
                    }}
                }} -ArgumentList $endTime
                $jobs += $job
            }}
            
            # Esperar a que terminen todos los trabajos
            $jobs | Wait-Job | Remove-Job
            
            Write-Host "Carga de CPU completada"
            """
            
            # Ejecutar en background
            process = subprocess.Popen([
                "powershell", "-Command", powershell_script
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.log("Carga de CPU iniciada en background")
            self.log("Monitorea las alertas durante los próximos minutos...")
            
            return process
            
        except Exception as e:
            self.log(f"Error simulando carga de CPU: {e}")
            return None
    
    def simulate_memory_usage(self, duration=120):
        """Simular uso alto de memoria"""
        self.log(f"Simulando uso alto de memoria por {duration} segundos...")
        
        try:
            powershell_script = f"""
            $duration = {duration}
            $endTime = (Get-Date).AddSeconds($duration)
            
            Write-Host "Generando uso de memoria por $duration segundos..."
            
            # Crear arrays grandes para consumir memoria
            $arrays = @()
            $arraySize = 50MB
            
            while ((Get-Date) -lt $endTime) {{
                try {{
                    $array = New-Object byte[] $arraySize
                    $arrays += $array
                    Start-Sleep -Milliseconds 500
                }} catch {{
                    Write-Host "Límite de memoria alcanzado"
                    break
                }}
            }}
            
            # Limpiar memoria
            $arrays = $null
            [System.GC]::Collect()
            
            Write-Host "Simulación de memoria completada"
            """
            
            process = subprocess.Popen([
                "powershell", "-Command", powershell_script
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.log("Simulación de memoria iniciada")
            return process
            
        except Exception as e:
            self.log(f"Error simulando uso de memoria: {e}")
            return None
    
    def test_webhook_alert(self):
        """Probar webhook con alerta simulada"""
        self.log("Probando webhook con alerta simulada...")
        
        try:
            response = requests.post(f"{self.webhook_url}/webhook/test", timeout=10)
            if response.status_code == 200:
                self.log("[OK] Webhook de prueba enviado exitosamente")
                return True
            else:
                self.log(f"[ERROR] Error en webhook de prueba: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"[ERROR] Error enviando webhook de prueba: {e}")
            return False
    
    def test_local_notifications(self):
        """Probar notificaciones locales"""
        self.log("Probando sistema de notificaciones locales...")
        
        try:
            result = subprocess.run([
                sys.executable, "local_alert_manager.py", "--test"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("[OK] Prueba de notificaciones locales exitosa")
                return True
            else:
                self.log(f"[ERROR] Error en prueba de notificaciones: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"[ERROR] Error ejecutando prueba de notificaciones: {e}")
            return False
    
    def monitor_alerts_during_test(self, duration=180):
        """Monitorear alertas durante el periodo de prueba"""
        self.log(f"Monitoreando alertas por {duration} segundos...")
        
        start_time = time.time()
        initial_alerts = len(self.get_current_alerts())
        
        while time.time() - start_time < duration:
            current_alerts = self.get_current_alerts()
            
            if len(current_alerts) > initial_alerts:
                self.log("[ALERT] Nueva alerta detectada!")
                
                # Mostrar detalles de alertas nuevas
                for alert in current_alerts:
                    labels = alert.get("labels", {})
                    if labels.get("server_type") == "windows":
                        self.log(f"  [LOCAL] Alerta Local: {labels.get('alertname')} - {alert.get('status', {}).get('state')}")
            
            time.sleep(30)  # Verificar cada 30 segundos
    
    def run_comprehensive_test(self):
        """Ejecutar prueba completa del sistema de alertas"""
        self.log("INICIANDO PRUEBA COMPLETA DEL SISTEMA DE ALERTAS")
        self.log("=" * 60)
        
        # 1. Verificar servicios
        if not self.check_services_status():
            self.log("[ERROR] Algunos servicios no están disponibles. Verifica Docker Compose.")
            return False
        
        # 2. Obtener estado inicial
        self.log("\nEstado inicial:")
        initial_alerts = self.get_current_alerts()
        
        # 3. Probar notificaciones locales
        self.log("\n" + "="*40)
        self.test_local_notifications()
        
        # 4. Probar webhook
        self.log("\n" + "="*40)
        self.test_webhook_alert()
        
        # 5. Generar carga para disparar alertas reales
        self.log("\n" + "="*40)
        self.log("Generando condiciones para disparar alertas reales...")
        
        # Simular carga de CPU
        cpu_process = self.simulate_cpu_load_windows(120)
        
        # Esperar un poco y simular memoria
        time.sleep(10)
        memory_process = self.simulate_memory_usage(90)
        
        # 6. Monitorear alertas
        self.log("\n" + "="*40)
        self.monitor_alerts_during_test(180)
        
        # 7. Verificar estado final
        self.log("\n" + "="*40)
        self.log("Estado final:")
        final_alerts = self.get_current_alerts()
        
        if len(final_alerts) > len(initial_alerts):
            self.log(f"[SUCCESS] Prueba exitosa: Se generaron {len(final_alerts) - len(initial_alerts)} nuevas alertas")
        else:
            self.log("[WARNING] No se generaron nuevas alertas. Verifica umbrales o métricas.")
        
        self.log("\n" + "="*60)
        self.log("PRUEBA COMPLETA FINALIZADA")
        
        return True

def main():
    """Función principal"""
    tester = AlertTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            tester.check_services_status()
            tester.get_current_alerts()
        elif sys.argv[1] == "--cpu":
            tester.simulate_cpu_load_windows(180)
        elif sys.argv[1] == "--memory":
            tester.simulate_memory_usage(120)
        elif sys.argv[1] == "--webhook":
            tester.test_webhook_alert()
        elif sys.argv[1] == "--notifications":
            tester.test_local_notifications()
        elif sys.argv[1] == "--full":
            tester.run_comprehensive_test()
        else:
            print("Uso: python alert_tester.py [--status|--cpu|--memory|--webhook|--notifications|--full]")
    else:
        print("OptiMon Alert Tester")
        print("Opciones disponibles:")
        print("  --status        : Verificar estado de servicios y alertas")
        print("  --cpu          : Simular carga de CPU")
        print("  --memory       : Simular uso alto de memoria")
        print("  --webhook      : Probar webhook de alertas")
        print("  --notifications: Probar notificaciones locales")
        print("  --full         : Ejecutar prueba completa")

if __name__ == "__main__":
    main()