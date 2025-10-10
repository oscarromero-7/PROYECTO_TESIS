#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de Emails OptiMon
Sistema simple para que los usuarios configuren sus emails sin complejidad SMTP
"""

import json
import os
import shutil
from pathlib import Path

CONFIG_DIR = Path("config/optimon")
EMAIL_CONFIG_FILE = CONFIG_DIR / "email_recipients.json"
ALERTMANAGER_CONFIG_DIR = Path("config/alertmanager")

def ensure_config_dir():
    """Asegura que el directorio de configuración existe"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_email_config():
    """Carga la configuración de emails"""
    if EMAIL_CONFIG_FILE.exists():
        with open(EMAIL_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"recipients": [], "default_recipient": ""}

def save_email_config(config):
    """Guarda la configuración de emails"""
    ensure_config_dir()
    with open(EMAIL_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def add_email_recipient(email, name="", is_default=False):
    """
    Agrega un destinatario de email
    Args:
        email: Dirección de email
        name: Nombre del destinatario (opcional)
        is_default: Si es el destinatario por defecto
    """
    config = load_email_config()
    
    # Verificar si el email ya existe
    for recipient in config["recipients"]:
        if recipient["email"] == email:
            print(f"⚠️ El email {email} ya está configurado")
            return False
    
    # Agregar nuevo destinatario
    recipient = {
        "email": email,
        "name": name or email.split('@')[0],
        "active": True,
        "added_date": str(Path().cwd())
    }
    
    config["recipients"].append(recipient)
    
    # Configurar como default si es el primero o se especifica
    if is_default or not config["default_recipient"]:
        config["default_recipient"] = email
    
    save_email_config(config)
    
    print(f"✅ Email agregado exitosamente: {email}")
    if is_default or not config.get("default_recipient"):
        print(f"📧 Configurado como destinatario principal")
    
    return True

def list_email_recipients():
    """Lista todos los destinatarios configurados"""
    config = load_email_config()
    
    if not config["recipients"]:
        print("📭 No hay destinatarios configurados")
        return
    
    print("📧 Destinatarios configurados:")
    print("=" * 50)
    
    for i, recipient in enumerate(config["recipients"], 1):
        status = "✅ Activo" if recipient.get("active", True) else "❌ Inactivo"
        default = " (PRINCIPAL)" if recipient["email"] == config.get("default_recipient") else ""
        
        print(f"{i}. {recipient['email']}{default}")
        print(f"   Nombre: {recipient.get('name', 'Sin nombre')}")
        print(f"   Estado: {status}")
        print()

def set_default_recipient(email):
    """Establece un email como destinatario principal"""
    config = load_email_config()
    
    # Verificar que el email existe
    email_exists = any(r["email"] == email for r in config["recipients"])
    
    if not email_exists:
        print(f"❌ El email {email} no está configurado. Agrégalo primero.")
        return False
    
    config["default_recipient"] = email
    save_email_config(config)
    
    print(f"✅ {email} configurado como destinatario principal")
    return True

def remove_email_recipient(email):
    """Elimina un destinatario"""
    config = load_email_config()
    
    # Buscar y eliminar el email
    original_count = len(config["recipients"])
    config["recipients"] = [r for r in config["recipients"] if r["email"] != email]
    
    if len(config["recipients"]) < original_count:
        # Si era el principal, limpiar
        if config.get("default_recipient") == email:
            config["default_recipient"] = config["recipients"][0]["email"] if config["recipients"] else ""
        
        save_email_config(config)
        print(f"✅ Email {email} eliminado exitosamente")
        
        if config["recipients"] and config["default_recipient"]:
            print(f"📧 Nuevo destinatario principal: {config['default_recipient']}")
        
        return True
    else:
        print(f"❌ El email {email} no fue encontrado")
        return False

def update_alertmanager_webhook_config():
    """
    Actualiza la configuración de AlertManager para usar nuestro servicio webhook
    No requiere configuración SMTP del usuario
    """
    source_config = Path("config/alertmanager/alertmanager_webhook.yml")
    target_config = ALERTMANAGER_CONFIG_DIR / "alertmanager.yml"
    
    if source_config.exists():
        shutil.copy2(source_config, target_config)
        print("✅ Configuración de AlertManager actualizada para usar webhook")
        print("📧 Ahora el sistema manejará los emails automáticamente")
        return True
    else:
        print("❌ Archivo de configuración webhook no encontrado")
        return False

def configure_system_for_simple_email():
    """Configura todo el sistema para email simple"""
    print("🔧 Configurando OptiMon para envío simple de emails...")
    print("=" * 60)
    
    # 1. Actualizar AlertManager
    if update_alertmanager_webhook_config():
        print("✅ AlertManager configurado")
    
    # 2. Mostrar configuración actual
    print("\n📧 Configuración actual de emails:")
    list_email_recipients()
    
    print("\n💡 Instrucciones:")
    print("1. El sistema ahora usa un servicio SMTP interno")
    print("2. Los usuarios solo necesitan agregar su email")
    print("3. No es necesario configurar contraseñas SMTP")
    print("4. Para agregar emails, usa: add_email_recipient('tu@email.com')")

def main():
    """Función principal para configurar emails"""
    import sys
    
    if len(sys.argv) < 2:
        print("🔧 OptiMon Email Configurator")
        print("=" * 40)
        print("Uso:")
        print("  python email_config.py list                    - Listar emails")
        print("  python email_config.py add email@example.com   - Agregar email")
        print("  python email_config.py default email@example.com - Configurar principal")
        print("  python email_config.py remove email@example.com  - Eliminar email")
        print("  python email_config.py setup                   - Configurar sistema")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_email_recipients()
    elif command == "add" and len(sys.argv) > 2:
        email = sys.argv[2]
        is_default = len(sys.argv) > 3 and sys.argv[3].lower() == "default"
        add_email_recipient(email, is_default=is_default)
    elif command == "default" and len(sys.argv) > 2:
        set_default_recipient(sys.argv[2])
    elif command == "remove" and len(sys.argv) > 2:
        remove_email_recipient(sys.argv[2])
    elif command == "setup":
        configure_system_for_simple_email()
    else:
        print("❌ Comando inválido")

if __name__ == "__main__":
    main()