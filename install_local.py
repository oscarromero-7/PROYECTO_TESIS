#!/usr/bin/env python3
"""
OptiMon - Instalador Automático Local
Instala Node Exporter en la computadora actual con elevación automática
"""

import os
import sys
import subprocess
import time

def install_local_node_exporter():
    """Instala Node Exporter localmente con elevación automática"""
    
    print("🚀 OptiMon - Instalación Local Automática")
    print("=" * 50)
    print()
    print("📍 Instalando Node Exporter en esta computadora")
    print("💻 Sistema: Windows Local")
    print("🔐 Solicitará permisos de administrador automáticamente")
    print()
    
    # Verificar que estamos en Windows
    if os.name != 'nt':
        print("❌ Este script es solo para Windows")
        return False
    
    # Verificar que el script batch existe
    script_path = "install_local_auto.bat"
    if not os.path.exists(script_path):
        print(f"❌ Error: No se encontró {script_path}")
        print("💡 Asegúrate de ejecutar desde el directorio del proyecto OptiMon")
        return False
    
    print("🔄 Iniciando instalación automática...")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Se abrirá una ventana UAC (Control de Cuentas de Usuario)")
    print("   - Click 'SÍ' para permitir la instalación")
    print("   - La instalación continuará automáticamente")
    print()
    
    # Preguntar al usuario si está listo
    response = input("¿Estás listo para continuar? (s/n): ").lower().strip()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Instalación cancelada por el usuario")
        return False
    
    print()
    print("🚀 Ejecutando instalador...")
    
    try:
        # Ejecutar el script batch
        # El script batch se encargará de solicitar permisos de administrador
        result = subprocess.run([script_path], 
                              cwd=os.getcwd(),
                              shell=True)
        
        if result.returncode == 0:
            print()
            print("✅ Instalación completada exitosamente!")
            
            # Verificar que funciona
            print("🔍 Verificando instalación...")
            time.sleep(2)
            
            try:
                import requests
                response = requests.get("http://localhost:9100/metrics", timeout=5)
                if response.status_code == 200:
                    print("✅ Node Exporter funcionando correctamente!")
                    print("📊 Métricas disponibles en: http://localhost:9100/metrics")
                    
                    # Contar métricas
                    metrics_count = len([line for line in response.text.split('\n') 
                                       if line.startswith('# HELP')])
                    print(f"📈 {metrics_count} métricas disponibles")
                    
                else:
                    print("⚠️  Servicio instalado pero aún no responde")
            except Exception as e:
                print("⚠️  Servicio instalado, verificando manualmente...")
                print("💡 Verifica en: http://localhost:9100/metrics")
            
            print()
            print("🎯 Próximos pasos:")
            print("   1. Ve a Grafana: http://localhost:3000")
            print("   2. Busca el dashboard 'Physical Servers'")
            print("   3. Tu computadora aparecerá como 'local-computer'")
            print()
            
            return True
            
        else:
            print("❌ Error durante la instalación")
            print("💡 Verifica que tienes permisos de administrador")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando instalador: {e}")
        return False

def main():
    """Función principal"""
    try:
        # Cambiar al directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        success = install_local_node_exporter()
        
        if success:
            print("🎉 ¡Proceso completado exitosamente!")
            print()
            print("📋 Resumen:")
            print("   ✅ Node Exporter instalado localmente")
            print("   ✅ Servicio de Windows configurado") 
            print("   ✅ Firewall configurado")
            print("   ✅ Prometheus actualizado")
            print("   ✅ Listo para monitoreo en Grafana")
        else:
            print("❌ Instalación no completada")
            print("💡 Intenta ejecutar manualmente: install_local_auto.bat")
        
        input("\nPresiona Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\n❌ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()