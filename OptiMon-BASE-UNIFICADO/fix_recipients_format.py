#!/usr/bin/env python3
"""
Script para corregir el formato de email_recipients.json
"""

import json
import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
EMAILS_CONFIG = CONFIG_DIR / "email_recipients.json"

def fix_recipients_format():
    """Corregir formato de destinatarios"""
    try:
        if EMAILS_CONFIG.exists():
            with open(EMAILS_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Si ya está en el formato correcto (lista de diccionarios)
            if isinstance(config, dict) and 'recipients' in config:
                recipients = config['recipients']
                if recipients and isinstance(recipients[0], dict):
                    print("✅ El formato ya es correcto")
                    return True
                else:
                    # Convertir lista simple a lista de diccionarios
                    new_config = {
                        "recipients": [
                            {"email": email, "active": True} 
                            for email in recipients if email
                        ]
                    }
            else:
                print("⚠️ Formato detectado: lista simple")
                new_config = {
                    "recipients": [
                        {"email": email, "active": True} 
                        for email in config if email
                    ]
                }
            
            # Guardar formato corregido
            with open(EMAILS_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Formato corregido. Destinatarios: {len(new_config['recipients'])}")
            
            # Mostrar contenido
            for recipient in new_config['recipients']:
                status = "Activo" if recipient.get('active', True) else "Inactivo"
                print(f"   📧 {recipient['email']} - {status}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error corrigiendo formato: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Corrigiendo formato de destinatarios...")
    success = fix_recipients_format()
    
    if success:
        print("\n✅ Formato corregido exitosamente")
        print("Ahora las alertas deberían llegar a los destinatarios configurados")
    else:
        print("\n❌ Error en la corrección")