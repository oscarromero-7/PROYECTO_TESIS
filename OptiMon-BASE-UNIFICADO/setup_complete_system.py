#!/usr/bin/env python3
"""
Configuración automática de destinatarios y prueba de alertas
"""

import requests
import json

def setup_recipients():
    """Configurar destinatarios automáticamente"""
    print("📧 Configurando destinatarios de prueba...")
    
    # Lista de destinatarios de ejemplo
    recipients = [
        "wacry77@gmail.com",  # Tu email principal
        "admin@ejemplo.com",   # Email de administrador (ejemplo)
    ]
    
    try:
        # Configurar destinatarios vía API
        response = requests.post(
            'http://localhost:5000/api/email/config',
            headers={'Content-Type': 'application/json'},
            json={'recipients': recipients},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {len(recipients)} destinatarios configurados:")
                for email in recipients:
                    print(f"   📥 {email}")
                return True
            else:
                print(f"❌ Error configurando destinatarios: {result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_system_ready():
    """Verificar que el sistema esté listo"""
    print("🔍 Verificando sistema OptiMon...")
    
    try:
        # Verificar configuración email
        response = requests.get('http://localhost:5000/api/email/config', timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            
            print("✅ Sistema OptiMon activo")
            print(f"✅ Gmail configurado: {config.get('configured', False)}")
            print(f"✅ Destinatarios: {len(config.get('recipients', []))}")
            
            if config.get('configured') and config.get('recipients'):
                print("🎉 Sistema completamente listo para alertas!")
                return True
            else:
                print("⚠️  Sistema necesita configuración")
                return False
        else:
            print(f"❌ Sistema no responde: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando al sistema: {e}")
        return False

def main():
    """Configuración y prueba completa"""
    print("🚀 SETUP AUTOMÁTICO OPTIMON - GMAIL INTEGRADO")
    print("=" * 60)
    print()
    
    # Paso 1: Verificar sistema
    if not verify_system_ready():
        print("❌ Sistema no está listo")
        return
    
    print()
    
    # Paso 2: Configurar destinatarios
    if setup_recipients():
        print()
        print("🎯 SISTEMA LISTO PARA ALERTAS:")
        print("   ✅ Gmail preconfigurado")
        print("   ✅ Destinatarios configurados")
        print("   ✅ Portal web activo")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("   1. Ve a: http://localhost:5000/emails")
        print("   2. Agrega más destinatarios si quieres")
        print("   3. Envía email de prueba")
        print("   4. ¡Las alertas automáticas funcionarán!")
        print()
        print("🚨 Para probar alerta al 50%:")
        print("   python test_alert_50_percent.py")
    else:
        print("❌ Error en configuración")

if __name__ == "__main__":
    main()