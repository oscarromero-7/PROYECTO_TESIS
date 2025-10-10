# OptiMon - Sistema de Monitoreo Automatizado
## Manual de Usuario Completo

### 🎯 Descripción General
OptiMon es un sistema completamente automatizado de monitoreo de infraestructura que:
- Monitorea servicios Docker (Prometheus, Grafana, AlertManager)
- Verifica y corrige automáticamente dashboards
- Detecta y soluciona problemas de configuración
- Se ejecuta como servicio de Windows
- Genera logs detallados de todas las operaciones

### 📋 Requisitos del Sistema
- Windows 10/11 o Windows Server
- Python 3.8 o superior
- Docker Desktop instalado y funcionando
- Servicios OptiMon ejecutándose (Prometheus, Grafana)

### 🚀 Instalación Rápida

#### Paso 1: Instalación del Servicio
```bash
# Ejecutar como Administrador
install_optimon_service.bat
```

#### Paso 2: Configuración Inicial
```bash
python configure_optimon.py
```

#### Paso 3: Verificación Manual (Opcional)
```bash
python optimon_dashboard_service.py
```

### ⚙️ Configuración Avanzada

#### Archivo de Configuración (optimon_config.json)
```json
{
  "verification_interval_minutes": 5,
  "auto_restart_services": true,
  "max_retry_attempts": 3,
  "notification_webhook": "",
  "enabled_checks": {
    "prometheus_health": true,
    "grafana_health": true,
    "dashboard_validation": true,
    "datasource_correction": true,
    "auto_import": true
  }
}
```

#### Parámetros Configurables
- **verification_interval_minutes**: Frecuencia de verificación (recomendado: 5-15 minutos)
- **auto_restart_services**: Reiniciar servicios Docker automáticamente si fallan
- **max_retry_attempts**: Número máximo de reintentos antes de alertar
- **enabled_checks**: Activar/desactivar verificaciones específicas

### 🔧 Comandos de Gestión

#### Gestión del Servicio Windows
```bash
# Iniciar servicio
schtasks /run /tn "OptiMon Dashboard Service"

# Detener servicio
schtasks /end /tn "OptiMon Dashboard Service"

# Ver estado del servicio
schtasks /query /tn "OptiMon Dashboard Service"

# Desinstalar servicio
schtasks /delete /tn "OptiMon Dashboard Service" /f
```

#### Verificación Manual
```bash
# Verificación única
python optimon_dashboard_service.py

# Configurar parámetros
python configure_optimon.py

# Ver logs en tiempo real
Get-Content optimon_service.log -Wait
```

### 📊 Monitoreo y Logs

#### Archivos de Log
- **optimon_service.log**: Log principal del servicio
- **dashboard_verification.log**: Logs específicos de verificación de dashboards

#### Interpretación de Logs
```
[2024-01-15 10:30:00] INICIANDO VERIFICACION PROGRAMADA
[2024-01-15 10:30:01] Verificando servicios Docker...
[2024-01-15 10:30:02] Servicios Docker verificados: 3 activos
[2024-01-15 10:30:03] Iniciando verificacion automatica de dashboards...
[2024-01-15 10:30:05] Verificacion completada exitosamente
[2024-01-15 10:30:05] Todos los dashboards funcionando correctamente
```

### 🛠️ Funcionalidades Automatizadas

#### 1. Verificación de Servicios Docker
- Verifica que Prometheus, Grafana y AlertManager estén ejecutándose
- Reinicia servicios automáticamente si fallan
- Monitorea uso de recursos

#### 2. Validación de Dashboards
- Verifica integridad de archivos JSON
- Corrige UIDs de datasources automáticamente
- Importa dashboards faltantes a Grafana
- Valida consultas de Prometheus

#### 3. Autocorrección de Problemas
- Corrige configuraciones incorrectas
- Regenera dashboards dañados
- Sincroniza datasources
- Maneja conflictos de importación

#### 4. Alertas y Notificaciones
- Logs detallados de todas las operaciones
- Alertas en caso de fallos críticos
- Reportes de estado periódicos

### 🚨 Resolución de Problemas

#### Problema: Servicio no inicia
```bash
# Verificar permisos
schtasks /query /tn "OptiMon Dashboard Service" /v

# Verificar Python
python --version

# Verificar dependencias
python -c "import schedule, requests; print('OK')"
```

#### Problema: Dashboards no se corrigen
```bash
# Verificar conectividad con Grafana
curl http://localhost:3000/api/health

# Verificar conectividad con Prometheus
curl http://localhost:9090/-/healthy

# Ejecutar verificación manual con debug
python optimon_dashboard_service.py
```

#### Problema: Servicios Docker fallan
```bash
# Verificar estado de Docker
docker ps

# Reiniciar servicios manualmente
cd 2-INICIAR-MONITOREO
docker-compose restart

# Verificar logs de Docker
docker-compose logs
```

### 📈 Dashboard de Monitoreo

El sistema incluye dashboards específicos para:
- **Windows Local**: Monitoreo de la máquina local
- **AWS Infrastructure**: Monitoreo de instancias EC2
- **Azure Infrastructure**: Monitoreo de VMs de Azure
- **Physical Servers**: Monitoreo de servidores físicos

### 🔄 Actualizaciones y Mantenimiento

#### Actualización de Dashboards
Los dashboards se actualizan automáticamente cuando:
- Se detectan archivos JSON modificados
- Se cambian configuraciones de datasources
- Se agregan nuevos dashboards al directorio

#### Mantenimiento Preventivo
El sistema ejecuta automáticamente:
- Limpieza de logs antiguos
- Verificación de integridad de archivos
- Optimización de consultas de Prometheus
- Sincronización de configuraciones

### 📞 Soporte y Documentación

#### Archivos de Referencia
- `dashboard_auto_verifier_simple.py`: Motor de verificación principal
- `optimon_dashboard_service.py`: Servicio de monitoreo
- `configure_optimon.py`: Configurador del sistema

#### Comandos de Diagnóstico
```bash
# Estado completo del sistema
python optimon_dashboard_service.py --status

# Verificación de configuración
python configure_optimon.py --check

# Reporte de salud del sistema
python dashboard_auto_verifier_simple.py --health
```

### 🎯 Mejores Prácticas

1. **Configuración Inicial**
   - Configura intervalos de verificación según tu carga de trabajo
   - Habilita auto-reinicio para entornos de producción
   - Configura notificaciones para alertas críticas

2. **Monitoreo Continuo**
   - Revisa logs periódicamente
   - Monitorea uso de recursos del sistema
   - Mantén respaldos de configuraciones

3. **Mantenimiento**
   - Actualiza dashboards según necesidades
   - Optimiza consultas de Prometheus lentas
   - Documenta cambios en configuraciones

### ✅ Lista de Verificación Post-Instalación

- [ ] Servicio Windows creado correctamente
- [ ] Configuración inicial completada
- [ ] Servicios Docker ejecutándose
- [ ] Dashboards importados en Grafana
- [ ] Verificación automática funcionando
- [ ] Logs generándose correctamente
- [ ] Acceso a interfaces web (Grafana: localhost:3000, Prometheus: localhost:9090)

**¡OptiMon está listo para monitorear tu infraestructura 24/7!**