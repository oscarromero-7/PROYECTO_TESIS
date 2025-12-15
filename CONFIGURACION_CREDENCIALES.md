# 🔒 Configuración de Credenciales - OptiMon

**IMPORTANTE:** Por seguridad, las credenciales de AWS y Azure NO están incluidas en el repositorio.

---

## 📋 Archivos de Configuración Requeridos

### 1. **Credenciales de Nube** (OBLIGATORIO para AWS/Azure)

Crear el archivo: `OptiMon-BASE-UNIFICADO/config/cloud_credentials.json`

```json
{
  "aws": {
    "enabled": true,
    "region": "us-east-1",
    "access_key_id": "TU_AWS_ACCESS_KEY_ID_AQUI",
    "secret_access_key": "TU_AWS_SECRET_ACCESS_KEY_AQUI"
  },
  "azure": {
    "enabled": true,
    "subscription_id": "TU_AZURE_SUBSCRIPTION_ID_AQUI",
    "tenant_id": "TU_AZURE_TENANT_ID_AQUI",
    "client_id": "TU_AZURE_CLIENT_ID_AQUI",
    "client_secret": "TU_AZURE_CLIENT_SECRET_AQUI"
  }
}
```

### 2. **Credenciales de Nube (Formato Alternativo)**

Crear el archivo: `config/cloud_credentials.json`

```json
{
  "aws_access_key_id": "TU_AWS_ACCESS_KEY_ID_AQUI",
  "aws_secret_access_key": "TU_AWS_SECRET_ACCESS_KEY_AQUI",
  "aws_region": "us-east-1",
  "azure_subscription_id": "TU_AZURE_SUBSCRIPTION_ID_AQUI",
  "azure_tenant_id": "TU_AZURE_TENANT_ID_AQUI",
  "azure_client_id": "TU_AZURE_CLIENT_ID_AQUI",
  "azure_client_secret": "TU_AZURE_CLIENT_SECRET_AQUI"
}
```

---

## 🚀 Pasos para Configurar

### Opción 1: Copiar desde ejemplo

```bash
# En OptiMon-BASE-UNIFICADO/config/
cp cloud_credentials.json.example cloud_credentials.json

# Editar y agregar tus credenciales
notepad cloud_credentials.json
```

### Opción 2: Crear manualmente

1. Crea el archivo `cloud_credentials.json` en la ruta correcta
2. Copia el formato JSON de arriba
3. Reemplaza los valores `TU_*_AQUI` con tus credenciales reales

---

## 🔑 Cómo Obtener las Credenciales

### AWS

1. **Accede a AWS Console:** https://console.aws.amazon.com/
2. **IAM → Users → Security credentials**
3. **Create access key** → Descarga el archivo CSV
4. Usa `Access Key ID` y `Secret Access Key`

### Azure

1. **Accede a Azure Portal:** https://portal.azure.com/
2. **Azure Active Directory → App registrations**
3. **New registration** (si no tienes una app)
4. Obtén:
   - `Subscription ID`: En "Subscriptions"
   - `Tenant ID`: En "App registration overview"
   - `Client ID`: En "App registration overview"
   - `Client Secret`: En "Certificates & secrets" → New client secret

---

## ⚠️ IMPORTANTE - Seguridad

### ❌ NO HACER:
- ❌ NO subas `cloud_credentials.json` a GitHub
- ❌ NO compartas tus credenciales en chat/email
- ❌ NO las incluyas en capturas de pantalla

### ✅ HACER:
- ✅ Mantén las credenciales solo localmente
- ✅ Usa el archivo `.gitignore` (ya configurado)
- ✅ Rota las credenciales periódicamente
- ✅ Usa credenciales de solo lectura cuando sea posible

---

## 🧪 Verificar Configuración

Después de configurar las credenciales, verifica que funcionen:

```bash
cd OptiMon-BASE-UNIFICADO
python app.py
```

Luego accede a:
- **Dashboard:** http://localhost:5000/
- **Cloud Config:** Deberías ver tus instancias AWS/Azure

---

## 📁 Estructura de Archivos

```
PROYECTO_TESIS/
├── OptiMon-BASE-UNIFICADO/
│   ├── config/
│   │   ├── cloud_credentials.json          ← CREAR ESTE (ignorado por git)
│   │   ├── cloud_credentials.json.example  ← Plantilla
│   │   ├── alertmanager/
│   │   ├── prometheus/
│   │   └── grafana/
│   └── ...
├── config/
│   ├── cloud_credentials.json              ← CREAR ESTE (ignorado por git)
│   ├── cloud_credentials.json.example      ← Plantilla
│   └── ...
└── .gitignore                               ← Protege credenciales
```

---

## 🆘 Problemas Comunes

### "No cloud credentials found"
**Solución:** Verifica que el archivo `cloud_credentials.json` esté en la ruta correcta:
- `OptiMon-BASE-UNIFICADO/config/cloud_credentials.json`
- `config/cloud_credentials.json`

### "Invalid AWS credentials"
**Solución:** 
1. Verifica que el Access Key ID y Secret Access Key sean correctos
2. Asegúrate de que no haya espacios al copiar/pegar
3. Verifica que el usuario IAM tenga permisos de EC2

### "Invalid Azure credentials"
**Solución:**
1. Verifica que el Service Principal esté creado
2. Asegúrate de que tenga permisos de "Reader" en la subscripción
3. Verifica que el Client Secret no haya expirado

---

## 📚 Recursos Adicionales

- **AWS IAM Guide:** https://docs.aws.amazon.com/IAM/latest/UserGuide/
- **Azure Service Principals:** https://learn.microsoft.com/azure/active-directory/develop/app-objects-and-service-principals
- **OptiMon Documentation:** Ver `DASHBOARDS_MODERNIZADOS.md`

---

**Generado:** 15 de Diciembre de 2025  
**Sistema:** OptiMon v3.1.0-COST-OPTIMIZER
