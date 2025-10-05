
# Reporte de Infraestructura OptiMon
**Versión:** 26  
**Fecha:** 2025-10-05 18:39:16

## Resumen de Infraestructura Detectada


### Servidor Local
- **CPU Cores:** 12
- **Memoria:** 15.71 GB
- **Disco:** 457.61 GB
- **Contenedores Docker:** 3


### Infraestructura AWS
- **Instancias EC2:** 2
- **VPCs:** 3
- **Security Groups:** 0


## Archivos Generados
- `terraform/` - Código Terraform para replicar la infraestructura
- `ansible/` - Playbooks para configuración automatizada
- `scan_results.json` - Datos completos del escaneo

## Cómo usar el código generado
1. `cd 3-CODIGO-GENERADO\version_26/terraform`
2. `terraform init`
3. `terraform plan`
4. `terraform apply`

## Monitoreo
Los recursos incluyen configuración automática de Node Exporter para integración con OptiMon.
