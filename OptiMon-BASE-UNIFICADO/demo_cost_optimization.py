#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Demo: Motor de Optimización de Costos OptiMon v3.1.0
====================================================
Demostración completa del sistema de recomendaciones para optimización de costos
"""

import sys
import json
from pathlib import Path
from cost_optimization_engine import CostOptimizationEngine

def print_banner():
    """Mostrar banner del demo"""
    print("=" * 70)
    print("🎯 DEMO: MOTOR DE OPTIMIZACIÓN DE COSTOS OptiMon v3.1.0")
    print("=" * 70)
    print("💡 Sistema Inteligente de Recomendaciones para Reducir Costos Cloud")
    print()

def simulate_aws_instances():
    """Simular diferentes tipos de instancias AWS con varios patrones de uso"""
    return [
        {
            "id": "i-0123456789abcdef0",
            "type": "t3.large",
            "provider": "aws",
            "scenario": "Servidor subutilizado",
            "metrics": {
                "cpu_average": 8.5,
                "cpu_max": 25.0,
                "memory_average": 15.2,
                "memory_max": 30.5,
                "network_in": 5000000,  # 5MB
                "network_out": 2000000  # 2MB
            }
        },
        {
            "id": "i-0987654321fedcba0",
            "type": "t3.medium",
            "provider": "aws", 
            "scenario": "Servidor con uso variable",
            "metrics": {
                "cpu_average": 35.8,
                "cpu_max": 89.3,
                "memory_average": 45.7,
                "memory_max": 78.2,
                "network_in": 50000000,  # 50MB
                "network_out": 25000000  # 25MB
            }
        },
        {
            "id": "i-abcdef0123456789",
            "type": "m5.large",
            "provider": "aws",
            "scenario": "Servidor con uso intensivo constante",
            "metrics": {
                "cpu_average": 78.9,
                "cpu_max": 95.4,
                "memory_average": 82.1,
                "memory_max": 96.8,
                "network_in": 200000000,  # 200MB
                "network_out": 150000000  # 150MB
            }
        },
        {
            "id": "i-fedcba0987654321",
            "type": "t3.small",
            "provider": "aws",
            "scenario": "Servidor prácticamente inactivo",
            "metrics": {
                "cpu_average": 2.1,
                "cpu_max": 8.5,
                "memory_average": 12.3,
                "memory_max": 18.7,
                "network_in": 1000000,   # 1MB
                "network_out": 500000    # 0.5MB
            }
        }
    ]

def simulate_azure_instances():
    """Simular instancias Azure con diferentes patrones"""
    return [
        {
            "id": "vm-web-prod-001",
            "type": "Standard_D2s_v3",
            "provider": "azure",
            "scenario": "VM de producción bien optimizada",
            "metrics": {
                "cpu_average": 55.2,
                "cpu_max": 75.8,
                "memory_average": 60.1,
                "memory_max": 80.3,
                "network_in": 80000000,  # 80MB
                "network_out": 45000000  # 45MB
            }
        },
        {
            "id": "vm-dev-test-002",
            "type": "Standard_B2ms",
            "provider": "azure",
            "scenario": "VM de desarrollo sobredimensionada",
            "metrics": {
                "cpu_average": 12.8,
                "cpu_max": 40.2,
                "memory_average": 25.5,
                "memory_max": 50.1,
                "network_in": 10000000,  # 10MB
                "network_out": 5000000   # 5MB
            }
        }
    ]

def print_instance_analysis(instance, analysis, recommendations):
    """Mostrar análisis detallado de una instancia"""
    print(f"🖥️  INSTANCIA: {instance['id']}")
    print(f"   📋 Tipo: {instance['type']} ({instance['provider'].upper()})")
    print(f"   📊 Escenario: {instance['scenario']}")
    print()
    
    # Métricas de utilización
    cpu_util = analysis['cpu_utilization']
    memory_util = analysis['memory_utilization']
    
    print(f"   📈 UTILIZACIÓN DE RECURSOS:")
    print(f"      🔥 CPU: {cpu_util['average']:.1f}% promedio, {cpu_util['max']:.1f}% máximo")
    print(f"         Puntuación: {cpu_util['score'].upper()}")
    print(f"      🧠 Memoria: {memory_util['average']:.1f}% promedio, {memory_util['max']:.1f}% máximo")
    print(f"         Puntuación: {memory_util['score'].upper()}")
    print(f"      🔄 Patrón de uso: {analysis['usage_pattern'].upper()}")
    print()
    
    # Recomendaciones
    if recommendations:
        print(f"   💡 RECOMENDACIONES ({len(recommendations)}):")
        total_savings = 0
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }
            
            print(f"      {priority_icon.get(rec['priority'], '⚪')} {i}. {rec['type'].replace('_', ' ').title()}")
            print(f"         📄 {rec['description']}")
            
            if 'estimated_monthly_savings' in rec and isinstance(rec['estimated_monthly_savings'], (int, float)):
                savings = rec['estimated_monthly_savings']
                total_savings += savings
                print(f"         💰 Ahorro estimado: ${savings:.2f}/mes")
            
            if 'current_instance' in rec and 'recommended_instance' in rec:
                print(f"         🔄 Cambio: {rec['current_instance']} → {rec['recommended_instance']}")
                
            print(f"         🛠️  Implementación: {rec.get('implementation', 'Ver documentación')}")
            print(f"         ⚠️  Riesgo: {rec.get('risk_level', 'N/A')}")
            print()
        
        if total_savings > 0:
            print(f"   💸 AHORRO TOTAL ESTIMADO: ${total_savings:.2f}/mes (${total_savings * 12:.2f}/año)")
        else:
            print(f"   ✅ INSTANCIA OPTIMIZADA: No se requieren cambios")
    else:
        print(f"   ✅ INSTANCIA OPTIMIZADA: No se encontraron oportunidades de mejora")
    
    print("-" * 70)
    print()

def generate_summary_report(all_analyses, all_recommendations):
    """Generar reporte resumen de todas las instancias"""
    print("📊 REPORTE RESUMEN DE OPTIMIZACIÓN")
    print("=" * 50)
    
    total_instances = len(all_analyses)
    total_recommendations = sum(len(recs) for recs in all_recommendations)
    total_savings = 0
    
    recommendations_by_type = {}
    recommendations_by_priority = {'high': 0, 'medium': 0, 'low': 0}
    
    for recs in all_recommendations:
        for rec in recs:
            # Contar por tipo
            rec_type = rec.get('type', 'other')
            recommendations_by_type[rec_type] = recommendations_by_type.get(rec_type, 0) + 1
            
            # Contar por prioridad
            priority = rec.get('priority', 'low')
            recommendations_by_priority[priority] = recommendations_by_priority.get(priority, 0) + 1
            
            # Sumar ahorros
            if 'estimated_monthly_savings' in rec and isinstance(rec['estimated_monthly_savings'], (int, float)):
                total_savings += rec['estimated_monthly_savings']
    
    print(f"🎯 Instancias analizadas: {total_instances}")
    print(f"💡 Total de recomendaciones: {total_recommendations}")
    print(f"💰 Ahorro potencial mensual: ${total_savings:.2f}")
    print(f"💰 Ahorro potencial anual: ${total_savings * 12:.2f}")
    print()
    
    print("📈 DISTRIBUCIÓN POR PRIORIDAD:")
    for priority, count in recommendations_by_priority.items():
        percentage = (count / total_recommendations * 100) if total_recommendations > 0 else 0
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[priority]
        print(f"   {icon} {priority.capitalize()}: {count} ({percentage:.1f}%)")
    print()
    
    print("🏷️  DISTRIBUCIÓN POR TIPO:")
    for rec_type, count in recommendations_by_type.items():
        percentage = (count / total_recommendations * 100) if total_recommendations > 0 else 0
        print(f"   📋 {rec_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    print()
    
    # ROI estimado
    if total_savings > 0:
        annual_savings = total_savings * 12
        print("💹 RETORNO DE INVERSIÓN (ROI):")
        print(f"   📅 Ahorro mensual: ${total_savings:.2f}")
        print(f"   📅 Ahorro anual: ${annual_savings:.2f}")
        print(f"   🎯 Implementando solo recomendaciones de alta prioridad:")
        high_priority_savings = sum(
            rec.get('estimated_monthly_savings', 0) 
            for recs in all_recommendations 
            for rec in recs 
            if rec.get('priority') == 'high' and isinstance(rec.get('estimated_monthly_savings'), (int, float))
        )
        print(f"      💰 Ahorro garantizado: ${high_priority_savings:.2f}/mes")
        print(f"      💰 Ahorro garantizado anual: ${high_priority_savings * 12:.2f}")

def main():
    """Función principal del demo"""
    print_banner()
    
    # Inicializar motor
    engine = CostOptimizationEngine()
    
    # Obtener instancias de prueba
    aws_instances = simulate_aws_instances()
    azure_instances = simulate_azure_instances()
    all_instances = aws_instances + azure_instances
    
    all_analyses = []
    all_recommendations = []
    
    print(f"🔍 Analizando {len(all_instances)} instancias ({len(aws_instances)} AWS, {len(azure_instances)} Azure)...")
    print()
    
    # Analizar cada instancia
    for instance in all_instances:
        # Realizar análisis
        analysis = engine.analyze_resource_utilization(
            instance['provider'], 
            instance['id'], 
            instance['metrics']
        )
        
        # Generar recomendaciones
        recommendations = engine.generate_cost_recommendations(
            analysis, 
            instance['type']
        )
        
        # Agregar a listas
        all_analyses.append(analysis)
        all_recommendations.append(recommendations)
        
        # Agregar al cache del motor para reporte semanal
        engine.recommendations_cache.extend(recommendations)
        
        # Mostrar análisis individual
        print_instance_analysis(instance, analysis, recommendations)
    
    # Generar reporte resumen
    generate_summary_report(all_analyses, all_recommendations)
    
    # Generar reporte semanal
    print("📅 REPORTE SEMANAL AUTOMÁTICO")
    print("=" * 40)
    weekly_report = engine.generate_weekly_report()
    
    print(f"📋 Período: {weekly_report.get('period', 'semanal')}")
    print(f"📅 Fecha: {weekly_report.get('report_date', 'N/A')}")
    
    summary = weekly_report.get('summary', {})
    print(f"💡 Total recomendaciones: {summary.get('total_recommendations', 0)}")
    print(f"🔴 Elementos prioritarios: {summary.get('high_priority_items', 0)}")
    print(f"💰 Ahorro potencial: ${summary.get('potential_monthly_savings', 0):.2f}/mes")
    
    print()
    print("✅ Demo completado. OptiMon Motor de Optimización está listo para usar!")
    print("🌐 Acceda al dashboard web en: http://localhost:5000/cost-optimization")

if __name__ == "__main__":
    main()