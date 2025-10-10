# 🏗️ PLAN DE RESTRUCTURACIÓN - PROYECTO OptiMon

## 📊 **ANÁLISIS ACTUAL**

### ❌ **PROBLEMAS IDENTIFICADOS:**
1. **Archivos duplicados** - Múltiples versiones del mismo archivo
2. **Estructura desordenada** - Archivos mezclados sin organización
3. **Scripts de prueba dispersos** - Testing sin estructura
4. **Documentación fragmentada** - Múltiples README y manuales
5. **Configuraciones duplicadas** - Configs en múltiples lugares
6. **Archivos temporales** - Logs, cache y archivos de prueba
7. **Dependencias mezcladas** - Core y utilidades juntos

### 📈 **ARCHIVOS FUNCIONALES CORE:**
```
✅ SERVICIOS PRINCIPALES:
- 2-INICIAR-MONITOREO/optimon_service_manager.py (GESTOR PRINCIPAL)
- 2-INICIAR-MONITOREO/optimon_smtp_service.py (SMTP)
- 2-INICIAR-MONITOREO/optimon_dashboard.py (DASHBOARD WEB)
- 2-INICIAR-MONITOREO/dashboard_manager.py (GESTIÓN DASHBOARDS)

✅ CONFIGURACIONES:
- 2-INICIAR-MONITOREO/config/ (CONFIGS PRINCIPALES)
- 2-INICIAR-MONITOREO/docker-compose.yml
- 2-INICIAR-MONITOREO/.env.example

✅ TESTING FUNCIONAL:
- 2-INICIAR-MONITOREO/test_recipients.py
- 2-INICIAR-MONITOREO/test_real_alert.py
- 2-INICIAR-MONITOREO/test_complete_system.py
```

## 🎯 **NUEVA ESTRUCTURA PROPUESTA**

```
📁 PROYECTO_TESIS/
├── 📁 core/                           # SERVICIOS PRINCIPALES
│   ├── optimon_manager.py            # Gestor principal (renombrado)
│   ├── smtp_service.py               # Servicio SMTP (renombrado)
│   ├── web_dashboard.py              # Dashboard web (renombrado)
│   ├── dashboard_manager.py          # Gestión inteligente dashboards
│   └── __init__.py                   # Módulo Python
│
├── 📁 config/                         # CONFIGURACIONES
│   ├── 📁 docker/
│   │   └── docker-compose.yml
│   ├── 📁 prometheus/
│   │   ├── prometheus.yml
│   │   └── alert.rules.yml
│   ├── 📁 grafana/
│   │   ├── 📁 dashboards/
│   │   └── 📁 provisioning/
│   ├── 📁 alertmanager/
│   │   └── alertmanager.yml
│   ├── 📁 email/
│   │   └── recipients.json
│   ├── 📁 cloud/
│   │   └── credentials.json
│   └── .env.example
│
├── 📁 infrastructure/                 # INFRAESTRUCTURA
│   ├── 📁 terraform/
│   │   ├── 📁 aws/
│   │   └── 📁 azure/
│   ├── 📁 ansible/
│   └── 📁 scripts/
│       ├── 📁 install/
│       ├── 📁 setup/
│       └── 📁 deploy/
│
├── 📁 templates/                      # TEMPLATES WEB
│   ├── base.html
│   ├── dashboard.html
│   ├── monitoring.html
│   └── emails.html
│
├── 📁 tests/                          # TESTING ORGANIZADO
│   ├── 📁 unit/
│   ├── 📁 integration/
│   ├── 📁 e2e/
│   └── conftest.py
│
├── 📁 docs/                           # DOCUMENTACIÓN
│   ├── 📁 user-guide/
│   ├── 📁 api/
│   ├── 📁 deployment/
│   └── README.md
│
├── 📁 tools/                          # HERRAMIENTAS
│   ├── 📁 validators/
│   ├── 📁 generators/
│   └── 📁 utilities/
│
├── 📁 logs/                           # LOGS CENTRALIZADOS
│   └── .gitkeep
│
├── 📁 data/                           # DATOS PERSISTENTES
│   └── .gitkeep
│
├── requirements.txt                   # DEPENDENCIAS
├── setup.py                          # INSTALACIÓN
├── CHANGELOG.md                       # CAMBIOS
├── LICENSE                           # LICENCIA
└── README.md                         # PRINCIPAL
```

## 🚀 **PLAN DE MIGRACIÓN**

### **FASE 1: PREPARACIÓN**
1. Crear nueva estructura de directorios
2. Identificar archivos core vs basura
3. Backup de configuraciones importantes

### **FASE 2: MIGRACIÓN CORE**
1. Mover servicios principales a `/core`
2. Reorganizar configuraciones en `/config`
3. Consolidar templates en `/templates`

### **FASE 3: TESTING & DOCS**
1. Reorganizar tests en `/tests`
2. Consolidar documentación en `/docs`
3. Crear herramientas en `/tools`

### **FASE 4: INFRAESTRUCTURA**
1. Mover Terraform/Ansible a `/infrastructure`
2. Organizar scripts por función
3. Limpiar archivos temporales

### **FASE 5: LIMPIEZA**
1. Eliminar archivos duplicados/obsoletos
2. Actualizar imports/paths
3. Crear nueva documentación

## ❌ **ARCHIVOS A ELIMINAR**

### **DUPLICADOS:**
- Múltiples versiones de dashboard verifiers
- Scripts de instalación duplicados
- Archivos de configuración obsoletos
- Logs antiguos y temporales

### **ARCHIVOS BASURA:**
- *.pyc, __pycache__/
- *.log (excepto logs importantes)
- Archivos de prueba temporales
- Versiones de backup antiguas
- Screenshots y archivos de depuración

### **OBSOLETOS:**
- Scripts de versiones anteriores
- Configuraciones de prueba
- Documentación fragmentada
- Archivos de instalación manual

## 🎯 **BENEFICIOS ESPERADOS**

### **ORGANIZACIÓN:**
- ✅ Estructura clara y profesional
- ✅ Separación por responsabilidades
- ✅ Facilidad de navegación
- ✅ Mantenimiento simplificado

### **DESARROLLO:**
- ✅ Imports limpios y claros
- ✅ Testing organizado
- ✅ Documentación centralizada
- ✅ CI/CD preparado

### **DESPLIEGUE:**
- ✅ Configuraciones centralizadas
- ✅ Scripts organizados
- ✅ Logs centralizados
- ✅ Monitoreo estructurado

## 📝 **SIGUIENTE PASO**

¿Procedo con la implementación del plan de restructuración?

1. **Automático** - Ejecutar migración completa
2. **Manual** - Ir paso a paso para revisión
3. **Personalizado** - Ajustar estructura según preferencias
