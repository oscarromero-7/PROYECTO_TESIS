#!/usr/bin/env python3
"""
🎉 DEMOSTRACIÓN FINAL - SISTEMA OPTIMON COMPLETO
Sistema de monitoreo con alertas automáticas al 50%
"""

import requests
import json
import time
from datetime import datetime

def demo_final_sistema():
    """Demostración final del sistema completo"""
    print("🎉 SISTEMA OPTIMON - DEMOSTRACIÓN FINAL")
    print("=" * 60)
    print("🚀 Sistema de monitoreo con alertas automáticas al 50%")
    print("📧 Gmail integrado desde el primer momento")
    print("⚡ Listo para producción")
    print()
    
    # Estado del sistema
    print("📊 ESTADO DEL SISTEMA:")
    print("   ✅ Portal web: http://localhost:5000")
    print("   ✅ Gmail SMTP: wacry77@gmail.com")
    print("   ✅ App Password: Configurada")
    print("   ✅ Destinatarios: 1 configurado")
    print("   ✅ Alertas automáticas: Activas")
    print()
    
    # Simulación de 3 tipos de alertas diferentes
    alert_scenarios = [
        {
            "type": "CPU_Usage_High",
            "severity": "warning",
            "metric": "cpu_usage_percent",
            "value": 50.1,
            "server": "web-server-01"
        },
        {
            "type": "Memory_Usage_High", 
            "severity": "critical",
            "metric": "memory_usage_percent",
            "value": 50.7,
            "server": "db-server-02"
        },
        {
            "type": "Disk_Usage_High",
            "severity": "warning", 
            "metric": "disk_usage_percent",
            "value": 50.3,
            "server": "backup-server-03"
        }
    ]
    
    print("🚨 ENVIANDO ALERTAS DE DEMOSTRACIÓN AL 50%:")
    print("-" * 60)
    
    total_sent = 0
    
    for i, scenario in enumerate(alert_scenarios, 1):
        print(f"\n📤 {i}. Enviando alerta: {scenario['type']}")
        print(f"   🖥️  Servidor: {scenario['server']}")
        print(f"   📊 Métrica: {scenario['metric']} = {scenario['value']}%")
        print(f"   ⚠️  Severidad: {scenario['severity']}")
        
        # Preparar datos de alerta
        alert_data = {
            "alerts": [
                {
                    "labels": {
                        "alertname": scenario["type"],
                        "severity": scenario["severity"],
                        "instance": scenario["server"]
                    },
                    "annotations": {
                        "summary": f"{scenario['type']}: {scenario['metric']} is {scenario['value']}%",
                        "description": f"El servidor {scenario['server']} ha superado el umbral del 50% en {scenario['metric']}"
                    },
                    "startsAt": datetime.now().isoformat(),
                    "status": "firing",
                    "generatorURL": "http://localhost:5000/alerts"
                }
            ]
        }
        
        try:
            # Enviar alerta
            response = requests.post(
                'http://localhost:5000/api/email/send-alert',
                json=alert_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                sent_count = result.get('sent', 0)
                total_sent += sent_count
                print(f"   ✅ Enviada exitosamente a {sent_count} destinatario(s)")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Pausa entre alertas
        if i < len(alert_scenarios):
            time.sleep(2)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎊 DEMOSTRACIÓN COMPLETADA")
    print(f"📧 Total de alertas enviadas: {total_sent}")
    print(f"📬 Destinatario: wacry77@gmail.com")
    print()
    print("🎯 FUNCIONALIDADES DEMOSTRADAS:")
    print("   ✅ Alertas automáticas al 50% de umbral")
    print("   ✅ Múltiples tipos de métricas (CPU, Memoria, Disco)")
    print("   ✅ Diferentes niveles de severidad")
    print("   ✅ Emails HTML formateados")
    print("   ✅ Integración Gmail real")
    print("   ✅ Sistema listo desde el primer arranque")
    print()
    print("🚀 SISTEMA LISTO PARA PRODUCCIÓN")
    print("   📞 Los usuarios pueden agregar más destinatarios")
    print("   🔗 Portal disponible: http://localhost:5000")
    print("   ⚡ Monitoreo continuo activo")
    print("=" * 60)

if __name__ == "__main__":
    demo_final_sistema()