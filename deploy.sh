#!/bin/bash
# OptiMon Deployment Script
# Automated deployment for infrastructure monitoring

set -e

echo "🚀 OptiMon - Sistema de Monitoreo de Infraestructura"
echo "=================================================="

# Verificar prerrequisitos
check_prerequisites() {
    echo "📋 Verificando prerrequisitos..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker no está instalado"
        echo "Por favor instala Docker antes de continuar"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose no está instalado"
        echo "Por favor instala Docker Compose antes de continuar"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 no está instalado"
        echo "Por favor instala Python 3 antes de continuar"
        exit 1
    fi
    
    echo "✅ Todos los prerrequisitos están instalados"
}

# Instalar dependencias Python
install_python_deps() {
    echo "📦 Instalando dependencias Python..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        echo "✅ Dependencias Python instaladas"
    else
        echo "⚠️  Archivo requirements.txt no encontrado"
    fi
}

# Configurar credenciales
setup_credentials() {
    echo "🔐 Configurando credenciales..."
    
    if [ ! -f "config/credentials.simple.yml" ]; then
        echo "⚠️  No se encontró archivo de credenciales simplificado"
        echo "Por favor configura tus credenciales de nube en:"
        echo "  - config/credentials.simple.yml"
        echo ""
        echo "Solo necesitas completar las credenciales de AWS o Azure"
        echo "El sistema detectará automáticamente toda la infraestructura"
        
        read -p "¿Quieres continuar sin credenciales de nube? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "✅ Archivo de credenciales simplificado encontrado"
        echo "El sistema detectará automáticamente toda la infraestructura"
    fi
}

# Inicializar configuración de Prometheus
setup_prometheus() {
    echo "⚙️  Configurando Prometheus..."
    
    if [ ! -f "config/prometheus/prometheus.yml" ]; then
        echo "📝 Creando configuración inicial de Prometheus"
        python3 scripts/setup_prometheus.py
    fi
    
    echo "✅ Prometheus configurado"
}

# Iniciar servicios Docker
start_services() {
    echo "🐳 Iniciando servicios Docker..."
    
    # Detener servicios existentes si están corriendo
    docker-compose down 2>/dev/null || true
    
    # Construir e iniciar servicios
    docker-compose up -d
    
    echo "✅ Servicios iniciados exitosamente"
}

# Verificar que los servicios están funcionando
verify_services() {
    echo "🔍 Verificando servicios..."
    
    # Esperar unos segundos para que los servicios inicien
    sleep 10
    
    services=("prometheus:9090" "grafana:3000" "alertmanager:9093")
    
    for service in "${services[@]}"; do
        service_name="${service%:*}"
        port="${service#*:}"
        
        if curl -s "http://localhost:${port}" > /dev/null 2>&1; then
            echo "✅ ${service_name} está funcionando en puerto ${port}"
        else
            echo "❌ ${service_name} no responde en puerto ${port}"
        fi
    done
}

# Configurar infraestructura automáticamente
auto_discover() {
    echo "🤖 Iniciando descubrimiento automático..."
    
    if [ -f "config/credentials.simple.yml" ]; then
        echo "🔄 Ejecutando configuración 100% automática..."
        echo "Esto detectará e instalará Node Exporter automáticamente"
        python3 scripts/auto_setup.py
    else
        echo "⚠️  Configuración manual disponible:"
        
        if [ -f "config/aws-credentials.yml" ]; then
            echo "🔄 Configurando monitoreo AWS..."
            python3 scripts/setup_aws_monitoring.py
        fi
        
        if [ -f "config/azure-credentials.yml" ]; then
            echo "🔄 Configurando monitoreo Azure..."
            python3 scripts/setup_azure_monitoring.py
        fi
    fi
    
    echo "✅ Configuración automática completada"
}

# Mostrar información final
show_final_info() {
    echo ""
    echo "🎉 ¡Despliegue completado exitosamente!"
    echo "======================================"
    echo ""
    echo "📊 Accede a los servicios:"
    echo "  • Grafana:      http://localhost:3000 (admin/admin)"
    echo "  • Prometheus:   http://localhost:9090"
    echo "  • AlertManager: http://localhost:9093"
    echo ""
    echo "🛠️  Comandos útiles:"
    echo "  • Ver logs:           docker-compose logs -f"
    echo "  • Detener servicios:  docker-compose down"
    echo "  • Reiniciar:          docker-compose restart"
    echo "  • Añadir servidor:    ./scripts/add_server.sh"
    echo ""
    echo "📖 Para más información, consulta README.md"
}

# Función principal
main() {
    check_prerequisites
    install_python_deps
    setup_credentials
    setup_prometheus
    start_services
    verify_services
    auto_discover
    show_final_info
}

# Manejar interrupciones
trap 'echo "❌ Despliegue interrumpido"; exit 1' INT TERM

# Ejecutar función principal
main "$@"