#!/bin/bash

# --- FASE 0: Instalar prerrequisitos (jq para procesar JSON) ---
# Verifica si jq está instalado y, si no, lo instala.
if ! command -v jq &> /dev/null
then
    echo "jq no está instalado. Se requiere para procesar las salidas de Terraform."
    echo "Instalando jq..."
    sudo apt-get update && sudo apt-get install -y jq
fi

echo "---"
echo "--- BIENVENIDO A LA CONFIGURACIÓN DEL PRODUCTO OPTIMON ---"
echo "---"
echo "Este script te guiará para desplegar y monitorear tu infraestructura."
echo

# --- FASE 1: Recolectar todas las credenciales del usuario ---
echo "Por favor, introduce tus credenciales de Azure (Service Principal):"
read -p 'Azure Client ID: ' AZURE_CLIENT_ID
read -sp 'Azure Client Secret: ' AZURE_CLIENT_SECRET
echo # Salto de línea después de la contraseña
read -p 'Azure Tenant ID: ' AZURE_TENANT_ID
read -p 'Azure Subscription ID: ' AZURE_SUBSCRIPTION_ID
echo
read -sp 'Crea una contraseña para la nueva Máquina Virtual: ' VM_PASSWORD
echo
echo "¡Gracias! Todas las credenciales han sido recibidas."
echo

# --- FASE 2: Crear infraestructura con Terraform ---
echo
