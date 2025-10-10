# 🚀 OptiMon - Sistema de Monitoreo Automatizado

## 📋 Descripción
OptiMon es una solución completa de monitoreo que combina Prometheus, Grafana, AlertManager y un dashboard web personalizado para monitorear infraestructura local y en la nube.

## ⚡ Inicio Rápido (Totalmente Automático)

### 🎯 Para Windows
1. **Doble clic en `start_optimon_auto.bat`**
2. ¡Eso es todo! El sistema se iniciará automáticamente

### 🐍 Para cualquier SO (Python)
```bash
python optimon_auto_starter.py
```

## 🌐 Acceso a los Servicios

Una vez iniciado, acceder a:

- **📊 Panel de Control OptiMon**: http://localhost:8080
- **📈 Grafana**: http://localhost:3000 (admin/admin)
- **🔍 Prometheus**: http://localhost:9090
- **⚠️ AlertManager**: http://localhost:9093

## 🛑 Detener el Sistema

### 🎯 Para Windows
```batch
stop_optimon.bat
```

### 🐍 Para cualquier SO (Python)
```bash
python optimon_auto_starter.py --stop
```

## 📁 Estructura del Proyecto

```
2-INICIAR-MONITOREO/
├── start_optimon_auto.bat       # ✨ Inicio automático (Windows)
├── stop_optimon.bat             # 🛑 Parada automática (Windows)
├── optimon_auto_starter.py      # 🤖 Gestión automática inteligente
├── optimon_dashboard.py         # 🌐 Dashboard web principal
├── optimon_smtp_service.py      # 📧 Servicio de emails
├── docker-compose.yml           # 🐳 Configuración Docker
├── config/                      # ⚙️ Configuraciones
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
└── templates/                   # 🎨 Plantillas web
```

## 🔧 Características Principales

### 🎯 Inicio Automático Inteligente
- ✅ Verificación de requisitos
- ✅ Inicio secuencial de servicios
- ✅ Verificación de salud de cada componente
- ✅ Manejo de errores y timeouts
- ✅ Apertura automática del navegador

### 📊 Dashboard Web Completo
- ✅ Configuración de emails y alertas
- ✅ Monitoreo de métricas en tiempo real
- ✅ Instalación automática de Node Exporter
- ✅ Gestión de configuraciones de nube
- ✅ Estado de todos los servicios

### 📧 Sistema de Alertas
- ✅ Envío automático de emails
- ✅ Configuración múltiples destinatarios
- ✅ Alertas personalizables
- ✅ Integración con Gmail/SMTP

### 🌐 Monitoreo Multi-Plataforma
- ✅ Servidores locales (Windows/Linux)
- ✅ AWS EC2
- ✅ Azure Virtual Machines
- ✅ Servidores físicos

## 🧪 Verificación del Sistema

### Verificación automática:
```bash
python test_complete_system.py
```

### Verificación manual:
```batch
check_optimon_status.bat
```

## 📝 Configuración

### 📧 Configurar Emails
1. Acceder a http://localhost:8080/emails
2. Configurar servidor SMTP (Gmail recomendado)
3. Agregar destinatarios
4. Probar envío

### ☁️ Configurar Monitoreo en Nube
1. Acceder a http://localhost:8080/cloud
2. Seleccionar proveedor (AWS/Azure)
3. Ingresar credenciales
4. Configurar instancias a monitorear

### 🖥️ Configurar Monitoreo Local
1. Acceder a http://localhost:8080/monitoring
2. Hacer clic en "Instalar Node Exporter"
3. Configurar umbrales de alertas
4. Activar monitoreo

## 🚨 Solución de Problemas

### ❌ Error: "Docker no disponible"
```bash
# Instalar Docker Desktop para Windows
# O Docker Engine para Linux
```

### ❌ Error: "Puerto ocupado"
```bash
# Verificar que no hay otros servicios ejecutándose
netstat -an | findstr :8080
```

### ❌ Error: "Python no encontrado"
```bash
# Instalar Python 3.8+ desde python.org
python --version
```

### 🔧 Reinicio Completo
```batch
stop_optimon.bat
start_optimon_auto.bat
```

## 📊 Monitoreo Incluido

### Métricas de Sistema
- 🖥️ CPU (uso, carga, procesos)
- 💾 Memoria (uso, disponible, swap)
- 💽 Disco (uso, I/O, espacio libre)
- 🌐 Red (tráfico, conexiones, latencia)

### Métricas de Aplicación
- 🔥 Servicios activos
- 📊 Logs de aplicación
- ⚡ Tiempo de respuesta
- 🔍 Disponibilidad de endpoints

### Alertas Configuradas
- ⚠️ CPU > 80%
- ⚠️ Memoria > 85%
- ⚠️ Disco > 90%
- ⚠️ Servicio caído
- ⚠️ Red sin conectividad

## 🎨 Personalización

### Dashboard Grafana
- Importar dashboards desde `grafana/dashboards/`
- Personalizar métricas y visualizaciones
- Configurar alertas adicionales

### Configuración Prometheus
- Editar `config/prometheus/prometheus.yml`
- Agregar nuevos targets
- Configurar reglas de alertas

## 🔐 Seguridad

### Configuración Recomendada
- ✅ Cambiar contraseñas por defecto
- ✅ Configurar HTTPS en producción
- ✅ Restringir acceso por IP
- ✅ Usar autenticación robusta

## 📞 Soporte

### Logs del Sistema
```bash
# Ver logs de Docker
docker-compose logs

# Ver estado detallado
cat optimon_status.json

# Ver reporte de pruebas
cat test_report.json
```

### Contacto
- 📧 Configurar emails para recibir alertas
- 📊 Usar el dashboard para monitoreo visual
- 🔍 Consultar logs para debugging

---

## 🎉 ¡Listo para Usar!

OptiMon está diseñado para ser **plug-and-play**. Simplemente ejecuta `start_optimon_auto.bat` y tendrás un sistema completo de monitoreo funcionando en minutos.

**¡Disfruta monitoreando tu infraestructura! 🚀**