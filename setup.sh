#!/bin/bash

set -e

echo "---------------------------------------------------"
echo "--- BIENVENIDO A LA CONFIGURACIÓN DEL PRODUCTO OPTIMON ---"
echo "---------------------------------------------------"
echo "Este script te guiará para desplegar y monitorear tu infraestructura."
echo "Soporta: Servidores Físicos, Azure y AWS"
echo "NUEVO: Genera código IaC automáticamente basado en tu infraestructura"
echo

# --- FASE 0: Verificar prerrequisitos ---
echo "Verificando prerrequisitos..."

command -v jq >/dev/null 2>&1 || { echo "[ERROR] 'jq' no está instalado. Instálalo con: sudo apt install jq"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "[ERROR] 'docker-compose' no está instalado. Instálalo con: sudo apt install docker-compose"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] 'python3' no está instalado. Instálalo con: sudo apt install python3"; exit 1; }

if [[ ! -f "iac_generator.py" ]]; then
    echo "[WARNING] No se encuentra el generador de IaC (iac_generator.py)"
    echo "El monitoreo continuará sin generación automática de IaC"
    SKIP_IAC=1
else
    SKIP_IAC=0
fi

echo "[OK] Prerrequisitos verificados correctamente"
echo

# --- FASE 1: Seleccionar tipo de infraestructura ---
while true; do
    echo "Selecciona el tipo de infraestructura a escanear:"
    echo "[1] Servidor físico (este equipo)"
    echo "[2] Servidores en la nube (Azure)"
    echo "[3] Servidores en la nube (AWS)"
    echo "[0] Salir"
    read -rp "Opción (1-3, 0 para salir): " OPTION
    echo

    case "$OPTION" in
        0) echo "Gracias por usar OptiMon!"; exit 0 ;;
        1) PROVIDER="local"; break ;;
        2) PROVIDER="azure"; break ;;
        3) PROVIDER="aws"; break ;;
        *) echo "[ERROR] Opción inválida. Por favor selecciona 1, 2, 3 o 0."; echo ;;
    esac
done

# --- FASE 2A: Configuración para servidor físico ---
if [[ "$PROVIDER" == "local" ]]; then
    echo "Configurando monitoreo del servidor local..."
    MONITORING_DIR="2-INICIAR-MONITOREO"

    if [[ ! -d "$MONITORING_DIR" ]]; then
        echo "[ERROR] Directorio $MONITORING_DIR no existe."
        exit 1
    fi

    mkdir -p "$MONITORING_DIR/config/prometheus"

    # Crear prometheus.yml para localhost
    cat > "$MONITORING_DIR/config/prometheus/prometheus.yml" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "windows_exporter"
    static_configs:
      - targets: ["host.docker.internal:9182"]
EOF

    # Crear archivo de reglas de alertas básico si no existe
    if [[ ! -f "$MONITORING_DIR/config/prometheus/alert.rules.yml" ]]; then
        cat > "$MONITORING_DIR/config/prometheus/alert.rules.yml" <<EOF
groups:
  - name: optimon_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - avg(rate(windows_cpu_time_total{mode="idle"}[2m])) * 100 > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 2 minutes"

      - alert: HighMemoryUsage
        expr: (windows_os_physical_memory_free_bytes / windows_cs_physical_memory_bytes) * 100 < 20
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 80% for more than 5 minutes"
EOF
    fi

    echo "[OK] Configuración de Prometheus creada para servidor local"
    echo "[OK] Dashboard OptiMon ya está configurado"
    echo "[OK] Alertas personalizables disponibles en: $MONITORING_DIR/config/prometheus/alert.rules.yml"
    echo

    echo "Iniciando Prometheus y Grafana..."
    if [[ -f "$MONITORING_DIR/docker-compose.yml" ]]; then
        (cd "$MONITORING_DIR" && docker-compose up -d)
    else
        echo "[ERROR] No se encuentra docker-compose.yml en $MONITORING_DIR"
        exit 1
    fi

    echo
    echo "Esperando 30 segundos a que los servicios se inicialicen..."
    sleep 30

    if [[ "$SKIP_IAC" == "0" ]]; then
        echo
        echo "=== GENERANDO CÓDIGO IaC AUTOMÁTICAMENTE ==="
        echo "Escaneando infraestructura local y generando Terraform/Ansible..."
        echo
        echo 1 | python3 iac_generator.py || echo "[WARNING] El generador IaC encontró algunos problemas, pero el monitoreo continúa..."
    fi

    echo
    echo "---------------------------------------------------------"
    echo "Monitoreo del servidor local iniciado!"
    echo "Dashboard Grafana: http://localhost:3000  (admin/admin)"
    echo "Dashboard OptiMon: Ya importado automáticamente"
    echo "Prometheus: http://localhost:9090"
    if [[ "$SKIP_IAC" == "0" ]]; then
        echo "CÓDIGO IaC GENERADO:"
        echo "- Revisa la carpeta 3-CODIGO-GENERADO/version_X/"
        echo "- Contiene: Terraform, Ansible y reporte de infraestructura"
    fi
    echo "---------------------------------------------------------"
    exit 0
fi

# --- FASE 2B: Configuración para servidores Azure ---
if [[ "$PROVIDER" == "azure" ]]; then
    echo "Por favor, introduce tus credenciales de Azure (Service Principal):"
    read -rp "Azure Client ID: " AZURE_CLIENT_ID
    [[ -z "$AZURE_CLIENT_ID" ]] && echo "[ERROR] Client ID no puede estar vacío" && exit 1

    read -rp "Azure Client Secret: " AZURE_CLIENT_SECRET
    [[ -z "$AZURE_CLIENT_SECRET" ]] && echo "[ERROR] Client Secret no puede estar vacío" && exit 1

    read -rp "Azure Tenant ID: " AZURE_TENANT_ID
    [[ -z "$AZURE_TENANT_ID" ]] && echo "[ERROR] Tenant ID no puede estar vacío" && exit 1

    read -rp "Azure Subscription ID: " AZURE_SUBSCRIPTION_ID
    [[ -z "$AZURE_SUBSCRIPTION_ID" ]] && echo "[ERROR] Subscription ID no puede estar vacío" && exit 1

    echo
    read -rp "Crea una contraseña para la nueva Máquina Virtual: " VM_PASSWORD
    [[ -z "$VM_PASSWORD" ]] && echo "[ERROR] La contraseña no puede estar vacía" && exit 1

    if [[ ! -d "1-CREAR-INFRAESTRUCTURA" ]]; then
        echo "[ERROR] Directorio 1-CREAR-INFRAESTRUCTURA no existe"
        exit 1
    fi

    cd "1-CREAR-INFRAESTRUCTURA"

    if [[ -f "provider-azure.tf" ]]; then
        cp "provider-azure.tf" "provider.tf"
    else
        echo "[ERROR] No se encuentra provider-azure.tf"
        exit 1
    fi

    echo "vm_password = \"$VM_PASSWORD\"" > terraform.tfvars

    echo "Ejecutando terraform init..."
    terraform init -upgrade || { echo "[ERROR] Fallo terraform init"; exit 1; }

    echo "Ejecutando terraform apply..."
    terraform apply -auto-approve || { echo "[ERROR] Fallo terraform apply"; exit 1; }

    VM_PRIVATE_IP=$(terraform output -raw vm_private_ip 2>/dev/null)
    VM_PUBLIC_IP=$(terraform output -raw vm_public_ip 2>/dev/null)

    if [[ -z "$VM_PUBLIC_IP" ]]; then
        echo "[ERROR] No se pudo obtener la IP pública de la VM"
        exit 1
    fi

    echo "[OK] VM Azure desplegada - IP: $VM_PUBLIC_IP"
    cd ..

    MONITORING_DIR="2-INICIAR-MONITOREO"

    mkdir -p "$MONITORING_DIR/config/prometheus"

    # Crear prometheus.yml para Azure VM
    cat > "$MONITORING_DIR/config/prometheus/prometheus.yml" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "azure_vm"
    static_configs:
      - targets: ["$VM_PUBLIC_IP:9100"]
    scrape_interval: 30s
    scrape_timeout: 10s
EOF

    if [[ -f "$MONITORING_DIR/docker-compose.yml" ]]; then
        (cd "$MONITORING_DIR" && docker-compose up -d)
    else
        echo "[ERROR] No se encuentra docker-compose.yml en $MONITORING_DIR"
        exit 1
    fi

    echo
    echo "Esperando 45 segundos a que Azure VM y servicios se inicialicen..."
    sleep 45

    if [[ "$SKIP_IAC" == "0" ]]; then
        echo
        echo "=== GENERANDO CÓDIGO IaC AUTOMÁTICAMENTE ==="
        echo "Escaneando infraestructura Azure + Local y generando Terraform/Ansible..."
        echo
        echo 3 | python3 iac_generator.py || echo "[WARNING] El generador IaC encontró algunos problemas, pero continúa..."
    fi

    echo
    echo "---------------------------------------------------------"
    echo "Infraestructura Azure desplegada!"
    echo "IP Pública VM: $VM_PUBLIC_IP"
    echo "Dashboard Grafana: http://localhost:3000  (admin/admin)"
    echo "Dashboard OptiMon: Ya importado automáticamente"
    if [[ "$SKIP_IAC" == "0" ]]; then
        echo "CÓDIGO IaC GENERADO:"
        echo "- Revisa la carpeta 3-CODIGO-GENERADO/version_X/"
        echo "- Contiene: Terraform para replicar Azure VM + Local"
        echo "- Playbooks Ansible para configuración automática"
    fi
    echo "---------------------------------------------------------"
    exit 0
fi

# --- FASE 2C: Configuración para servidores AWS ---
if [[ "$PROVIDER" == "aws" ]]; then
    echo "Por favor, introduce tus credenciales de AWS:"
    read -rp "AWS Access Key ID: " AWS_ACCESS_KEY_ID
    [[ -z "$AWS_ACCESS_KEY_ID" ]] && echo "[ERROR] Access Key ID no puede estar vacío" && exit 1

    read -rp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
    [[ -z "$AWS_SECRET_ACCESS_KEY" ]] && echo "[ERROR] Secret Access Key no puede estar vacío" && exit 1

    read -rp "AWS Region (ej: us-east-1): " AWS_REGION
    [[ -z "$AWS_REGION" ]] && AWS_REGION="us-east-1"

    echo
    echo "NOTA: Se creará un Key Pair para acceso SSH."
    read -rp "Nombre para el Key Pair (ej: optimon-key): " KEY_NAME
    [[ -z "$KEY_NAME" ]] && KEY_NAME="optimon-key"
    echo

    if [[ ! -d "1-CREAR-INFRAESTRUCTURA" ]]; then
        echo "[ERROR] Directorio 1-CREAR-INFRAESTRUCTURA no existe"
        exit 1
    fi

    cd "1-CREAR-INFRAESTRUCTURA"

    echo "aws_region = \"$AWS_REGION\"" > terraform.tfvars
    echo "key_name = \"$KEY_NAME\"" >> terraform.tfvars
    echo "instance_type = \"t3.micro\"" >> terraform.tfvars

    echo "Ejecutando terraform init..."
    terraform init -upgrade || { echo "[ERROR] Fallo terraform init"; exit 1; }

    echo "Ejecutando terraform apply..."
    terraform apply -auto-approve || { echo "[ERROR] Fallo terraform apply"; exit 1; }

    INSTANCE_PRIVATE_IP=$(terraform output -raw instance_private_ip 2>/dev/null)
    INSTANCE_PUBLIC_IP=$(terraform output -raw instance_public_ip 2>/dev/null)

    if [[ -z "$INSTANCE_PUBLIC_IP" ]]; then
        echo "[ERROR] No se pudo obtener la IP pública de la instancia EC2"
        exit 1
    fi

    echo "[OK] Instancia EC2 desplegada - IP: $INSTANCE_PUBLIC_IP"
    cd ..

    MONITORING_DIR="2-INICIAR-MONITOREO"

    mkdir -p "$MONITORING_DIR/config/prometheus"

    # Crear prometheus.yml para AWS EC2
    cat > "$MONITORING_DIR/config/prometheus/prometheus.yml" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "aws_ec2"
    static_configs:
      - targets: ["$INSTANCE_PUBLIC_IP:9100"]
    scrape_interval: 30s
    scrape_timeout: 10s
EOF

    if [[ -f "$MONITORING_DIR/docker-compose.yml" ]]; then
        (cd "$MONITORING_DIR" && docker-compose up -d)
    else
        echo "[ERROR] No se encuentra docker-compose.yml en $MONITORING_DIR"
        exit 1
    fi

    echo
    echo "Esperando 45 segundos a que AWS EC2 y servicios se inicialicen..."
    sleep 45

    if [[ "$SKIP_IAC" == "0" ]]; then
        echo
        echo "=== GENERANDO CÓDIGO IaC AUTOMÁTICAMENTE ==="
        echo "Escaneando infraestructura AWS + Local y generando Terraform/Ansible..."
        echo
        echo 2 | python3 iac_generator.py || echo "[WARNING] El generador IaC encontró algunos problemas, pero continúa..."
    fi

    echo
    echo "---------------------------------------------------------"
    echo "Infraestructura AWS desplegada!"
    echo "IP Pública EC2: $INSTANCE_PUBLIC_IP"
    echo "Dashboard Grafana: http://localhost:3000  (admin/admin)"
    echo "Dashboard OptiMon: Ya importado automáticamente"
    echo "IMPORTANTE: Descarga la clave privada desde la consola AWS"
    if [[ "$SKIP_IAC" == "0" ]]; then
        echo "CÓDIGO IaC GENERADO:"
        echo "- Revisa la carpeta 3-CODIGO-GENERADO/version_X/"
        echo "- Contiene: Terraform para replicar EC2 + Local"
        echo "- Playbooks Ansible para configuración automática"
    fi
    echo "---------------------------------------------------------"