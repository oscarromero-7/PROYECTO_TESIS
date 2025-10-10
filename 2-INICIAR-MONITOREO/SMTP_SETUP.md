# 📧 Guía de Configuración SMTP - OptiMon

## 🚀 Configuración Rápida

### Opción 1: Configurador Automático (Recomendado)
```bash
python configure_smtp.py
```

### Opción 2: Configuración Manual

1. **Copia el archivo de ejemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Edita el archivo `.env` con tus datos:**

#### Para Gmail:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion
SMTP_USE_TLS=true
```

#### Para Outlook/Hotmail:
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@hotmail.com
SMTP_PASSWORD=tu-contraseña
SMTP_USE_TLS=true
```

## 🔐 Configuración de Proveedores

### Gmail
1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Seguridad → Verificación en 2 pasos (activar)
3. Contraseñas de aplicaciones → Generar nueva
4. Selecciona "Correo" y copia la contraseña generada
5. Usa esa contraseña en `SMTP_PASSWORD`

### Outlook/Hotmail
1. Ve a [account.microsoft.com](https://account.microsoft.com)
2. Seguridad → Verificación en dos pasos (activar)
3. Puedes usar tu contraseña normal o generar una contraseña de aplicación

### Yahoo
1. Ve a [login.yahoo.com](https://login.yahoo.com)
2. Seguridad de la cuenta → Verificación en 2 pasos (activar)
3. Generar contraseña de aplicación
4. Usa esa contraseña en `SMTP_PASSWORD`

## ✅ Verificar Configuración

```bash
# Instalar dependencias
pip install -r requirements_smtp.txt

# Verificar configuración
python optimon_smtp_service.py

# Probar envío
python test_email_direct.py
```

## 🔧 Solución de Problemas

### Error de Autenticación
- Verifica que tengas verificación en 2 pasos activada
- Usa contraseña de aplicación, no la contraseña normal
- Revisa que el usuario/email sea correcto

### Error de Conexión
- Verifica el host y puerto SMTP
- Comprueba tu conexión a internet
- Algunos ISP bloquean puertos SMTP

### No se envían emails
- Revisa la carpeta de spam
- Verifica que los destinatarios estén configurados en `email_config.py`
- Comprueba los logs del servicio para errores

## 📋 Comandos Útiles

```bash
# Ver configuración actual de emails
python email_config.py list

# Agregar email destinatario
python email_config.py add nuevo@email.com

# Simular envío (sin SMTP real)
python simulate_emails.py

# Prueba completa del sistema
python system_status.py
```

## 🔒 Seguridad

- **NUNCA** subas el archivo `.env` a repositorios públicos
- Usa contraseñas de aplicación, no contraseñas principales
- El archivo `.env` está en `.gitignore` para tu seguridad
- Revisa regularmente los accesos a tu cuenta de email