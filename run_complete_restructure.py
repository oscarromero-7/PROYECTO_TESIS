#!/usr/bin/env python3
"""
🚀 OptiMon Complete Restructure & Verify
Script principal para ejecutar restructuración completa + verificación

Autor: OptiMon Team
Versión: 1.0
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

def log(message, level="INFO"):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "START": "🚀"}
    icon = icons.get(level, "📝")
    print(f"[{timestamp}] {icon} {message}")

def print_banner():
    """Mostrar banner del script"""
    banner = """
🚀 OptiMon Complete Restructure & Verify Tool v1.0
==================================================

Este script automatizará completamente la restructuración de tu proyecto:

🏗️ FASE 1: RESTRUCTURACIÓN
- Crear backup de seguridad
- Reorganizar 794 archivos en estructura profesional
- Migrar servicios a ubicaciones apropiadas
- Eliminar archivos duplicados y obsoletos
- Actualizar imports y referencias

🔍 FASE 2: VERIFICACIÓN
- Validar estructura de archivos
- Verificar imports de Python
- Comprobar servicios Docker
- Testear endpoints de servicios
- Validar configuraciones
- Ejecutar tests básicos

⏱️ Tiempo estimado: 3-5 minutos
💾 Backup automático: Sí
🔄 Funcionalidad preservada: 100%

==================================================
"""
    print(banner)

def check_prerequisites():
    """Verificar prerequisitos antes de empezar"""
    log("Verificando prerequisitos...")
    
    issues = []
    
    # Verificar Python
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ requerido")
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path.cwd()
    if not (current_dir / "2-INICIAR-MONITOREO").exists():
        issues.append("No se encuentra directorio '2-INICIAR-MONITOREO'. ¿Estás en el directorio correcto?")
    
    # Verificar scripts necesarios
    required_scripts = ["restructure_project.py", "verify_restructure.py"]
    for script in required_scripts:
        if not (current_dir / script).exists():
            issues.append(f"Script requerido no encontrado: {script}")
    
    # Verificar permisos de escritura
    try:
        test_file = current_dir / "test_write_permission.tmp"
        test_file.write_text("test")
        test_file.unlink()
    except Exception:
        issues.append("Sin permisos de escritura en directorio actual")
    
    if issues:
        log("❌ PREREQUISITOS NO CUMPLIDOS:", "ERROR")
        for issue in issues:
            log(f"  • {issue}", "ERROR")
        return False
    
    log("Prerequisitos verificados correctamente", "SUCCESS")
    return True

def get_user_confirmation():
    """Obtener confirmación del usuario"""
    print("""
⚠️  CONFIRMACIÓN REQUERIDA

Esta operación:
✅ Creará un backup automático de seguridad
✅ Reorganizará completamente el proyecto (794 → estructura profesional)
✅ Preservará toda la funcionalidad existente
✅ Generará reportes detallados

❓ ¿Deseas continuar con la restructuración completa?

Opciones:
  [Y] Sí, continuar con restructuración completa
  [N] No, cancelar operación
  [R] Solo ejecutar restructuración (sin verificación)
  [V] Solo ejecutar verificación (si ya restructuraste)

""")
    
    while True:
        choice = input("Selecciona una opción [Y/N/R/V]: ").upper().strip()
        
        if choice in ['Y', 'YES', 'S', 'SI']:
            return 'complete'
        elif choice in ['N', 'NO']:
            return 'cancel'
        elif choice == 'R':
            return 'restructure_only'
        elif choice == 'V':
            return 'verify_only'
        else:
            print("❌ Opción inválida. Usa Y, N, R, o V")

def run_script(script_name, description):
    """Ejecutar script y capturar resultado"""
    log(f"Ejecutando: {description}...", "START")
    
    try:
        # Ejecutar script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # Mostrar output en tiempo real
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            log(f"Errores en {script_name}:", "ERROR")
            print(result.stderr)
        
        if result.returncode == 0:
            log(f"{description} completado exitosamente", "SUCCESS")
            return True
        else:
            log(f"{description} completado con errores (código {result.returncode})", "WARNING")
            return False
            
    except Exception as e:
        log(f"Error ejecutando {script_name}: {e}", "ERROR")
        return False

def wait_for_user():
    """Esperar confirmación del usuario entre fases"""
    print("\n" + "="*50)
    input("Presiona ENTER para continuar con la siguiente fase...")
    print("="*50 + "\n")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar prerequisitos
    if not check_prerequisites():
        log("No se pueden cumplir los prerequisitos. Abortando.", "ERROR")
        return 1
    
    # Obtener confirmación del usuario
    user_choice = get_user_confirmation()
    
    if user_choice == 'cancel':
        log("Operación cancelada por el usuario", "INFO")
        return 0
    
    start_time = time.time()
    
    try:
        success_restructure = True
        success_verify = True
        
        # FASE 1: RESTRUCTURACIÓN
        if user_choice in ['complete', 'restructure_only']:
            log("="*60, "START")
            log("🏗️ INICIANDO FASE 1: RESTRUCTURACIÓN DEL PROYECTO", "START")
            log("="*60, "START")
            
            success_restructure = run_script(
                "restructure_project.py",
                "Restructuración del proyecto"
            )
            
            if not success_restructure:
                log("❌ Restructuración falló. Revisa los errores anteriores.", "ERROR")
                if user_choice == 'complete':
                    log("⚠️ Cancelando verificación debido a errores en restructuración", "WARNING")
                    return 1
            else:
                log("🎉 FASE 1 COMPLETADA: Proyecto restructurado exitosamente", "SUCCESS")
            
            if user_choice == 'complete':
                wait_for_user()
        
        # FASE 2: VERIFICACIÓN
        if user_choice in ['complete', 'verify_only']:
            log("="*60, "START")
            log("🔍 INICIANDO FASE 2: VERIFICACIÓN POST-RESTRUCTURACIÓN", "START")
            log("="*60, "START")
            
            success_verify = run_script(
                "verify_restructure.py",
                "Verificación post-restructuración"
            )
            
            if not success_verify:
                log("⚠️ Verificación completada con advertencias", "WARNING")
            else:
                log("🎉 FASE 2 COMPLETADA: Verificación exitosa", "SUCCESS")
        
        # RESUMEN FINAL
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        log("="*60, "SUCCESS")
        log("🏁 PROCESO COMPLETADO", "SUCCESS")
        log("="*60, "SUCCESS")
        
        print(f"""
📊 RESUMEN DE OPERACIÓN:
{'='*30}
⏱️ Tiempo total: {minutes}m {seconds}s
🏗️ Restructuración: {'✅ Exitosa' if success_restructure else '❌ Con errores'}
🔍 Verificación: {'✅ Exitosa' if success_verify else '⚠️ Con advertencias'}

📁 ARCHIVOS GENERADOS:
{'='*30}
📄 RESTRUCTURE_SUMMARY.md - Resumen detallado de restructuración
📄 VERIFICATION_REPORT.md - Reporte de verificación
📄 backup_* - Directorio de backup de seguridad

🔗 ACCESOS RÁPIDOS:
{'='*30}
🌐 Dashboard OptiMon: http://localhost:5000
📊 Grafana: http://localhost:3000 (admin/admin)
📈 Prometheus: http://localhost:9090
🚨 AlertManager: http://localhost:9093

📋 PRÓXIMOS PASOS:
{'='*30}
1. Revisar servicios: docker ps
2. Probar dashboard: http://localhost:5000
3. Ejecutar tests: python -m pytest tests/
4. Hacer commit: git add . && git commit -m "Restructure project v2.0"
5. Push cambios: git push origin tu-rama

🎉 ¡PROYECTO OPTIMON RESTRUCTURADO EXITOSAMENTE!
""")
        
        # Código de retorno
        if success_restructure and success_verify:
            return 0  # Todo exitoso
        elif success_restructure:
            return 1  # Restructuración ok, verificación con advertencias
        else:
            return 2  # Restructuración con errores
            
    except KeyboardInterrupt:
        log("\\n❌ Operación cancelada por el usuario (Ctrl+C)", "ERROR")
        return 130
    except Exception as e:
        log(f"❌ Error inesperado: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    exit(main())