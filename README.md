# OptiMon - Sistema de Monitoreo Unificado

**Versión:** 3.1.0-COST-OPTIMIZER  
**Estado:** ✅ 100% Funcional y Probado  
**Última actualización:** 15 de Diciembre de 2025

---

## 🚀 INICIO INMEDIATO

```bash
cd OptiMon-BASE-UNIFICADO
docker-compose up -d
python app.py
```

O usa el instalador automático:
```bash
cd OptiMon-BASE-UNIFICADO
INSTALL.bat
```

## 📊 Accesos Automáticos
- **Portal**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## 📁 Contenido del Proyecto

### ⭐ OptiMon-BASE-UNIFICADO
Sistema completo y autosuficiente que incluye:
- Portal web con todas las funcionalidades
- Monitoreo local automático (Windows Exporter)
- Sistema de alertas por email
- Integración cloud AWS/Azure
- Instalador automático completo

**20 archivos** - Todo lo necesario incluido

### 🔧 Funcionalidades
✅ **Instalación automática** - Un comando configura todo
✅ **Portal web moderno** - Dashboard Bootstrap 5
✅ **Monitoreo en tiempo real** - CPU, RAM, Disco
✅ **Alertas por email** - SMTP integrado
✅ **Cloud integration** - AWS/Azure auto-discovery
✅ **SSH scanner** - Configuración automática




## ✨ Novedades v3.1.0

### 🎨 Mejoras Visuales
- ✅ **Headers Modernizados** - Gradientes oscuros con mejor contraste
- ✅ **Navbar Profesional** - Diseño moderno con efectos hover
- ✅ **Dashboards Corregidos** - 4 dashboards Grafana actualizados
- ✅ **Dashboard Maestro** - Nueva vista unificada del sistema

### 🔧 Funcionalidades Mejoradas
- ✅ **Botón Descarga Mejorado** - Sin pop-ups, descarga directa
- ✅ **Optimización de Costos** - Motor completo operacional
- ✅ **Replicación Infraestructura** - Generación IaC automática
- ✅ **Windows Exporter** - Integrado y funcionando (4249 métricas)

### 🔒 Seguridad
- ✅ **Credenciales Protegidas** - .gitignore configurado
- ✅ **Archivos .example** - Plantillas de configuración
- ✅ **Documentación Completa** - Guías de seguridad incluidas

### 📚 Documentación Nueva
- 📄 [DASHBOARDS_MODERNIZADOS.md](DASHBOARDS_MODERNIZADOS.md) - Guía completa de dashboards
- 📄 [CONFIGURACION_CREDENCIALES.md](CONFIGURACION_CREDENCIALES.md) - Setup de credenciales AWS/Azure
- 📄 `scripts/fix_all_dashboards.ps1` - Script de modernización

---

## ℹ️ Información del Sistema
- **Versión**: 3.1.0-COST-OPTIMIZER
- **Tipo**: Sistema autosuficiente completo
- **Instalación**: Automática (sin configuración manual)
- **Dependencias**: Docker + Python (auto-verificadas)
- **Dashboards**: 4 corregidos + 1 maestro nuevo
- **Métricas**: 4249 métricas de Windows disponibles

## 🎯 Para Desarrolladores
Todo el código está en `OptiMon-BASE-UNIFICADO/`:
- `app.py` - Portal principal (4577 líneas)
- `cost_optimization_engine.py` - Motor de optimización
- `iac_generator.py` - Generador de infraestructura
- `infrastructure_replication_engine.py` - Replicación IaC
- `docker/` - Configuraciones servicios
- `templates/` - Interfaces HTML modernizadas
- `config/` - Configuraciones Prometheus, Grafana, AlertManager

## 📊 Dashboards Disponibles

### Dashboard Maestro (Nuevo en v3.1.0)
- **URL:** http://localhost:3000/d/optimon-master-modern/
- **Características:** CPU, Memoria, Disco en tiempo real
- **Actualización:** Automática cada 30 segundos

### Otros Dashboards
- 🖥️ **Windows Real:** http://localhost:3000/d/optimon-windows-real/
- 🏠 **Sistema Local:** http://localhost:3000/d/optimon-local/
- ☁️ **AWS Instances:** http://localhost:3000/d/optimon-aws-working/

Ver documentación completa: [DASHBOARDS_MODERNIZADOS.md](DASHBOARDS_MODERNIZADOS.md)

## 🔐 Configuración de Credenciales

**IMPORTANTE:** Las credenciales de AWS/Azure NO están incluidas por seguridad.

### Setup rápido:
```bash
# Copiar plantilla
cp OptiMon-BASE-UNIFICADO/config/cloud_credentials.json.example \
   OptiMon-BASE-UNIFICADO/config/cloud_credentials.json

# Editar con tus credenciales
notepad OptiMon-BASE-UNIFICADO/config/cloud_credentials.json
```

Ver guía completa: [CONFIGURACION_CREDENCIALES.md](CONFIGURACION_CREDENCIALES.md)

## 🚀 Componentes del Sistema

```
┌─────────────────────────────────────────────────┐
│            OptiMon v3.1.0                       │
├─────────────────────────────────────────────────┤
│  Flask (5000)    Prometheus (9090)  Grafana     │
│  Windows Exp.    AlertManager       (3000)      │
│  AWS Monitor     Azure Monitor                  │
└─────────────────────────────────────────────────┘
```

## 📈 Métricas y Monitoreo

- ✅ **Windows Local:** 4249 métricas (CPU, RAM, Disco, Red)
- ✅ **AWS EC2:** Instancias, CPU, Memoria, Estado
- ✅ **Azure VM:** Máquinas virtuales, Recursos
- ✅ **Servidores Físicos:** Node Exporter compatible

## 🆘 Solución de Problemas

### Dashboard sin datos
1. Verifica Windows Exporter: http://localhost:9182/metrics
2. Verifica Prometheus: http://localhost:9090/targets
3. Refresca con Ctrl + F5

### Credenciales no funcionan
Ver [CONFIGURACION_CREDENCIALES.md](CONFIGURACION_CREDENCIALES.md)

### Docker no inicia
```bash
docker-compose down --remove-orphans
docker-compose up -d
```

## 📚 Documentación Adicional

- 📘 [OptiMon-BASE-UNIFICADO/README_SISTEMA_COMPLETO.md](OptiMon-BASE-UNIFICADO/README_SISTEMA_COMPLETO.md)
- 📗 [DASHBOARDS_MODERNIZADOS.md](DASHBOARDS_MODERNIZADOS.md)
- 📙 [CONFIGURACION_CREDENCIALES.md](CONFIGURACION_CREDENCIALES.md)

**¡Sistema completamente refactorizado y optimizado!**
