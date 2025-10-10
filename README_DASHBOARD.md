# 🌐 OptiMon Web Dashboard

## Interfaz Web Completa para Gestión de Monitoreo

### 🚀 ¿Qué es el OptiMon Dashboard?

El **OptiMon Dashboard** es una interfaz web integral que te permite gestionar completamente tu sistema de monitoreo OptiMon desde el navegador. No necesitas comandos de terminal ni configuraciones manuales complejas.

### ✨ Características Principales

#### 📊 **Dashboard Principal**
- **Vista general del sistema** con tarjetas de estado en tiempo real
- **Monitoreo de servicios**: Prometheus, Grafana, AlertManager, SMTP
- **Métricas actuales**: CPU, Memoria, Disco en tiempo real
- **Estado de configuración** para cada componente

#### 📧 **Gestión de Emails**
- **Agregar/eliminar emails** de destino para alertas
- **Email principal** para notificaciones críticas
- **Activar/desactivar** destinatarios individualmente
- **Probar envío de emails** para verificar funcionamiento
- **Estadísticas** de emails configurados

#### 🛠️ **Configuración SMTP**
- **Configuración automática** para Gmail, Outlook, Yahoo
- **Configuración personalizada** para otros proveedores
- **Prueba de conexión** para verificar credenciales
- **Control del servicio**: Iniciar, detener, reiniciar
- **Logs en tiempo real** del servicio SMTP
- **Guías paso a paso** para configurar cada proveedor

#### ☁️ **Proveedores Cloud**
- **AWS**: Configuración con Access Keys y servicios a monitorear
- **Azure**: Configuración con Service Principal y suscripción
- **Google Cloud**: Configuración con Service Account JSON
- **Servidor Local**: Monitoreo del sistema actual con Node Exporter
- **Pruebas de conexión** para cada proveedor
- **Estado en tiempo real** de cada configuración

#### 📈 **Configuración de Monitoreo**
- **Umbrales personalizables** para CPU, Memoria, Disco
- **Intervalos de evaluación** y timeouts configurables
- **Reglas de alertas** con severidad y condiciones
- **Configuración de dashboard** (actualización, retención de datos)
- **Control de servicios** de monitoreo
- **Métricas en tiempo real** con barras de progreso
- **Gestión de alertas activas** con opciones de silenciar

#### ❓ **Ayuda y Documentación**
- **Guía completa** de configuración paso a paso
- **Instrucciones específicas** para cada proveedor cloud
- **Solución de problemas** con casos comunes
- **API Reference** para integraciones avanzadas
- **Navegación interactiva** por secciones

### 🏃‍♂️ Inicio Rápido

#### 1. **Ejecutar el Dashboard**
```bash
# Opción 1: Usar el script automático (recomendado)
INICIAR_OPTIMON_DASHBOARD.bat

# Opción 2: Manual
cd 2-INICIAR-MONITOREO
python optimon_dashboard.py
```

#### 2. **Acceder a la Interfaz**
- Abre tu navegador en: **http://localhost:8080**
- Se abrirá automáticamente al usar el script .bat

#### 3. **Configuración Inicial**

**Paso 1: Configurar SMTP**
1. Ve a la sección "SMTP" en el menú lateral
2. Selecciona tu proveedor (Gmail recomendado)
3. Ingresa tus credenciales de email
4. Haz clic en "Probar Conexión"

**Paso 2: Agregar Emails**
1. Ve a la sección "Emails"
2. Agrega tu email principal
3. Agrega emails adicionales si necesitas
4. Prueba el envío con "Probar Todos"

**Paso 3: Configurar Monitoreo Local**
1. Ve a la sección "Cloud" → pestaña "Servidor Local"
2. Instala Node Exporter si no está instalado
3. Configura las métricas que quieres monitorear

**Paso 4: Ajustar Alertas**
1. Ve a la sección "Monitoreo"
2. Configura umbrales para CPU, Memoria, Disco
3. Ajusta intervalos según tus necesidades
4. Inicia el sistema de monitoreo

### 🎯 Funcionalidades Avanzadas

#### **API REST Integrada**
El dashboard incluye una API REST completa:
- `/api/status` - Estado general del sistema
- `/api/emails` - Gestión de emails
- `/api/smtp` - Configuración SMTP
- `/api/cloud/{provider}` - Configuración de proveedores
- `/api/monitoring/*` - Control de monitoreo

#### **Configuración sin Base de Datos**
Todo se almacena en archivos JSON simples:
- `email_config.json` - Configuración de emails
- `smtp_config.json` - Configuración SMTP
- `cloud_config.json` - Configuración de proveedores
- `monitoring_config.json` - Configuración de monitoreo

#### **Responsive Design**
- **Diseño responsivo** con Bootstrap 5
- **Compatible con móviles** y tablets
- **Navegación lateral** intuitiva
- **Indicadores de estado** en tiempo real

### 🔧 Configuraciones Específicas

#### **Gmail SMTP**
1. Habilita verificación en 2 pasos
2. Genera contraseña de aplicación
3. Usa: smtp.gmail.com:587 (TLS)

#### **AWS Monitoring**
1. Crea usuario IAM programático
2. Asigna políticas CloudWatch y EC2 ReadOnly
3. Ingresa Access Key y Secret Key

#### **Azure Monitoring**
1. Registra aplicación en Azure AD
2. Crea client secret
3. Asigna permisos de Reader en suscripción

#### **Google Cloud**
1. Crea Service Account
2. Asigna rol Monitoring Viewer
3. Descarga JSON de credenciales

### 🚨 Sistema de Alertas

#### **Tipos de Alertas**
- **🔴 Críticas**: CPU > 90%, Memoria > 95%, Disco > 95%
- **🟡 Advertencias**: CPU > 80%, Memoria > 85%, Disco > 90%
- **🔵 Informativas**: Cambios de estado, inicio/parada de servicios

#### **Gestión de Alertas**
- **Silenciar individual**: Pausa una alerta específica
- **Silenciar todas**: Pausa todas las alertas activas
- **Reenvío automático**: Reenvía alertas no resueltas
- **Escalación**: Aumenta severidad con el tiempo

### 📱 Características de la Interfaz

#### **Dashboard Principal**
- **Tarjetas de estado** para cada servicio
- **Métricas en tiempo real** con gráficos
- **Acciones rápidas** para funciones comunes
- **Indicadores visuales** de estado (colores)

#### **Navegación Intuitiva**
- **Menú lateral** con iconos descriptivos
- **Breadcrumbs** para ubicación actual
- **Búsqueda rápida** en configuraciones
- **Atajos de teclado** para acciones comunes

#### **Feedback Visual**
- **Notificaciones toast** para acciones
- **Barras de progreso** para cargas
- **Indicadores de conexión** en tiempo real
- **Estados de color** (verde/amarillo/rojo)

### 🔒 Seguridad

#### **Credenciales**
- **No se almacenan passwords** en texto plano
- **Configuración local** únicamente
- **Sin transmisión externa** de credenciales
- **Acceso solo desde localhost** por defecto

#### **Validación**
- **Validación de formularios** en frontend
- **Sanitización de inputs** en backend
- **Verificación de conexiones** antes de guardar
- **Logs de actividad** para auditoría

### 🛠️ Solución de Problemas

#### **El dashboard no inicia**
1. Verifica que Python esté instalado
2. Instala dependencias: `pip install -r requirements_smtp.txt`
3. Verifica que el puerto 8080 esté libre

#### **No llegan emails**
1. Verifica configuración SMTP en la sección SMTP
2. Usa "Probar Conexión" para validar credenciales
3. Para Gmail, usa contraseña de aplicación
4. Revisa carpeta de spam

#### **Servicios no inician**
1. Verifica puertos libres (9090, 3000, 9093, 9100)
2. Instala Node Exporter desde la sección Cloud
3. Reinicia servicios desde Monitoreo

### 📞 Soporte

Para soporte adicional:
1. **Sección Ayuda** en el dashboard con documentación completa
2. **Logs del sistema** en cada sección para diagnóstico
3. **API Reference** para integraciones avanzadas
4. **Guías paso a paso** para cada configuración

---

**🎉 ¡Disfruta de OptiMon Dashboard y ten control total de tu infraestructura!**