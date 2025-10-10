#!/bin/bash
# Script de instalación automática de Node Exporter para VM física
# Ejecutar con: curl -sSL https://raw.githubusercontent.com/.../install_node_exporter.sh | bash

set -e

echo "🚀 Instalando Node Exporter en servidor físico..."

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="darwin"
else
    echo "❌ Sistema operativo no soportado: $OSTYPE"
    exit 1
fi

# Detectar arquitectura
ARCH=$(uname -m)
case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    armv7l) ARCH="armv7" ;;
    *) echo "❌ Arquitectura no soportada: $ARCH"; exit 1 ;;
esac

# Variables
NODE_EXPORTER_VERSION="1.6.1"
NODE_EXPORTER_USER="node_exporter"
NODE_EXPORTER_DIR="/opt/node_exporter"
SERVICE_FILE="/etc/systemd/system/node_exporter.service"

echo "📋 Configuración detectada:"
echo "   OS: $OS"
echo "   Arquitectura: $ARCH"
echo "   Versión Node Exporter: $NODE_EXPORTER_VERSION"

# Verificar permisos de sudo
if [[ $EUID -ne 0 ]]; then
    echo "🔐 Este script requiere permisos de administrador"
    echo "   Ejecuta: sudo $0"
    exit 1
fi

# Crear usuario para node_exporter
echo "👤 Creando usuario $NODE_EXPORTER_USER..."
if ! id "$NODE_EXPORTER_USER" &>/dev/null; then
    useradd --no-create-home --shell /bin/false $NODE_EXPORTER_USER
fi

# Crear directorio
echo "📁 Creando directorio $NODE_EXPORTER_DIR..."
mkdir -p $NODE_EXPORTER_DIR
chown $NODE_EXPORTER_USER:$NODE_EXPORTER_USER $NODE_EXPORTER_DIR

# Descargar Node Exporter
echo "⬇️  Descargando Node Exporter $NODE_EXPORTER_VERSION..."
cd /tmp
DOWNLOAD_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.${OS}-${ARCH}.tar.gz"

curl -LO "$DOWNLOAD_URL"
tar xvf "node_exporter-${NODE_EXPORTER_VERSION}.${OS}-${ARCH}.tar.gz"

# Instalar binario
echo "📦 Instalando binario..."
cp "node_exporter-${NODE_EXPORTER_VERSION}.${OS}-${ARCH}/node_exporter" $NODE_EXPORTER_DIR/
chown $NODE_EXPORTER_USER:$NODE_EXPORTER_USER $NODE_EXPORTER_DIR/node_exporter
chmod +x $NODE_EXPORTER_DIR/node_exporter

# Crear servicio systemd
echo "⚙️  Configurando servicio systemd..."
cat > $SERVICE_FILE << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=$NODE_EXPORTER_USER
Group=$NODE_EXPORTER_USER
Type=simple
ExecStart=$NODE_EXPORTER_DIR/node_exporter \\
    --web.listen-address=:9100 \\
    --path.procfs=/proc \\
    --path.sysfs=/sys \\
    --collector.filesystem.mount-points-exclude='^/(dev|proc|sys|var/lib/docker/.+|var/lib/kubelet/.+)($|/)' \\
    --collector.filesystem.fs-types-exclude='^(autofs|binfmt_misc|bpf|cgroup2?|configfs|debugfs|devpts|devtmpfs|fusectl|hugetlbfs|iso9660|mqueue|nsfs|overlay|proc|procfs|pstore|rpc_pipefs|securityfs|selinuxfs|squashfs|sysfs|tracefs)$'

SyslogIdentifier=node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configurar firewall (si está activo)
echo "🔥 Configurando firewall..."
if command -v ufw &> /dev/null; then
    echo "   Detectado UFW, abriendo puerto 9100..."
    ufw allow 9100/tcp
elif command -v firewall-cmd &> /dev/null; then
    echo "   Detectado firewalld, abriendo puerto 9100..."
    firewall-cmd --permanent --add-port=9100/tcp
    firewall-cmd --reload
elif command -v iptables &> /dev/null; then
    echo "   Configurando iptables para puerto 9100..."
    iptables -A INPUT -p tcp --dport 9100 -j ACCEPT
    # Intentar guardar reglas
    if command -v iptables-save &> /dev/null; then
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    fi
fi

# Habilitar e iniciar servicio
echo "🚀 Iniciando servicio Node Exporter..."
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

# Verificar estado
echo "✅ Verificando instalación..."
sleep 2
if systemctl is-active --quiet node_exporter; then
    echo "✅ Node Exporter instalado correctamente!"
    echo "📊 Métricas disponibles en: http://$(hostname -I | awk '{print $1}'):9100/metrics"
    echo "🔍 Estado del servicio:"
    systemctl status node_exporter --no-pager -l
else
    echo "❌ Error: Node Exporter no está ejecutándose"
    echo "🔍 Logs del servicio:"
    journalctl -u node_exporter --no-pager -l
    exit 1
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -rf /tmp/node_exporter-*

echo ""
echo "🎉 ¡Instalación completada!"
echo "📋 Información del servidor:"
echo "   IP: $(hostname -I | awk '{print $1}')"
echo "   Puerto: 9100"
echo "   Métricas: http://$(hostname -I | awk '{print $1}'):9100/metrics"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Agrega este servidor a tu configuración OptiMon"
echo "   2. Ejecuta el setup automático de OptiMon"
echo "   3. Verifica las métricas en Grafana"