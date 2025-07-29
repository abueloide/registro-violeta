# 🛠️ Guía de Troubleshooting - Registro Violeta

## 🚨 Problema: No puedo iniciar sesión

### ✅ **Verificaciones Básicas**

1. **Credenciales por defecto:**
   ```
   Email: admin@registrovioleta.org
   Contraseña: RegistroVioleta2025!
   ```

2. **URLs correctas:**
   - Backend (Railway): Debe terminar en `.railway.app`
   - Frontend (Vercel): Debe apuntar al backend correcto en `REACT_APP_BACKEND_URL`

### 🔧 **Pasos de Diagnóstico**

#### **1. Verificar Backend (Railway)**
```bash
# Comprobar logs de Railway
railway logs

# Verificar variables de entorno
railway variables

# Test de salud del API
curl https://tu-app.railway.app/api/health
```

#### **2. Variables de Entorno Requeridas en Railway**
```bash
MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/registro_violeta
JWT_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
```

#### **3. MongoDB Atlas Setup**
1. Crear cuenta en [MongoDB Atlas](https://mongodb.com/atlas)
2. Crear cluster gratuito (512MB)
3. Configurar usuario de base de datos
4. Whitelist IP: `0.0.0.0/0` (para Railway)
5. Obtener connection string

#### **4. Frontend (Vercel) Configuration**
```bash
# En Vercel, configurar:
REACT_APP_BACKEND_URL=https://tu-app.railway.app
```

### 🐛 **Errores Comunes y Soluciones**

#### **Error: "Error de conexión al servidor"**
```
Causa: Frontend no puede conectar con backend
Solución:
1. Verificar que Railway app esté desplegada
2. Comprobar REACT_APP_BACKEND_URL en Vercel
3. Verificar CORS en backend (ya configurado)
```

#### **Error: "Database connection failed"**
```
Causa: MongoDB no conecta
Solución:
1. Verificar MONGO_URL en Railway
2. Verificar usuario/password de MongoDB Atlas
3. Comprobar whitelist IP en Atlas
```

#### **Error: "JWT_SECRET_KEY not set"**
```
Causa: Variable de entorno faltante
Solución:
1. Generar clave: python -c "import secrets; print(secrets.token_urlsafe(32))"
2. Configurar en Railway variables
```

#### **Error: "No admin user found"**
```
Causa: Base de datos vacía
Solución:
1. El script railway-start.sh auto-crea admin
2. O ejecutar manualmente: python backend/init_admin.py
```

### 📋 **Checklist de Deployment**

#### **Railway (Backend):**
- [ ] Repositorio conectado a Railway
- [ ] Variables de entorno configuradas:
  - [ ] `MONGO_URL` con MongoDB Atlas
  - [ ] `JWT_SECRET_KEY` generada
- [ ] Deploy exitoso (logs sin errores)
- [ ] API responde en `/api/health`

#### **Vercel (Frontend):**
- [ ] Repositorio conectado a Vercel
- [ ] Variable configurada:
  - [ ] `REACT_APP_BACKEND_URL` apunta a Railway
- [ ] Build exitoso
- [ ] Frontend carga sin errores

#### **MongoDB Atlas:**
- [ ] Cluster creado y funcionando
- [ ] Usuario de base de datos creado
- [ ] IP 0.0.0.0/0 en whitelist
- [ ] Connection string correcto

### 🧪 **Tests Manuales**

#### **1. Test Backend Health**
```bash
curl https://tu-app.railway.app/api/health
# Debe retornar: {"status": "healthy", "database": "connected"}
```

#### **2. Test Login API**
```bash
curl -X POST https://tu-app.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@registrovioleta.org", "password": "RegistroVioleta2025!"}'
```

#### **3. Test Frontend Connection**
1. Abrir DevTools (F12)
2. Ir a Network tab
3. Intentar login
4. Verificar requests al backend

### 🔄 **Redeployment Steps**

Si nada funciona, redeploy completo:

#### **Backend (Railway):**
```bash
# Force redeploy
railway up --detach

# O desde Railway Dashboard:
# Settings > Deploy > Manual Deploy
```

#### **Frontend (Vercel):**
```bash
# Force redeploy desde Vercel Dashboard:
# Deployments > ... > Redeploy
```

### 📞 **Obtener Ayuda**

Si el problema persiste:

1. **Recopilar información:**
   - URL del backend (Railway)
   - URL del frontend (Vercel)
   - Screenshot del error
   - Logs de Railway
   - Network tab del navegador

2. **Lugares para buscar ayuda:**
   - [GitHub Issues](https://github.com/abueloide/registro-violeta/issues)
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)

### 🎯 **Configuración Exitosa**

Cuando todo funcione correctamente verás:

- ✅ Backend health check pasa
- ✅ Frontend muestra "Servidor conectado correctamente"
- ✅ Login funciona con credenciales por defecto
- ✅ Dashboard carga después del login

### 🔒 **Seguridad Post-Deploy**

Después del primer login exitoso:

1. Cambiar contraseña del admin
2. Crear usuarios específicos por rol
3. Regenerar JWT_SECRET_KEY si es necesario
4. Configurar Google Drive API (opcional)
5. Configurar Telegram Bot (opcional)

---

**💜 ¿Todo funcionando?** ¡Perfecto! Ya tienes Registro Violeta funcionando al 100%.
