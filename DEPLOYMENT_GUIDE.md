# 📦 Guía de Distribución y Despliegue - OptiMon v2.0

## 🎯 Resumen

Esta guía te ayudará a crear un **paquete de distribución completo** de OptiMon y desplegarlo en cualquier entorno.

---

## 📋 Paso 1: Crear Paquete de Distribución

### Ejecutar Generador de Paquete
```powershell
python create_distribution_package.py
```

### ¿Qué Genera?
- **ZIP completo** con todos los archivos necesarios
- **Scripts de instalación automática** (Windows + Linux)
- **Documentación completa** para usuarios finales
- **Configuraciones de ejemplo** pre-configuradas
- **Tests incluidos** para validación

### Resultado
```
OptiMon-v2.0-20251009.zip (~ 15-20 MB)
OptiMon-v2.0-20251009_INFO.json
```

---

## 📁 Contenido del Paquete ZIP

```
OptiMon-v2.0-20251009/
├── 📄 README.md                   # Documentación principal
├── 📄 INSTALL.bat                 # Instalador Windows
├── 📄 install.sh                  # Instalador Linux/Mac
├── 📄 requirements.txt            # Dependencias Python
├── 📄 .env.example                # Configuración ejemplo
│
├── 📁 optimon/                    # Servicios principales
│   ├── optimon_service_manager.py # Gestor principal
│   ├── optimon_smtp_service.py    # Servicio email
│   ├── optimon_dashboard.py       # Dashboard web
│   └── dashboard_manager.py       # Gestor dashboards
│
├── 📁 config/                     # Configuraciones
│   ├── docker/
│   │   └── docker-compose.yml
│   ├── prometheus/
│   ├── grafana/
│   ├── alertmanager/
│   └── email/
│       └── recipients.example.json
│
├── 📁 infrastructure/             # Terraform (opcional)
│   └── terraform/
│
├── 📁 tests/                      # Tests del sistema
│   ├── test_complete_system.py
│   ├── test_recipients.py
│   └── test_real_alert.py
│
├── 📁 scripts/                    # Utilidades
└── 📁 docs/                       # Documentación
    └── CONFIGURATION.md
```

---

## 🚀 Paso 2: Despliegue en Servidor de Producción

### A. Preparación del Servidor

#### Prerequisitos del Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip docker.io docker-compose git

# CentOS/RHEL
sudo yum install python3 python3-pip docker docker-compose git

# Windows Server
# - Instalar Python 3.8+
# - Instalar Docker Desktop
# - Instalar Git (opcional)
```

#### Verificar Prerequisitos
```bash
python3 --version  # >= 3.8
docker --version
docker-compose --version
```

### B. Instalación en Servidor Linux

```bash
# 1. Subir y extraer paquete
scp OptiMon-v2.0-20251009.zip user@servidor:/opt/
ssh user@servidor
cd /opt
unzip OptiMon-v2.0-20251009.zip
cd OptiMon-v2.0-20251009/

# 2. Ejecutar instalador
chmod +x install.sh
./install.sh

# 3. Configurar como servicio (opcional)
sudo cp scripts/optimon.service /etc/systemd/system/
sudo systemctl enable optimon
sudo systemctl start optimon
```

### C. Instalación en Windows Server

```powershell
# 1. Extraer ZIP en C:\OptiMon\
# 2. Abrir PowerShell como Administrador
cd C:\OptiMon\OptiMon-v2.0-20251009\

# 3. Ejecutar instalador
.\INSTALL.bat

# 4. Configurar como servicio (opcional)
# Usar Task Scheduler o NSSM para crear servicio
```

---

## ⚙️ Paso 3: Configuración Post-Instalación

### A. Configurar SMTP
```bash
# Editar archivo .env
nano .env

# Configurar para Gmail:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=monitoring@empresa.com
SMTP_PASSWORD=app-password-aqui
SMTP_FROM_EMAIL=monitoring@empresa.com
```

### B. Configurar Destinatarios
```bash
# Editar destinatarios de alertas
nano config/email/recipients.json

[
    {
        "name": "Admin Producción",
        "email": "admin@empresa.com",
        "alerts": ["critical", "warning"],
        "active": true
    }
]
```

### C. Configurar Firewall
```bash
# Ubuntu/Debian
sudo ufw allow 5000/tcp   # OptiMon Dashboard
sudo ufw allow 3000/tcp   # Grafana
sudo ufw allow 9090/tcp   # Prometheus
sudo ufw allow 9093/tcp   # AlertManager

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --permanent --add-port=9093/tcp
sudo firewall-cmd --reload
```

---

## 🔧 Paso 4: Configuración de Servicios

### A. Crear Servicio Systemd (Linux)

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/optimon.service
```

```ini
[Unit]
Description=OptiMon Monitoring Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=optimon
WorkingDirectory=/opt/OptiMon-v2.0-20251009
ExecStart=/usr/bin/python3 optimon/optimon_service_manager.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable optimon
sudo systemctl start optimon
sudo systemctl status optimon
```

### B. Configurar como Servicio Windows

```powershell
# Opción 1: Task Scheduler
schtasks /create /tn "OptiMon" /tr "C:\OptiMon\OptiMon-v2.0-20251009\optimon\optimon_service_manager.py" /sc onstart /ru SYSTEM

# Opción 2: NSSM (recomendado)
# 1. Descargar NSSM
# 2. nssm install OptiMon
# 3. Configurar ruta del ejecutable
```

---

## 🌐 Paso 5: Configuración de Proxy Reverso (Opcional)

### Nginx
```nginx
# /etc/nginx/sites-available/optimon
server {
    listen 80;
    server_name monitoring.empresa.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
    }
}
```

### Apache
```apache
# /etc/apache2/sites-available/optimon.conf
<VirtualHost *:80>
    ServerName monitoring.empresa.com
    
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    
    ProxyPass /grafana/ http://localhost:3000/
    ProxyPassReverse /grafana/ http://localhost:3000/
</VirtualHost>
```

---

## 🔒 Paso 6: Configuración de Seguridad

### A. SSL/TLS (Recomendado)
```bash
# Con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monitoring.empresa.com
```

### B. Autenticación Básica
```nginx
# Agregar a configuración Nginx
auth_basic "OptiMon Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

```bash
# Crear usuarios
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

### C. Configurar Grafana
```bash
# Cambiar password por defecto
curl -X PUT -H "Content-Type: application/json" \
-d '{"oldPassword":"admin","newPassword":"nuevo-password-seguro"}' \
http://admin:admin@localhost:3000/api/user/password
```

---

## 📊 Paso 7: Validación del Despliegue

### A. Tests Automáticos
```bash
# Ejecutar tests completos
python3 tests/test_complete_system.py

# Test específicos
python3 tests/test_recipients.py      # Test de emails
python3 tests/test_real_alert.py      # Test de alertas
```

### B. Verificación Manual
```bash
# Verificar servicios
curl http://localhost:5000/health     # OptiMon
curl http://localhost:3000/api/health # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:9093/-/healthy  # AlertManager

# Verificar Docker
docker ps | grep -E "(prometheus|grafana|alertmanager)"
```

### C. Test de Alertas
```bash
# Enviar alerta de prueba
curl -X POST http://localhost:5000/api/test-alert \
-H "Content-Type: application/json" \
-d '{"severity": "warning", "message": "Test de despliegue"}'
```

---

## 📋 Paso 8: Monitoreo Post-Despliegue

### A. Logs del Sistema
```bash
# Ver logs de OptiMon
tail -f logs/optimon.log

# Ver logs de Docker
docker logs prometheus
docker logs grafana
docker logs alertmanager

# Ver logs del sistema
sudo journalctl -u optimon -f
```

### B. Métricas de Sistema
```bash
# CPU y Memoria
top -p $(pgrep -f optimon)

# Espacio en disco
df -h

# Red
netstat -tlnp | grep -E "(5000|3000|9090|9093)"
```

### C. Alertas de Salud
```bash
# Configurar alerta de health check
curl -X POST http://localhost:5000/api/email/recipients \
-H "Content-Type: application/json" \
-d '{
    "name": "Health Monitor",
    "email": "ops@empresa.com",
    "alerts": ["system_health"],
    "active": true
}'
```

---

## 🚨 Paso 9: Troubleshooting Común

### Problemas de Conectividad
```bash
# Verificar puertos
sudo netstat -tlnp | grep -E "(5000|3000|9090|9093)"

# Verificar firewall
sudo ufw status
sudo iptables -L

# Test de conectividad
telnet localhost 5000
```

### Problemas de Docker
```bash
# Reiniciar servicios
cd config/docker
docker-compose down
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Problemas de Email
```bash
# Test manual de SMTP
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('user', 'pass')
print('SMTP OK')
"
```

---

## 📚 Paso 10: Documentación para Usuarios

### A. Manual de Usuario
- Acceso al dashboard: http://servidor:5000
- Gestión de destinatarios: /emails
- Configuración de alertas: /alerts
- Dashboards de Grafana: http://servidor:3000

### B. Procedimientos Operativos
```bash
# Reiniciar OptiMon
sudo systemctl restart optimon

# Actualizar configuración
nano .env
sudo systemctl restart optimon

# Backup de configuración
tar -czf optimon-backup-$(date +%Y%m%d).tar.gz config/ .env
```

### C. Contactos de Soporte
- **Admin Sistema**: admin@empresa.com
- **Equipo DevOps**: devops@empresa.com
- **Documentación**: Ver directorio `docs/`

---

## ✅ Checklist de Despliegue Completo

### Pre-Despliegue
- [ ] ✅ Servidor con prerequisitos instalados
- [ ] ✅ Credenciales SMTP configuradas
- [ ] ✅ Lista de destinatarios preparada
- [ ] ✅ Puertos de firewall abiertos
- [ ] ✅ Backup del sistema actual (si aplica)

### Durante el Despliegue
- [ ] ✅ Paquete ZIP extraído
- [ ] ✅ Instalador ejecutado sin errores
- [ ] ✅ Archivo .env configurado
- [ ] ✅ Servicios Docker iniciados
- [ ] ✅ OptiMon iniciado como servicio

### Post-Despliegue
- [ ] ✅ Tests automáticos ejecutados
- [ ] ✅ Verificación manual completada
- [ ] ✅ Alerta de prueba enviada
- [ ] ✅ Proxy reverso configurado (si aplica)
- [ ] ✅ SSL configurado (si aplica)
- [ ] ✅ Monitoreo de logs configurado
- [ ] ✅ Documentación entregada al equipo

---

## 🎯 Resultado Final

### Lo que tendrás funcionando:
- ✅ **OptiMon Dashboard** completamente operativo
- ✅ **Sistema de alertas** por email configurado
- ✅ **Monitoreo automático** de infraestructura
- ✅ **Grafana** con dashboards pre-configurados
- ✅ **Prometheus** recolectando métricas
- ✅ **AlertManager** gestionando notificaciones
- ✅ **Servicios automatizados** con auto-recuperación

### Accesos:
- **Dashboard**: http://tu-servidor:5000
- **Grafana**: http://tu-servidor:3000 (admin/tu-password)
- **Prometheus**: http://tu-servidor:9090
- **AlertManager**: http://tu-servidor:9093

---

## 📞 Soporte

- 📧 **Email**: admin@empresa.com
- 📚 **Docs**: Ver directorio `docs/` en el paquete
- 🐛 **Issues**: Reportar problemas con logs detallados

**¡OptiMon listo para producción! 🎉**