#!/bin/bash
# OptiMon - Comandos de Automatización
# Para sistemas Unix/Linux

set -e

COMMAND=$1
TARGET=$2

show_help() {
    echo "🚀 OptiMon - Sistema de Monitoreo"
    echo "================================="
    echo ""
    echo "Comandos disponibles:"
    echo ""
    echo "  setup          - Despliegue completo del sistema"
    echo "  start          - Iniciar servicios"
    echo "  stop           - Detener servicios"
    echo "  restart        - Reiniciar servicios"
    echo "  status         - Ver estado de servicios"
    echo "  logs           - Ver logs de servicios"
    echo "  test           - Ejecutar pruebas del sistema"
    echo "  config         - Regenerar configuraciones"
    echo "  package        - Crear paquete ZIP para distribución"
    echo "  clean          - Limpiar datos y contenedores"
    echo ""
    echo "Comandos específicos:"
    echo "  add-server     - Añadir servidor físico"
    echo "  list-servers   - Listar servidores configurados"
    echo "  setup-aws      - Configurar monitoreo AWS"
    echo "  setup-azure    - Configurar monitoreo Azure"
    echo ""
    echo "Ejemplos:"
    echo "  ./make.sh setup"
    echo "  ./make.sh logs prometheus"
    echo "  ./make.sh restart grafana"
}

invoke_setup() {
    echo "🚀 Iniciando despliegue completo..."
    ./deploy.sh
}

invoke_start() {
    echo "▶️  Iniciando servicios..."
    docker-compose up -d
    echo "✅ Servicios iniciados"
}

invoke_stop() {
    echo "⏹️  Deteniendo servicios..."
    docker-compose down
    echo "✅ Servicios detenidos"
}

invoke_restart() {
    if [ -n "$TARGET" ]; then
        echo "🔄 Reiniciando servicio: $TARGET"
        docker-compose restart "$TARGET"
    else
        echo "🔄 Reiniciando todos los servicios..."
        docker-compose restart
    fi
    echo "✅ Reinicio completado"
}

show_status() {
    echo "📊 Estado de servicios:"
    docker-compose ps
    
    echo ""
    echo "🌐 URLs de acceso:"
    echo "  • Grafana:      http://localhost:3000"
    echo "  • Prometheus:   http://localhost:9090"
    echo "  • AlertManager: http://localhost:9093"
}

show_logs() {
    if [ -n "$TARGET" ]; then
        echo "📋 Logs de $TARGET"
        docker-compose logs -f "$TARGET"
    else
        echo "📋 Logs de todos los servicios"
        docker-compose logs -f
    fi
}

invoke_test() {
    echo "🧪 Ejecutando pruebas del sistema..."
    python3 test_system.py
}

invoke_config() {
    echo "⚙️  Regenerando configuraciones..."
    python3 scripts/setup_prometheus.py
    echo "🔄 Reiniciando Prometheus..."
    docker-compose restart prometheus
    echo "✅ Configuración actualizada"
}

invoke_package() {
    echo "📦 Creando paquete de distribución..."
    python3 create_package.py
}

invoke_clean() {
    echo "🧹 Limpiando sistema..."
    
    read -p "¿Estás seguro? Esto eliminará todos los datos (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Eliminando contenedores y volúmenes..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo "✅ Limpieza completada"
    else
        echo "❌ Operación cancelada"
    fi
}

invoke_add_server() {
    echo "🖥️  Añadir servidor físico"
    ./add_server.sh
}

invoke_list_servers() {
    echo "📋 Servidores configurados:"
    python3 scripts/add_physical_server.py list
}

invoke_setup_aws() {
    echo "☁️  Configurando monitoreo AWS..."
    python3 scripts/setup_aws_monitoring.py
}

invoke_setup_azure() {
    echo "☁️  Configurando monitoreo Azure..."
    python3 scripts/setup_azure_monitoring.py
}

# Función principal
case "${COMMAND,,}" in
    "setup")
        invoke_setup
        ;;
    "start")
        invoke_start
        ;;
    "stop")
        invoke_stop
        ;;
    "restart")
        invoke_restart
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        invoke_test
        ;;
    "config")
        invoke_config
        ;;
    "package")
        invoke_package
        ;;
    "clean")
        invoke_clean
        ;;
    "add-server")
        invoke_add_server
        ;;
    "list-servers")
        invoke_list_servers
        ;;
    "setup-aws")
        invoke_setup_aws
        ;;
    "setup-azure")
        invoke_setup_azure
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Comando no reconocido: $COMMAND"
        echo "Usa './make.sh help' para ver comandos disponibles"
        exit 1
        ;;
esac