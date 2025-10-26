# OptiMon Sistema Unificado v3.0.0

🚀 **Sistema completo de monitoreo con configuración automática**

## 📋 Características Principales

✅ **Monitoreo Local Automático**
- Windows Exporter auto-instalado y configurado
- Métricas en tiempo real (CPU, RAM, Disco)
- Dashboard automático en Grafana

✅ **Sistema de Alertas Integrado**
- Servicio SMTP configurado automáticamente
- Integración completa con AlertManager
- Plantillas HTML para emails de alertas

✅ **Portal Web Unificado**
- Dashboard único con todas las funcionalidades
- Configuración automática desde la web
- API REST completa

✅ **Integración Cloud**
- Auto-descubrimiento AWS/Azure
- Credenciales seguras
- Dashboards automáticos por servicio

✅ **Instalación Automática**
- Un comando instala todo el sistema
- Verificación de dependencias
- Configuración automática de servicios

## 🔧 Diferencias vs Versiones Anteriores

### ❌ Problema Anterior:
- **44+ copias** de `optimon_dashboard.py`
- **12+ copias** de `email_service.py`
- Múltiples carpetas test_ con funcionalidad duplicada
- Configuración manual compleja
- Servicios dispersos y desconectados

### ✅ Solución Unificada:
- **1 solo proyecto** con toda la funcionalidad
- **1 instalador** que configura todo automáticamente
- **1 portal web** para gestionar todo
- **Configuración automática** sin intervención manual
- **Integración completa** entre todos los servicios

## ⚡ Instalación Rápida

### Windows:
```bash
# 1. Doble clic en INSTALL.bat
# o desde PowerShell:
.\INSTALL.bat

# ¡Listo! Todo configurado automáticamente
```

### Linux/Mac:
```bash
# 1. Ejecutar instalador
python3 install_v2.py

# ¡Listo! Todo configurado automáticamente
```

## 📊 Accesos del Sistema

Una vez instalado, tendrás acceso a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Portal OptiMon** | http://localhost:5000 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **AlertManager** | http://localhost:9093 | - |
| **Windows Exporter** | http://localhost:9182/metrics | - |
| **Email Service** | http://localhost:5555/health | - |

## 🎯 Funcionalidades Automáticas

### 1. Monitoreo Local
```python
# El portal detecta automáticamente tu PC y configura:
- Windows Exporter (puerto 9182)
- Métricas de CPU, RAM, Disco, Red
- Dashboard automático en Grafana
- Alertas configuradas
```

### 2. Sistema de Emails
```python
# SMTP service integrado:
- Configuración automática con Outlook/Gmail
- Plantillas HTML para alertas
- Integración con AlertManager via webhook
- Health checks automáticos
```

### 3. Cloud Integration
```python
# Auto-descubrimiento cloud:
- AWS EC2 instances via boto3
- Azure VMs via Azure SDK
- Dashboards automáticos por servicio
- Credenciales seguras encriptadas
```

## 📁 Estructura del Proyecto

```
OptiMon-BASE-UNIFICADO/
├── app.py                    # Portal web principal (700+ líneas)
├── install_v2.py            # Instalador automático
├── INSTALL.bat              # Instalador Windows
├── requirements.txt         # Dependencias Python
├── docker-compose.yml       # Stack completo Docker
│
├── core/
│   └── email_service.py     # Servicio SMTP unificado (500+ líneas)
│
├── docker/
│   ├── prometheus/
│   │   ├── prometheus.yml   # Config unificada Prometheus
│   │   └── alert.rules.yml  # Reglas de alertas
│   ├── grafana/
│   │   └── provisioning/    # Dashboards automáticos
│   └── alertmanager/
│       └── alertmanager.yml # Config AlertManager
│
├── templates/
│   └── dashboard_unified.html # Dashboard web unificado
│
└── config/                  # Configuraciones automáticas
    ├── clouds.json
    ├── emails.json
    └── monitoring.json
```

## 🔍 Monitoreo en Tiempo Real

El portal web muestra métricas en tiempo real:

- **CPU Usage**: Actualizado cada 5 segundos
- **Memory Usage**: Utilización de RAM
- **Disk Usage**: Espacio en disco
- **Service Status**: Estado de todos los servicios
- **Alert Status**: Alertas activas y configuración

## 📧 Sistema de Alertas

### Configuración Automática:
```yaml
# El sistema configura automáticamente:
- SMTP server (Outlook/Gmail/Custom)
- Destinatarios de alertas
- Plantillas HTML profesionales
- Webhook AlertManager → Email Service
- Health checks automáticos
```

### Alertas Disponibles:
- CPU alta (>80%)
- Memoria alta (>90%)
- Disco lleno (>85%)
- Servicios caídos
- Métricas cloud personalizadas

## 🔧 Configuración Avanzada

### Agregar Credenciales Cloud:
```python
# Desde el portal web:
1. Ir a "Cloud Integration"
2. Seleccionar AWS/Azure
3. Ingresar credenciales
4. ¡Auto-descubrimiento activado!
```

### Configurar Emails:
```python
# Desde el portal web:
1. Ir a "Email Configuration"
2. Configurar SMTP (auto-detect para Outlook/Gmail)
3. Agregar destinatarios
4. ¡Alertas por email activadas!
```

## 🚀 Ventajas del Sistema Unificado

### ✅ Para Usuarios Finales:
- **Instalación de 1 clic**: No configuración manual
- **Portal único**: Todo desde una interfaz
- **Configuración automática**: Sin conocimientos técnicos
- **Alertas funcionando**: Email automático desde el inicio

### ✅ Para Desarrolladores:
- **Código unificado**: No más duplicaciones
- **Mantenimiento simple**: Un solo proyecto
- **Escalabilidad**: Arquitectura modular
- **Documentación clara**: APIs bien definidas

### ✅ Para Administradores:
- **Despliegue simple**: Docker compose up
- **Monitoreo completo**: Local + Cloud + Alertas
- **Configuración centralizada**: Un solo lugar
- **Logs unificados**: Fácil troubleshooting

## 📋 Comandos Útiles

```bash
# Iniciar sistema completo
python install_v2.py

# Solo servicios Docker
docker compose up -d

# Ver logs de servicios
docker compose logs -f

# Detener sistema
docker compose down

# Reiniciar solo el portal
python app.py

# Ver estado de servicios
curl http://localhost:5000/api/health
```

## 🔄 Actualizaciones

Para actualizar el sistema:
```bash
# 1. Detener servicios
docker compose down

# 2. Actualizar código
git pull

# 3. Reinstalar
python install_v2.py
```

## 🐛 Troubleshooting

### Portal no inicia:
```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar puerto libre
netstat -an | findstr :5000
```

### Docker no funciona:
```bash
# Verificar Docker Desktop ejecutándose
docker --version
docker compose version

# Limpiar contenedores
docker system prune -a
```

### Windows Exporter no funciona:
```bash
# Verificar puerto
netstat -an | findstr :9182

# Reinstalar manualmente
# Ir a: https://github.com/prometheus-community/windows_exporter/releases
```

## 📞 Soporte

- **API Health**: http://localhost:5000/api/health
- **Portal Web**: http://localhost:5000
- **Logs Docker**: `docker compose logs -f`
- **Logs Python**: Revisa consola donde ejecutas `python app.py`

---

## 🎉 ¡Disfruta de OptiMon Sistema Unificado!

**Configuración de 1 minuto, monitoreo profesional de por vida** 🚀