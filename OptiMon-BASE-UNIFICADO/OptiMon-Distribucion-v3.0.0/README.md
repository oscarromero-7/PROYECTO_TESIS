# 🚀 OptiMon - Sistema de Monitoreo Automático

## ⚡ CONFIGURACIÓN AUTOMÁTICA COMPLETA

### 🎯 Opción 1: Super Simple (Recomendado)
```bash
# Ejecutar desde Windows
SETUP_AUTOMATICO_COMPLETO.bat
```

### 🎯 Opción 2: PowerShell
```powershell
.\setup_automatico.ps1
```

### 🎯 Opción 3: Python
```bash
python setup_automatico_completo.py
```

## ✨ ¿Qué hace la configuración automática?

1. **🛑 Limpia servicios existentes**
   - Detiene procesos Python anteriores
   - Elimina Windows Exporter previo
   - Detiene contenedores Docker

2. **🐳 Configura Docker**
   - Inicia Prometheus (puerto 9090)
   - Inicia Grafana (puerto 3000)
   - Inicia AlertManager (puerto 9093)

3. **🌐 Configura Portal OptiMon**
   - Inicia servidor Flask en puerto 5000
   - Ejecuta en segundo plano automáticamente

4. **📊 Configura Windows Exporter**
   - Descarga e instala automáticamente
   - Configura en puerto 9182
   - Integra con Prometheus

5. **✅ Verifica sistema completo**
   - Comprueba todos los servicios
   - Valida conectividad
   - Confirma recolección de métricas

## 🎉 Resultado Final

Después de la configuración automática tendrás:

- ✅ **Portal OptiMon**: http://localhost:5000
- ✅ **Grafana**: http://localhost:3000 (admin/admin)
- ✅ **Prometheus**: http://localhost:9090
- ✅ **Windows Exporter**: http://localhost:9182/metrics
- ✅ **AlertManager**: http://localhost:9093

## 🔥 Características del Sistema Automático

### 🎪 Configuración Zero-Touch
- **Sin intervención manual requerida**
- **Detección automática de puertos**
- **Instalación automática de dependencias**
- **Configuración automática de targets**

### 🛡️ Manejo Robusto de Errores
- **Limpieza automática de procesos**
- **Reintentos automáticos**
- **Verificación de estado en tiempo real**
- **Rollback en caso de errores**

### 📱 Interfaz de Usuario Mejorada
- **Feedback en tiempo real**
- **Códigos de color informativos**
- **Progreso paso a paso**
- **Resumen final completo**

## 🚨 Solución de Problemas

### ❓ Si algo no funciona:

1. **Ejecutar como Administrador**
   ```bash
   # Hacer clic derecho en SETUP_AUTOMATICO_COMPLETO.bat
   # Seleccionar "Ejecutar como administrador"
   ```

2. **Verificar Docker**
   ```bash
   docker --version
   docker compose --version
   ```

3. **Verificar Python**
   ```bash
   python --version
   pip --version
   ```

4. **Verificar puertos libres**
   ```bash
   netstat -an | findstr ":5000"
   netstat -an | findstr ":9090"
   netstat -an | findstr ":3000"
   netstat -an | findstr ":9182"
   ```

## 🎯 Características Avanzadas

### 🔄 Auto-Restart
El sistema se reinicia automáticamente si detecta fallos.

### 📈 Métricas Completas
- CPU, Memoria, Disco, Red
- Servicios de Windows
- Métricas de aplicación
- Alertas personalizadas

### 🎨 Dashboards Prediseñados
- Dashboard de sistema Windows
- Métricas de aplicación
- Alertas en tiempo real
- Visualizaciones avanzadas

## 💡 Tips para Desarrollo

- **Logs en tiempo real**: Todos los componentes registran actividad
- **API completa**: Endpoints para integración
- **Configuración flexible**: Fácil personalización
- **Escalabilidad**: Preparado para múltiples hosts

---

## 🚀 ¡Listo para Usar!

Una vez ejecutado el setup automático, tu sistema de monitoreo estará **100% operativo** sin configuración adicional.

**¡Disfruta monitoreando! 📊✨**