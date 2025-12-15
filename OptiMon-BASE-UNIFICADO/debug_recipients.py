#!/usr/bin/env python3
"""
Debug específico para load_email_recipients()
"""

import json
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append('.')

# Importar funciones desde app.py
from app import load_email_recipients, EMAILS_CONFIG

def debug_recipients():
    """Debug detallado de la carga de destinatarios"""
    print("🔍 DEBUG: load_email_recipients()")
    print("=" * 50)
    
    # 1. Verificar archivo
    print(f"\n📁 Archivo: {EMAILS_CONFIG}")
    print(f"   Existe: {EMAILS_CONFIG.exists()}")
    
    if EMAILS_CONFIG.exists():
        # 2. Leer contenido raw
        with open(EMAILS_CONFIG, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        print(f"   Contenido raw: {raw_content}")
        
        # 3. Parse JSON
        try:
            config = json.loads(raw_content)
            print(f"   JSON parseado: {config}")
            print(f"   Tipo: {type(config)}")
            
            if isinstance(config, dict) and 'recipients' in config:
                recipients_data = config['recipients']
                print(f"   recipients: {recipients_data}")
                print(f"   Tipo recipients: {type(recipients_data)}")
                
                if recipients_data:
                    print(f"   Primer elemento: {recipients_data[0]}")
                    print(f"   Tipo primer elemento: {type(recipients_data[0])}")
                
        except Exception as e:
            print(f"   ❌ Error parsing JSON: {e}")
    
    # 4. Ejecutar función load_email_recipients
    print(f"\n🔧 Ejecutando load_email_recipients():")
    try:
        recipients = load_email_recipients()
        print(f"   Resultado: {recipients}")
        print(f"   Tipo: {type(recipients)}")
        print(f"   Cantidad: {len(recipients) if recipients else 0}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_recipients()