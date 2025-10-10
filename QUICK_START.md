# 🎉 OptiMon v2.0 - Instalación Inmediata

## ⚡ SISTEMA LISTO PARA USAR

**¡SMTP ya configurado!** Solo configura los destinatarios y comienza a recibir alertas.

---

## 🚀 INSTALACIÓN ULTRA-RÁPIDA

### Windows:
```cmd
1. Extraer este ZIP
2. Ejecutar: INSTALL.bat  
3. Ir a: http://localhost:5000/emails
4. Agregar destinatarios de alertas
5. ¡Listo! 🎉
```

### Linux/Mac:
```bash
1. Extraer este ZIP
2. chmod +x install.sh && ./install.sh
3. Ir a: http://localhost:5000/emails  
4. Agregar destinatarios de alertas
5. ¡Listo! 🎉
```

**⏱️ Tiempo total: menos de 3 minutos**

## 📋 Checklist de Funcionamiento

### ✅ Servicios Core
- [ ] Docker ejecutándose
- [ ] Prometheus (puerto 9090)
- [ ] Grafana (puerto 3000)
- [ ] AlertManager (puerto 9093)

### ✅ Servicios OptiMon
- [ ] SMTP Service (puerto 5555)
- [ ] Dashboard Web (puerto 5000)

### ✅ Funcionalidades
- [ ] Monitoreo de métricas del sistema
- [ ] Alertas configuradas
- [ ] Envío de emails automático
- [ ] Instalación de Node Exporter
- [ ] Configuración de clouds (AWS, Azure)

## 🛠️ Resolución Rápida de Problemas

### Problema: Dashboard no inicia
```bash
# Verificar que Docker esté funcionando
docker ps

# Reiniciar servicios
stop_optimon.bat
start_optimon_auto.bat
```

### Problema: Alertas no llegan por email
1. Ir a http://localhost:5000/emails
2. Configurar credenciales de email
3. Probar envío

### Problema: Métricas no aparecen
1. Verificar que Node Exporter esté instalado
2. Reiniciar Prometheus
3. Verificar configuración en http://localhost:9090/targets

## 📊 URLs Importantes

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| Prometheus | http://localhost:9090 | No requiere |
| Grafana | http://localhost:3000 | admin/admin |
| AlertManager | http://localhost:9093 | No requiere |
| Dashboard OptiMon | http://localhost:5000 | No requiere |
| SMTP Service | http://localhost:5555/health | No requiere |

## 🎯 Configuración Inicial

### 1. Configurar Email (Obligatorio)
- Ir a Dashboard → Configuración de Emails
- Ingresar credenciales Gmail
- Activar "Aplicaciones menos seguras" en Gmail

### 2. Añadir Cloud Provider
- AWS: Ir a Dashboard → AWS → Configurar credenciales
- Azure: Ir a Dashboard → Azure → Configurar credenciales

### 3. Monitorear Servidor Local
- Dashboard → Monitoreo Local → Instalar Node Exporter

## 📈 Próximos Pasos

1. **Personalizar Dashboards**: Acceder a Grafana y crear dashboards personalizados
2. **Configurar Alertas**: Personalizar reglas de alertas en AlertManager
3. **Escalabilidad**: Añadir más servidores al monitoreo
4. **Backup**: Configurar backup de configuraciones importantes

---
*OptiMon - Sistema de Monitoreo Automatizado*