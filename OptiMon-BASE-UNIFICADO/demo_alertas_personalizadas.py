#!/usr/bin/env python3
"""
🎯 DEMO - ALERTAS PERSONALIZADAS
Demostración de la nueva funcionalidad de alertas personalizadas
"""

import requests
import json
from datetime import datetime

def demo_alertas_personalizadas():
    """Demostración completa de alertas personalizadas"""
    print("🎯 DEMO: ALERTAS PERSONALIZADAS - OPTIMON")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 1. Verificar que el servidor esté funcionando
    try:
        response = requests.get(f"{base_url}")
        if response.status_code == 200:
            print("✅ Servidor OptiMon activo")
        else:
            print("❌ Servidor no responde")
            return
    except:
        print("❌ No se puede conectar al servidor")
        return
    
    print("\n🌐 PÁGINAS DISPONIBLES:")
    print("   📊 Dashboard: http://localhost:5000")
    print("   🚨 Alertas Personalizadas: http://localhost:5000/custom-alerts")
    print("   📧 Configuración Email: http://localhost:5000/emails")
    
    # 2. Crear algunas alertas de ejemplo
    alertas_ejemplo = [
        {
            "name": "CPU_Alto_Personalizado",
            "description": "Alerta cuando CPU supera 80% en servidores críticos",
            "metric": "cpu_usage_percent",
            "threshold": 80.0,
            "operator": ">",
            "severity": "critical",
            "enabled": True,
            "tags": ["servidor", "critico", "cpu"]
        },
        {
            "name": "Memoria_Advertencia",
            "description": "Advertencia cuando memoria supera 70%",
            "metric": "memory_usage_percent", 
            "threshold": 70.0,
            "operator": ">=",
            "severity": "warning",
            "enabled": True,
            "tags": ["memoria", "advertencia"]
        },
        {
            "name": "Tiempo_Respuesta_Lento",
            "description": "Alerta cuando tiempo de respuesta es mayor a 500ms",
            "metric": "response_time_ms",
            "threshold": 500.0,
            "operator": ">",
            "severity": "warning",
            "enabled": True,
            "tags": ["performance", "web"]
        }
    ]
    
    print(f"\n🚨 CREANDO ALERTAS DE EJEMPLO:")
    print("-" * 40)
    
    created_alerts = []
    for i, alerta in enumerate(alertas_ejemplo, 1):
        try:
            response = requests.post(
                f"{base_url}/api/custom-alerts",
                json=alerta,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    created_alerts.append(result['alert'])
                    print(f"   {i}. ✅ {alerta['name']}")
                    print(f"      📊 {alerta['metric']} {alerta['operator']} {alerta['threshold']}")
                    print(f"      ⚠️  Severidad: {alerta['severity']}")
                else:
                    print(f"   {i}. ❌ Error: {result.get('error', 'Error desconocido')}")
            else:
                print(f"   {i}. ❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   {i}. ❌ Error: {e}")
    
    # 3. Listar alertas creadas
    print(f"\n📋 ALERTAS CONFIGURADAS:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/custom-alerts")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            
            if alerts:
                for alert in alerts:
                    status = "🟢 ACTIVA" if alert.get('enabled') else "🔴 INACTIVA"
                    severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️" if alert['severity'] == 'warning' else "ℹ️"
                    
                    print(f"   {severity_icon} {alert['name']} - {status}")
                    print(f"      📊 {alert['metric']} {alert['operator']} {alert['threshold']}")
                    print(f"      📝 {alert.get('description', 'Sin descripción')}")
                    print()
            else:
                print("   📝 No hay alertas configuradas")
        else:
            print("   ❌ Error obteniendo alertas")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Probar una alerta
    if created_alerts:
        print(f"🧪 PROBANDO ALERTA:")
        print("-" * 40)
        
        test_alert = created_alerts[0]
        try:
            response = requests.post(
                f"{base_url}/api/custom-alerts/{test_alert['id']}/test"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Alerta '{test_alert['name']}' enviada exitosamente")
                    print(f"   📧 Destinatarios: {result.get('sent', 0)}")
                else:
                    print(f"   ❌ Error: {result.get('message', 'Error desconocido')}")
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 5. Resumen final
    print(f"\n" + "=" * 60)
    print("🎉 FUNCIONALIDAD DE ALERTAS PERSONALIZADAS LISTA")
    print(f"✅ Página web: http://localhost:5000/custom-alerts")
    print(f"✅ API REST: /api/custom-alerts")
    print(f"✅ Funciones disponibles:")
    print(f"   • Crear alertas personalizadas")
    print(f"   • Editar alertas existentes")
    print(f"   • Probar alertas (enviar email)")
    print(f"   • Activar/desactivar alertas")
    print(f"   • Múltiples métricas y operadores")
    print(f"   • Diferentes niveles de severidad")
    print("=" * 60)

if __name__ == "__main__":
    demo_alertas_personalizadas()