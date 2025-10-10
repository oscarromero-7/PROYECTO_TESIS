#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador SMTP OptiMon
Herramienta interactiva para configurar el envío de emails
"""

import os
import getpass
from pathlib import Path

def get_user_input(prompt, default="", password=False):
    """Obtiene entrada del usuario con valor por defecto"""
    if password:
        value = getpass.getpass(f"{prompt}: ")
    else:
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"{prompt}: ").strip()
    return value

def detect_provider(email):
    """Detecta el proveedor de email y sugiere configuración"""
    email_lower = email.lower()
    
    if '@gmail.com' in email_lower:
        return {
            'provider': 'Gmail',
            'host': 'smtp.gmail.com',
            'port': '587',
            'instructions': [
                "Para Gmail necesitas:",
                "1. Activar verificación en 2 pasos en tu cuenta",
                "2. Ir a 'Contraseñas de aplicaciones' en tu cuenta Google",
                "3. Generar una contraseña de aplicación para 'Correo'",
                "4. Usar esa contraseña (no tu contraseña normal)"
            ]
        }
    elif '@hotmail.com' in email_lower or '@outlook.com' in email_lower:
        return {
            'provider': 'Outlook/Hotmail',
            'host': 'smtp-mail.outlook.com',
            'port': '587',
            'instructions': [
                "Para Outlook/Hotmail:",
                "1. Asegúrate de tener verificación en 2 pasos activada",
                "2. Puedes usar tu contraseña normal",
                "3. O generar una contraseña de aplicación si tienes problemas"
            ]
        }
    elif '@yahoo.com' in email_lower:
        return {
            'provider': 'Yahoo',
            'host': 'smtp.mail.yahoo.com',
            'port': '587',
            'instructions': [
                "Para Yahoo necesitas:",
                "1. Activar verificación en 2 pasos",
                "2. Generar una contraseña de aplicación",
                "3. Usar esa contraseña de aplicación"
            ]
        }
    else:
        return {
            'provider': 'Otro',
            'host': 'smtp.gmail.com',
            'port': '587',
            'instructions': [
                "Proveedor no reconocido.",
                "Por favor configura manualmente:",
                "1. Host SMTP de tu proveedor",
                "2. Puerto (usualmente 587 o 465)",
                "3. Credenciales de autenticación"
            ]
        }

def configure_smtp():
    """Configurador interactivo de SMTP"""
    
    print("🔧 CONFIGURADOR SMTP OPTIMON")
    print("=" * 50)
    print("Este asistente te ayudará a configurar el envío de emails")
    print()
    
    # 1. Obtener email del usuario
    print("1️⃣ CONFIGURACIÓN DEL REMITENTE")
    print("-" * 30)
    email = get_user_input("Tu email (para enviar las alertas)")
    
    if not email:
        print("❌ Email requerido para continuar")
        return False
    
    # 2. Detectar proveedor y mostrar instrucciones
    provider_info = detect_provider(email)
    
    print(f"\n📧 Proveedor detectado: {provider_info['provider']}")
    print("\n💡 INSTRUCCIONES:")
    for instruction in provider_info['instructions']:
        print(f"   {instruction}")
    
    print(f"\n⚙️  Configuración sugerida:")
    print(f"   Host: {provider_info['host']}")
    print(f"   Puerto: {provider_info['port']}")
    
    # 3. Confirmar configuración
    print(f"\n2️⃣ CONFIGURACIÓN DEL SERVIDOR")
    print("-" * 30)
    
    host = get_user_input("Host SMTP", provider_info['host'])
    port = get_user_input("Puerto SMTP", provider_info['port'])
    
    # 4. Obtener credenciales
    print(f"\n3️⃣ CREDENCIALES")
    print("-" * 30)
    
    username = get_user_input("Usuario SMTP (tu email)", email)
    password = get_user_input("Contraseña SMTP", password=True)
    
    if not password:
        print("❌ Contraseña requerida para continuar")
        return False
    
    # 5. Configuración adicional
    print(f"\n4️⃣ CONFIGURACIÓN ADICIONAL")
    print("-" * 30)
    
    from_name = get_user_input("Nombre del remitente", "OptiMon Alerts")
    use_tls = get_user_input("Usar TLS [s/n]", "s").lower().startswith('s')
    
    # 6. Crear archivo .env
    env_content = f"""# Configuración SMTP OptiMon
# Generado automáticamente - {provider_info['provider']}

SMTP_HOST={host}
SMTP_PORT={port}
SMTP_USERNAME={username}
SMTP_PASSWORD={password}
SMTP_USE_TLS={'true' if use_tls else 'false'}
SMTP_TIMEOUT=30

# Configuración del remitente
EMAIL_FROM_NAME={from_name}
EMAIL_FROM_DISPLAY=Sistema de Monitoreo OptiMon
"""
    
    # 7. Guardar configuración
    env_file = Path(".env")
    
    print(f"\n5️⃣ GUARDANDO CONFIGURACIÓN")
    print("-" * 30)
    
    if env_file.exists():
        backup = input("Archivo .env existe. ¿Crear respaldo? [s/n]: ").lower().startswith('s')
        if backup:
            env_file.rename(".env.backup")
            print("✅ Respaldo creado como .env.backup")
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Configuración guardada en .env")
    
    # 8. Ofrecer prueba
    print(f"\n🧪 PRUEBA DE CONFIGURACIÓN")
    print("-" * 30)
    
    test = input("¿Realizar prueba de envío? [s/n]: ").lower().startswith('s')
    
    if test:
        print("\n🚀 Iniciando prueba...")
        return test_smtp_config(username)
    
    print(f"\n✅ CONFIGURACIÓN COMPLETADA")
    print("📋 Próximos pasos:")
    print("1. Iniciar el servicio: python optimon_smtp_service.py")
    print("2. Probar el envío: python test_email_direct.py")
    
    return True

def test_smtp_config(test_email):
    """Prueba la configuración SMTP"""
    try:
        # Cargar variables de entorno
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importar funciones del servicio
        import sys
        sys.path.append('.')
        
        # Test simple de conexión
        import smtplib
        
        host = os.getenv('SMTP_HOST')
        port = int(os.getenv('SMTP_PORT'))
        username = os.getenv('SMTP_USERNAME')
        password = os.getenv('SMTP_PASSWORD')
        use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        
        print(f"📧 Probando conexión a {host}:{port}")
        
        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                server.starttls()
            server.login(username, password)
            print("✅ Conexión SMTP exitosa")
            print("✅ Autenticación correcta")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        print("\n💡 Posibles soluciones:")
        print("• Verifica las credenciales")
        print("• Revisa la configuración de tu proveedor de email")
        print("• Asegúrate de tener permisos para aplicaciones menos seguras")
        return False

def main():
    """Función principal"""
    print("Bienvenido al configurador SMTP de OptiMon")
    print()
    
    # Verificar si ya existe configuración
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  Ya existe un archivo .env")
        reconfigure = input("¿Quieres reconfigurar? [s/n]: ").lower().startswith('s')
        if not reconfigure:
            print("Configuración existente mantenida")
            return
    
    # Ejecutar configuración
    if configure_smtp():
        print("\n🎉 ¡Configuración completada exitosamente!")
    else:
        print("\n❌ Configuración cancelada o incompleta")

if __name__ == "__main__":
    main()