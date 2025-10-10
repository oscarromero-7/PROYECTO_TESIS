# 🎯 OPTIMON v2.0 - INSTALACIÓN DESDE CERO

## ✅ ESTADO ACTUAL DEL SISTEMA
- ❌ Windows Exporter: **ELIMINADO** del sistema
- ✅ Credenciales SMTP: **MANTENIDAS** (para envío de alertas)
- ✅ Destinatarios: **LIMPIADOS** (usar emails de ejemplo)
- ✅ ZIP listo: **OptiMon-v2.0-Clean-20251009.zip**

## 📦 CONTENIDO DEL ZIP
```
OptiMon-v2.0-Clean/
├── 1-CREAR-INFRAESTRUCTURA/     # Terraform para infraestructura
├── 2-INICIAR-MONITOREO/         # Scripts principales de OptiMon
├── docker/                      # Configuraciones Docker
├── grafana/                     # Dashboards y configuración
├── prometheus/                  # Configuración de métricas
├── scripts/                     # Scripts auxiliares
└── *.py, *.md, *.txt           # Archivos de configuración
```

## 🚀 INSTALACIÓN PASO A PASO

### 1. Extraer ZIP
```bash
# Extraer en directorio limpio
Expand-Archive OptiMon-v2.0-Clean-20251009.zip -DestinationPath C:\OptiMon
cd C:\OptiMon
```

### 2. Configurar SMTP (OBLIGATORIO)
**El sistema mantiene tus credenciales Gmail**, pero necesitas configurar destinatarios:

**Editar:** `2-INICIAR-MONITOREO\config\optimon\email_recipients.json`
```json
{
  "recipients": [
    {
      "email": "tu-admin@empresa.com",
      "name": "Administrador",
      "active": true,
      "added_date": "2025-10-09T00:00:00.000000"
    }
  ],
  "default_recipient": "tu-admin@empresa.com"
}
```

### 3. Verificar requisitos
```bash
# Verificar Python
python --version  # Debe ser 3.8+

# Verificar Docker
docker --version
docker-compose --version

# Verificar puertos libres
netstat -ano | findstr ":3000 :5000 :5555 :9090 :9093 :9182"
```

### 4. Ejecutar instalación completa
```bash
cd 2-INICIAR-MONITOREO
python start_optimon_complete.py
```

### 5. Verificar instalación
El script debería mostrar:
```
🎉 SISTEMA INICIADO EXITOSAMENTE (100.0%)
🌐 Interfaces disponibles:
  • Dashboard OptiMon: http://localhost:5000
  • Grafana: http://localhost:3000 (admin/admin)
  • Prometheus: http://localhost:9090
  • AlertManager: http://localhost:9093
  • Windows Exporter: http://localhost:9182/metrics
```

## 🔧 PRUEBA DEL SISTEMA

### Prueba automática completa
```bash
cd 2-INICIAR-MONITOREO
python test_windows_exporter_complete.py
```

Debería mostrar:
```
🏆 RESULTADO: 5/5 pruebas exitosas (100.0%)
🎉 EXCELENTE - Instalación y funcionalidad perfectas
```

### Prueba manual de componentes
```bash
# 1. Dashboard
curl http://localhost:5000/api/local/windows-exporter/status

# 2. Windows Exporter (se instala automáticamente)
curl http://localhost:9182/metrics

# 3. Prometheus
curl http://localhost:9090/api/v1/targets

# 4. Grafana
# Abrir: http://localhost:3000 (admin/admin)
```

## 📧 PRUEBA DE ALERTAS

### Enviar email de prueba
```bash
cd 2-INICIAR-MONITOREO
python test_email_direct.py
```

## 🛠️ SOLUCIÓN DE PROBLEMAS

### Puerto ocupado
```bash
# Ver qué usa el puerto
netstat -ano | findstr :PUERTO

# Terminar proceso
taskkill /PID <PID> /F
```

### Docker no inicia
```bash
# Reiniciar Docker Desktop
# Verificar que Docker está ejecutándose
docker ps
```

### Windows Exporter no instala
- El sistema lo descarga automáticamente
- Se instala en: `C:\optimon\windows_exporter\`
- Puerto: 9182

## 🎯 CARACTERÍSTICAS DEL SISTEMA LIMPIO

✅ **Windows Exporter**: Se instala automáticamente la primera vez
✅ **SMTP Service**: Mantiene tus credenciales Gmail
✅ **Dashboard Web**: Interfaz completa en puerto 5000
✅ **Docker Services**: Prometheus, Grafana, AlertManager
✅ **Ejecución en segundo plano**: Todos los servicios
✅ **Detección inteligente**: No reinstala si ya existe
✅ **APIs completas**: Gestión remota via REST

## 📊 MÉTRICAS ESPERADAS
- **Windows Exporter**: ~4,200 métricas Windows
- **Prometheus Targets**: 5 targets activos
- **Grafana Dashboards**: Pre-configurados
- **Email Alerts**: Automáticos via AlertManager

---

**🎉 ¡Sistema completamente limpio y listo para prueba desde cero!**

El ZIP **OptiMon-v2.0-Clean-20251009.zip** contiene todo lo necesario para una instalación completa en cualquier máquina Windows.