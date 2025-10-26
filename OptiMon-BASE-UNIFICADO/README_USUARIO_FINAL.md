# 🚀 OptiMon - Sistema Unificado de Monitoreo v3.0.0

## 📋 Descripción
OptiMon es un sistema completo de monitoreo que combina:
- **Monitoreo local** de tu computadora Windows
- **Generación automática** de infraestructura en Azure
- **Dashboards avanzados** con Grafana
- **Sistema de alertas** con Prometheus y AlertManager

## 🎯 Instalación Rápida (Usuario Final)

### Prerrequisitos
- Windows 10/11
- Docker Desktop instalado
- Python 3.8 o superior
- Privilegios de administrador

### Instalación Automática

**Opción 1: PowerShell (Recomendado)**
```powershell
# Ejecutar PowerShell como Administrador
.\INSTALAR_OPTIMON.ps1
```

**Opción 2: Batch**
```cmd
# Ejecutar como Administrador
INSTALAR_OPTIMON.bat
```

## 🌐 Accesos del Sistema

Una vez instalado, tendrás acceso a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| 🌐 Portal OptiMon | http://localhost:5000 | Sin login |
| 📊 Grafana | http://localhost:3000 | admin/admin |
| 🔍 Prometheus | http://localhost:9090 | Sin login |
| 🚨 AlertManager | http://localhost:9093 | Sin login |

## 🚀 Funcionalidades Principales

### 1. 🖥️ Monitoreo Local
- **CPU, Memoria, Disco** en tiempo real
- **Procesos del sistema** monitoreados
- **Métricas históricas** almacenadas
- **Alertas automáticas** por umbrales

### 2. ☁️ Integración Azure
- **Configuración de credenciales** desde interfaz web
- **Generación automática** de infraestructura
- **Despliegue de VMs** con monitoreo preconfigurado
- **Código Terraform** generado automáticamente

### 3. 📊 Dashboards Avanzados
- **Monitoreo en tiempo real** de la computadora local
- **Visualizaciones interactivas** con Grafana
- **Métricas personalizables** según necesidades
- **Exportación de reportes**

### 4. 🔔 Sistema de Alertas
- **Alertas por email** configurables
- **Umbrales personalizables** por métrica
- **Notificaciones inmediatas** por anomalías
- **Historial de alertas**

## 🎯 Guía de Uso Rápido

### Paso 1: Configurar Azure (Opcional)
1. Accede al portal: http://localhost:5000
2. Ve a la sección "Configuración Azure"
3. Ingresa tus credenciales de Azure
4. Guarda la configuración

### Paso 2: Monitoreo Local
1. El monitoreo local inicia automáticamente
2. Accede a Grafana: http://localhost:3000
3. Explora el dashboard "Real Computer Monitoring"
4. Ve métricas en tiempo real de tu PC

### Paso 3: Generar Infraestructura (Opcional)
1. En el portal, ve a "Infraestructura"
2. Selecciona la configuración deseada
3. Genera código Terraform automáticamente
4. Despliega en Azure con un clic

## 🔧 Configuración Avanzada

### Variables de Entorno
Crea un archivo `.env` para configuraciones personalizadas:
```env
# Azure Configuration
AZURE_SUBSCRIPTION_ID=tu-subscription-id
AZURE_CLIENT_ID=tu-client-id
AZURE_CLIENT_SECRET=tu-client-secret
AZURE_TENANT_ID=tu-tenant-id

# Email Alerts
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-password-app
```

### Personalización de Alertas
Edita `config/alertmanager/alertmanager.yml` para configurar:
- Receptores de alertas
- Canales de notificación
- Umbrales personalizados
- Horarios de silencio

## 🛠️ Solución de Problemas

### Docker no responde
```powershell
# Reiniciar Docker Desktop
Restart-Service docker
docker compose down
docker compose up -d
```

### Puerto ocupado
```powershell
# Verificar puertos en uso
netstat -ano | findstr ":5000"
netstat -ano | findstr ":3000"

# Terminar procesos si es necesario
taskkill /PID [PID_NUMBER] /F
```

### Servicios no inician
```powershell
# Verificar logs
docker compose logs prometheus
docker compose logs grafana
docker compose logs alertmanager
```

## 📁 Estructura del Proyecto

```
OptiMon-BASE-UNIFICADO/
├── app.py                     # Portal web principal
├── docker-compose.yml         # Servicios Docker
├── requirements.txt           # Dependencias Python
├── INSTALAR_OPTIMON.ps1      # Instalador PowerShell
├── INSTALAR_OPTIMON.bat      # Instalador Batch
├── config/                   # Configuraciones
│   ├── prometheus/           # Config Prometheus
│   ├── grafana/             # Dashboards y datasources
│   └── alertmanager/        # Config alertas
├── core/                    # Módulos del sistema
├── templates/               # Templates web
└── README.md               # Esta documentación
```

## 🆘 Soporte y Contacto

- **Documentación completa**: Incluida en el portal web
- **Logs del sistema**: Disponibles en la interfaz web
- **Diagnósticos**: Herramientas integradas de troubleshooting

## 📜 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

---

**🎉 ¡Disfruta monitoreando con OptiMon!** 🎉