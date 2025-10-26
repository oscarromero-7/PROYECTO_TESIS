# 🚀 OptiMon Sistema Unificado

**Versión 3.0.0-UNIFIED** - Sistema completo de monitoreo con instalación automática

## ✨ Características Principales

### 🎯 **Todo en Uno**
- **Portal web único**: Un solo punto de acceso para toda la configuración
- **Monitoreo automático**: PC local se configura automáticamente
- **Alertas inteligentes**: Sistema unificado de notificaciones
- **Cloud integrado**: AWS y Azure con descubrimiento automático
- **SSH scanner**: Detección automática de servidores

### 🛠️ **Funcionalidades Integradas**

#### 💻 **Monitoreo Local Automático**
- ✅ Windows Exporter se instala automáticamente
- ✅ Dashboard local pre-configurado
- ✅ Alertas de CPU, RAM, Disco
- ✅ Sin configuración manual requerida

#### ☁️ **Monitoreo Cloud**
- ✅ AWS EC2 con auto-descubrimiento
- ✅ Azure VMs con detección automática
- ✅ Configuración de credenciales desde el portal
- ✅ Dashboards cloud automáticos

#### 📧 **Sistema de Alertas**
- ✅ SMTP pre-configurado (Outlook)
- ✅ Emails HTML con diseño profesional
- ✅ Alertas diferenciadas por severidad
- ✅ Configuración de destinatarios desde el portal

#### 🔐 **SSH Scanner**
- ✅ Escaneo automático de claves SSH
- ✅ Detección de servidores físicos
- ✅ Instalación automática de Node Exporter
- ✅ Sin intervención manual

## 🚀 Instalación Ultra-Rápida

### **Método 1: Windows (Recomendado)**
```batch
# 1. Descargar y extraer OptiMon-BASE-UNIFICADO
# 2. Ejecutar como administrador:
INSTALL.bat
```

### **Método 2: Python**
```bash
# 1. Asegurarse que Docker esté ejecutándose
# 2. Ejecutar:
python install.py
```

### **Requisitos**
- ✅ **Docker Desktop** (para Prometheus, Grafana, AlertManager)
- ✅ **Python 3.7+** (para el portal y servicios)
- ✅ **Windows 10/11** (para monitoreo local)

## 📱 Acceso al Sistema

Una vez instalado, accede a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **🎛️ Panel Principal** | http://localhost:5000 | No requiere |
| **📊 Grafana** | http://localhost:3000 | admin / admin |
| **📈 Prometheus** | http://localhost:9090 | No requiere |
| **🚨 AlertManager** | http://localhost:9093 | No requiere |

## 🎯 Flujo de Configuración

### **1. Instalación (Automática)**
```
INSTALL.bat → Todo se configura automáticamente
```

### **2. Acceso al Portal**
```
http://localhost:5000 → Panel de control unificado
```

### **3. Configuración Cloud (Opcional)**
```
Panel → Cloud Config → Agregar credenciales AWS/Azure
```

### **4. Configuración Email (Opcional)**
```
Panel → Email Config → Agregar destinatarios
```

### **5. ¡Listo!**
```
Todo funciona automáticamente:
✅ PC local monitoreada
✅ Alertas configuradas  
✅ Dashboards listos
✅ Emails funcionando
```

## 📊 Dashboards Incluidos

### **Local Computer Dashboard**
- CPU, RAM, Disk usage en tiempo real
- Alertas automáticas configuradas
- Métricas históricas

### **Cloud Infrastructure Dashboard**
- AWS EC2 instances
- Azure Virtual Machines  
- Alertas de disponibilidad

### **System Overview Dashboard**
- Estado general del sistema
- Servicios activos/inactivos
- Estadísticas globales

## 🔧 Configuración Avanzada

### **Agregar Servidores Físicos**
```python
# El SSH scanner detecta automáticamente servidores
# Panel → SSH Scan → Sistema completo
```

### **Configurar Alertas Personalizadas**
```yaml
# Editar: docker/prometheus/alert.rules.yml
# Reiniciar: docker-compose restart prometheus
```

### **Agregar Métricas Personalizadas**
```yaml
# Editar: docker/prometheus/prometheus.yml
# Agregar nuevos jobs o targets
```

## 📁 Estructura del Proyecto

```
OptiMon-BASE-UNIFICADO/
├── app.py                 # Portal principal unificado
├── install.py             # Instalador automático Python
├── INSTALL.bat            # Instalador Windows
├── docker-compose.yml     # Servicios Docker
├── requirements.txt       # Dependencias Python
├── .env                   # Configuración SMTP (auto-generado)
│
├── core/                  # Módulos principales
│   ├── email_service.py   # Servicio SMTP unificado
│   ├── cloud_manager.py   # Gestión cloud (AWS/Azure)
│   ├── ssh_manager.py     # SSH scanner automático
│   └── monitoring_manager.py # Gestión de monitoreo
│
├── docker/                # Configuraciones Docker
│   ├── prometheus/        # Configuración Prometheus
│   ├── grafana/          # Dashboards Grafana
│   └── alertmanager/     # Configuración AlertManager
│
├── config/               # Configuraciones del sistema
│   ├── email_recipients.json
│   ├── cloud_credentials.json
│   └── monitoring_settings.json
│
└── templates/            # Templates web
    ├── dashboard_unified.html
    └── components/
```

## 🎯 Ventajas del Sistema Unificado

### **✅ Antes vs Después**

| **Antes (Múltiples Carpetas)** | **Después (Unificado)** |
|--------------------------------|--------------------------|
| ❌ 44+ archivos duplicados | ✅ 1 proyecto base |
| ❌ Configuración manual compleja | ✅ Instalación automática |
| ❌ Múltiples servicios separados | ✅ Portal único integrado |
| ❌ SSH scanner manual | ✅ Auto-detección |
| ❌ Dashboards manuales | ✅ Creación automática |
| ❌ Emails complicados | ✅ SMTP pre-configurado |

### **🚀 Beneficios Clave**

1. **🎯 Simplicidad**: Un solo instalador, todo funciona
2. **⚡ Velocidad**: Configuración en menos de 5 minutos
3. **🔧 Mantenimiento**: Un solo proyecto para actualizar
4. **📊 Completitud**: Todas las funcionalidades integradas
5. **🎨 Consistencia**: Interfaz única y coherente

## 📋 Funcionalidades Validadas

### **✅ Monitoreo Local**
- [x] Windows Exporter auto-instalación
- [x] Dashboard local automático
- [x] Alertas CPU/RAM/Disk configuradas
- [x] Métricas en tiempo real

### **✅ Sistema de Alertas**
- [x] SMTP service funcionando
- [x] AlertManager configurado
- [x] Emails HTML profesionales
- [x] Destinatarios configurables

### **✅ Integración Cloud**
- [x] API AWS configurada
- [x] API Azure configurada  
- [x] Auto-descubrimiento VMs
- [x] Dashboards cloud automáticos

### **✅ SSH Scanner**
- [x] Detección automática claves SSH
- [x] Escaneo sistema completo
- [x] Auto-instalación Node Exporter
- [x] Configuración Prometheus automática

## 🆘 Solución de Problemas

### **Docker no inicia**
```bash
# Verificar Docker Desktop está ejecutándose
docker ps

# Si no funciona, reiniciar Docker Desktop
```

### **Puerto 5000 ocupado**
```bash
# Encontrar proceso usando puerto 5000
netstat -ano | findstr :5000

# Terminar proceso y reiniciar
```

### **Emails no llegan**
```bash
# Verificar servicio email
curl http://localhost:5555/health

# Revisar configuración en .env
```

### **Windows Exporter no inicia**
```bash
# El sistema lo instala automáticamente
# Acceder a Panel → Local Setup → Auto Configure
```

## 📞 Soporte

Para soporte técnico:
- 📧 Email: Proyecto20251985@hotmail.com
- 🎯 Panel: http://localhost:5000/help
- 📊 Status: http://localhost:5000/api/health

---

## 🏆 Resultado Final

**OptiMon Sistema Unificado** elimina la complejidad de múltiples carpetas y archivos duplicados, proporcionando:

✅ **Un solo proyecto base**  
✅ **Instalación automática completa**  
✅ **Todas las funcionalidades integradas**  
✅ **Monitoreo local automático**  
✅ **Alertas y emails funcionando**  
✅ **Cloud y SSH scanner incluidos**  
✅ **Mantenimiento simplificado**  

**🎯 Objetivo cumplido: Un producto de calidad que funciona desde el primer momento sin intervención del usuario.**