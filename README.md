# OptiMon - Sistema de Monitoreo de Infraestructura

Sistema completo de monitoreo para infraestructura en la nube (AWS/Azure) y servidores físicos usando Prometheus, Grafana y Node Exporter.

## 🚀 Características

- **Monitoreo Multi-Plataforma**: AWS, Azure y servidores físicos
- **Instalación Automática**: Despliega Node Exporter automáticamente
- **Dashboards Preconfiguratos**: Grafana con métricas listas para usar
- **Alertas Inteligentes**: Notificaciones automáticas de problemas
- **Fácil Configuración**: Solo necesitas credenciales de nube

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Python 3.8+ (para scripts de configuración)
- Credenciales de AWS o Azure (según corresponda)
- Conectividad SSH a servidores físicos

## 🛠️ Instalación Súper Fácil

### 1. Descomprimir y navegar
```bash
unzip optimon-monitoring.zip
cd optimon-monitoring
```

### 2. Configurar credenciales (SOLO esto)
```bash
# Copiar plantilla simplificada
cp config/credentials.simple.yml config/credentials.simple.yml

# Editar y completar SOLO las credenciales de tu proveedor:
# - Para AWS: access_key_id, secret_access_key, region
# - Para Azure: subscription_id, tenant_id, client_id, client_secret
```

### 3. Ejecutar TODO automáticamente
```bash
# Linux/Mac
./deploy.sh

# Windows (PowerShell)
.\deploy.ps1

# Windows (CMD/Batch - compatible con cualquier Windows)
deploy.bat
```

**¡ESO ES TODO!** El sistema automáticamente:
- 🔍 Detecta todas tus VMs/instancias 
- 🔑 Encuentra y configura las claves SSH correctas automáticamente
- 📦 Instala Node Exporter en cada servidor
- 🌐 Abre puertos de firewall automáticamente (Azure NSG)
- ⚙️ Configura Prometheus y Grafana
- 📊 Crea dashboards personalizados con métricas importantes
- 🚨 Configura alertas automáticas
- 📡 Inicia el monitoreo completo

### 4. Acceder a los servicios
- **Grafana**: http://localhost:3000 (admin/admin)
  - 📊 **Dashboard "Infrastructure Overview"**: Métricas generales del sistema
  - 🔵 **Dashboard "Azure VMs Monitoring"**: Monitoreo específico de Azure
- **Prometheus**: http://localhost:9090 - Métricas y consultas
- **AlertManager**: http://localhost:9093 - Gestión de alertas

### 5. Dashboards preconfigurados
El sistema crea automáticamente dashboards con las métricas más importantes:
- **CPU Usage**: Uso de procesador en tiempo real
- **Memory Usage**: Consumo de memoria RAM
- **Disk Usage**: Espacio en disco utilizado
- **Network I/O**: Tráfico de red (entrada/salida)
- **System Load**: Carga del sistema
- **VM Status**: Estado de conexión de las VMs

## 📊 Uso

### Comandos disponibles:
```bash
# Linux/Mac:
./make.sh start       # Iniciar todo el stack
./make.sh stop        # Parar el stack
./make.sh restart     # Reiniciar
./make.sh status      # Ver estado
./add_server.sh       # Agregar nuevo servidor

# Windows PowerShell:
.\make.ps1 start
.\make.ps1 stop
.\make.ps1 restart
.\make.ps1 status
.\add_server.ps1

# Windows CMD/Batch (compatible con cualquier Windows):
make.bat start
make.bat stop
make.bat restart
make.bat status
add_server.bat
```

### Monitoreo de Nube (AWS/Azure)
1. El sistema detecta automáticamente las VMs en tu cuenta
2. Instala Node Exporter en cada VM
3. Configura Prometheus para recopilar métricas

### Monitoreo de Servidores Físicos
1. Agrega servidores manualmente con `./add-server.sh`
2. Proporciona IP, usuario y credenciales SSH
3. El sistema instala y configura automáticamente

## 🔧 Configuración Avanzada

### Personalizar Dashboards
- Edita archivos en `grafana/dashboards/`
- Reinicia Grafana: `docker-compose restart grafana`

### Añadir Alertas
- Modifica `prometheus/alert.rules.yml`
- Configura notificaciones en `alertmanager/alertmanager.yml`

## 📁 Estructura del Proyecto

```
optimon-monitoring/
├── docker-compose.yml          # Configuración principal
├── deploy.sh                   # Script de despliegue
├── config/                     # Configuraciones
│   ├── credentials.example.yml
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
├── scripts/                    # Scripts de automatización
│   ├── setup_cloud.py
│   ├── install_node_exporter.py
│   └── server_manager.py
└── docs/                       # Documentación adicional
```

## 🆘 Solución de Problemas

### Problemas comunes
1. **Docker no funciona**: Verificar que Docker esté iniciado
2. **No se conecta a VMs**: Revisar credenciales y permisos
3. **Grafana no muestra datos**: Verificar configuración de Prometheus

### Logs
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f prometheus
```

## 🔒 Seguridad

- Las credenciales se almacenan localmente
- Comunicación SSH encriptada
- Tokens temporales para APIs de nube
- Configuración de firewall recomendada

## 📈 Métricas Disponibles

### Métricas del Sistema
- CPU, Memoria, Disco
- Red, Procesos
- Temperatura, Hardware

### Métricas de Nube
- Estados de VMs
- Costos estimados
- Alertas de servicio

### Alertas Preconfiguratas
- CPU > 80%
- Memoria > 90%
- Disco > 85%
- Servicio no disponible

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature
3. Commit cambios
4. Push a la rama
5. Abrir Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE

## 📞 Soporte

- Email: support@optimon.com
- GitHub Issues: [Reportar problema](https://github.com/oscarromero-7/PROYECTO_TESIS/issues)
- Documentación: [Wiki del proyecto](https://github.com/oscarromero-7/PROYECTO_TESIS/wiki)