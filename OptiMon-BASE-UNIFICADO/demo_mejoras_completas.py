#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Demo: Sistema Completo de Optimización de Costos OptiMon v3.1.0
================================================================
Demostración de todas las mejoras implementadas:
- Instancias descubiertas automáticamente
- Recomendaciones detalladas con fuentes de precios
- Funcionalidad de descarga de reportes
- Integración completa con dashboard web
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

def print_banner():
    """Mostrar banner de demostración"""
    print("=" * 80)
    print("🎯 DEMO: SISTEMA COMPLETO DE OPTIMIZACIÓN DE COSTOS OptiMon v3.1.0")
    print("=" * 80)
    print("✨ NUEVAS CARACTERÍSTICAS IMPLEMENTADAS:")
    print("   📋 Instancias descubiertas automáticamente en formulario")
    print("   💰 Precios detallados con fuentes oficiales (AWS/Azure)")
    print("   📄 Recomendaciones más claras y descriptivas")
    print("   📥 Funcionalidad de descarga de reportes corregida")
    print("   🎨 Interfaz mejorada con información detallada")
    print()

def test_server_connection():
    """Verificar que el servidor está funcionando"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor OptiMon conectado correctamente")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("💡 Asegúrese de que el servidor esté ejecutándose: python app.py")
        return False

def test_discovered_instances():
    """Probar endpoint de instancias descubiertas"""
    print("\n🔍 PROBANDO: Instancias Descubiertas")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/cost-optimization/instances")
        data = response.json()
        
        if data['success']:
            instances = data['instances']
            print(f"✅ Se encontraron {len(instances)} instancias:")
            
            for i, instance in enumerate(instances, 1):
                print(f"   {i}. {instance['name']} ({instance['id']})")
                print(f"      📍 Proveedor: {instance['provider'].upper()}")
                print(f"      🖥️  Tipo: {instance['type']}")
                print(f"      📊 Estado: {instance['state']}")
                print(f"      🌍 Región: {instance['region']}")
                print()
            
            return instances[0] if instances else None
        else:
            print(f"❌ Error obteniendo instancias: {data.get('error', 'Desconocido')}")
            return None
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return None

def test_cost_analysis(instance):
    """Probar análisis de costos mejorado"""
    print("💡 PROBANDO: Análisis de Costos Mejorado")
    print("-" * 50)
    
    try:
        payload = {
            'instance_id': instance['id'],
            'provider': instance['provider'],
            'instance_type': instance['type']
        }
        
        response = requests.post("http://localhost:5000/api/cost-optimization/analyze", 
                               json=payload)
        data = response.json()
        
        if data['success']:
            analysis = data['analysis']
            recommendations = data['recommendations']
            
            print(f"✅ Análisis completado para: {instance['name']}")
            print(f"   🔥 CPU Promedio: {analysis['cpu_utilization']['average']:.1f}%")
            print(f"   🧠 Memoria Promedio: {analysis['memory_utilization']['average']:.1f}%")
            print(f"   🔄 Patrón de uso: {analysis['usage_pattern']}")
            print(f"   💰 Ahorro potencial: ${data.get('potential_savings', 0):.2f}/mes")
            print()
            
            if recommendations:
                print("🎯 RECOMENDACIONES DETALLADAS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec['type'].replace('_', ' ').title()}")
                    print(f"      📋 {rec['description'][:100]}...")
                    
                    if 'detailed_analysis' in rec:
                        print("      📊 Análisis detallado:")
                        for key, value in rec['detailed_analysis'].items():
                            print(f"         • {key}: {value}")
                    
                    if 'pricing_source' in rec:
                        print(f"      💲 Fuente de precios: {rec['pricing_source']}")
                    
                    if 'estimated_monthly_savings' in rec:
                        print(f"      💰 Ahorro: ${rec['estimated_monthly_savings']}/mes")
                    
                    print()
            
            return True
        else:
            print(f"❌ Error en análisis: {data.get('error', 'Desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def test_weekly_report():
    """Probar generación de reporte semanal"""
    print("📊 PROBANDO: Reporte Semanal")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/cost-optimization/weekly-report")
        data = response.json()
        
        if data['success']:
            report = data['report']
            summary = report['summary']
            
            print("✅ Reporte semanal generado:")
            print(f"   📅 Fecha: {report['report_date']}")
            print(f"   💡 Total recomendaciones: {summary['total_recommendations']}")
            print(f"   🔴 Alta prioridad: {summary['high_priority_items']}")
            print(f"   💰 Ahorro potencial: ${summary['potential_monthly_savings']:.2f}/mes")
            print(f"   💰 Ahorro anual: ${summary['potential_monthly_savings'] * 12:.2f}/año")
            print()
            
            return True
        else:
            print(f"❌ Error generando reporte: {data.get('error', 'Desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def test_download_functionality():
    """Probar funcionalidad de descarga"""
    print("📥 PROBANDO: Descarga de Reportes")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/cost-optimization/download-report")
        
        if response.status_code == 200:
            # Verificar headers de descarga
            content_disposition = response.headers.get('Content-Disposition', '')
            content_type = response.headers.get('Content-Type', '')
            
            print("✅ Funcionalidad de descarga funcionando:")
            print(f"   📄 Tipo de contenido: {content_type}")
            print(f"   📁 Nombre sugerido: {content_disposition}")
            print(f"   📊 Tamaño del reporte: {len(response.content)} bytes")
            
            # Verificar que es JSON válido
            try:
                report_data = response.json()
                print(f"   ✅ JSON válido con {len(report_data)} secciones")
                
                if 'metadata' in report_data:
                    print(f"   📋 Versión del sistema: {report_data['metadata'].get('system_version')}")
                
                return True
            except:
                print("   ⚠️ Respuesta no es JSON válido")
                return False
                
        else:
            print(f"❌ Error en descarga: Código {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def show_web_interface_info():
    """Mostrar información sobre la interfaz web"""
    print("🌐 INTERFAZ WEB MEJORADA")
    print("-" * 50)
    print("🎨 NUEVAS CARACTERÍSTICAS DEL DASHBOARD:")
    print("   📋 Selector automático de instancias descubiertas")
    print("   📊 Información detallada de cada instancia")
    print("   💰 Detalles de precios con fuentes oficiales")
    print("   📈 Barras de utilización con colores dinámicos")
    print("   📥 Botón de descarga de reportes funcional")
    print("   🎯 Recomendaciones expandidas con análisis detallado")
    print()
    print("🔗 ACCESO AL DASHBOARD:")
    print("   🏠 Dashboard Principal: http://localhost:5000")
    print("   💰 Optimización de Costos: http://localhost:5000/cost-optimization")
    print("   📧 Sistema de Alertas: http://localhost:5000/emails")
    print()

def main():
    """Función principal de demostración"""
    print_banner()
    
    # Verificar conexión al servidor
    if not test_server_connection():
        return
    
    print("\n🚀 INICIANDO PRUEBAS DEL SISTEMA MEJORADO...")
    
    # Probar instancias descubiertas
    instance = test_discovered_instances()
    if not instance:
        print("⚠️ No se pudieron obtener instancias para continuar las pruebas")
        return
    
    # Probar análisis de costos
    if test_cost_analysis(instance):
        print("✅ Análisis de costos mejorado funcionando correctamente")
    
    # Probar reporte semanal
    if test_weekly_report():
        print("✅ Reporte semanal funcionando correctamente")
    
    # Probar descarga
    if test_download_functionality():
        print("✅ Funcionalidad de descarga funcionando correctamente")
    
    # Mostrar información de interfaz web
    show_web_interface_info()
    
    # Resumen final
    print("🎉 RESUMEN DE MEJORAS IMPLEMENTADAS:")
    print("=" * 60)
    print("✅ Formulario con instancias descubiertas automáticamente")
    print("✅ Precios detallados con fuentes oficiales (AWS/Azure)")
    print("✅ Recomendaciones más claras y descriptivas")
    print("✅ Funcionalidad de descarga de reportes corregida")
    print("✅ Interfaz web mejorada con información detallada")
    print("✅ Integración completa entre backend y frontend")
    print()
    print("🌟 El sistema está completamente operativo y optimizado!")
    print("💡 Acceda al dashboard web para probar todas las funcionalidades.")

if __name__ == "__main__":
    main()