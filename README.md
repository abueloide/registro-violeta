# 🟣 Registro Violeta

**Registro Violeta** es una plataforma integral diseñada para fundaciones que apoyan a mujeres víctimas de violencia. Combina registro digital de sesiones terapéuticas, almacenamiento seguro en Google Drive, generación automática de PDFs y un bot de Telegram para notas rápidas.

## ✨ Características Principales

### 🔐 **Seguridad y Confidencialidad**
- Sistema de códigos anónimos (nunca nombres reales)
- Autenticación JWT con roles diferenciados
- Segregación por fundación (multi-tenant)
- Datos almacenados en Google Drive de la organización

### 📝 **Gestión de Sesiones Terapéuticas**
- Formulario completo basado en formato profesional oficial
- Generación automática de PDFs con formato oficial
- Almacenamiento automático en Google Drive organizado por usuaria
- Búsqueda y filtrado avanzado

### 👥 **Gestión de Perfiles**
- Perfiles anónimos con códigos únicos
- Seguimiento del estado del caso
- Historial completo de sesiones
- Reportes de progreso

### 🤖 **Bot de Telegram (Opcional)**
- Registro rápido de notas de voz
- Transcripción automática
- Clasificación por código de usuaria
- Backup automático en Drive

### 📊 **Dashboard y Reportes**
- Estadísticas en tiempo real
- Estado del sistema (DB, Drive, PDF)
- Descargas de PDF individuales
- Reportes por fundación

## 🛠️ Tecnologías

### Backend
- **FastAPI** - API REST moderna y rápida
- **MongoDB Atlas** - Base de datos NoSQL (512MB gratis)
- **Google Drive API** - Almacenamiento seguro de archivos
- **ReportLab** - Generación de PDFs profesionales
- **python-telegram-bot** - Bot integrado opcional

### Frontend
- **React 18** - Interfaz de usuario moderna
- **Tailwind CSS** - Diseño responsive y profesional
- **Axios** - Cliente HTTP
- **React Hook Form** - Formularios validados

### Hosting (100% Gratuito)
- **Railway** - Backend ($5 crédito mensual gratis)
- **Vercel** - Frontend (ilimitado gratuito)
- **MongoDB Atlas** - Base de datos (512MB gratis)
- **Google Drive** - Almacenamiento (15GB gratis)

## 🚀 Instalación y Despliegue

### ⚡ **Despliegue Rápido (1-Click)**

#### **Paso 1: Backend en Railway**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/abueloide/registro-violeta&envs=MONGO_URL,JWT_SECRET_KEY&referralCode=_registro-violeta)

**Variables requeridas:**
```bash
MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/registro_violeta
JWT_SECRET_KEY=tu-clave-secreta-generada-con-32-caracteres-minimo
```

#### **Paso 2: Frontend en Vercel**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/abueloide/registro-violeta/tree/main/frontend)

**Variable requerida:**
```bash
REACT_APP_BACKEND_URL=https://tu-app.railway.app
```

### 🔧 **Configuración Manual**

#### **1. MongoDB Atlas (Requerido)**
1. Crear cuenta en [MongoDB Atlas](https://mongodb.com/atlas)
2. Crear cluster gratuito
3. Crear usuario de base de datos
4. Whitelist IP: `0.0.0.0/0`
5. Obtener connection string

#### **2. Railway (Backend)**
1. Fork este repositorio
2. Conectar repositorio a [Railway](https://railway.app)
3. Configurar variables de entorno:
   ```bash
   MONGO_URL=tu-mongodb-atlas-url
   JWT_SECRET_KEY=tu-clave-secreta-jwt
   ```
4. Deploy automático ✅

#### **3. Vercel (Frontend)**
1. Conectar `frontend/` folder a [Vercel](https://vercel.com)
2. Configurar variable:
   ```bash
   REACT_APP_BACKEND_URL=https://tu-app.railway.app
   ```
3. Deploy automático ✅

## 🔑 **Primer Login**

Después del deploy exitoso, usa estas credenciales iniciales:

```
📧 Email: admin@registrovioleta.org
🔑 Contraseña: RegistroVioleta2025!
```

**⚠️ IMPORTANTE:** Cambiar contraseña después del primer login

## 🛠️ **Desarrollo Local**

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/registro-violeta.git
cd registro-violeta

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configurar variables en .env
uvicorn server:app --reload

# Frontend (en otra terminal)
cd ../frontend
npm install
npm start
```

## 🚨 **¿Problemas con el Login?**

Si no puedes iniciar sesión, consulta nuestra [**Guía de Troubleshooting**](TROUBLESHOOTING.md) que incluye:

- ✅ Verificaciones básicas
- 🔧 Diagnóstico paso a paso
- 🐛 Errores comunes y soluciones
- 📋 Checklist de deployment
- 🧪 Tests manuales

## 💰 Costos de Operación

### Tier Gratuito (Recomendado para fundaciones pequeñas)
- **Total: $0/mes**
- Hasta 25 usuarias activas
- 512MB base de datos
- 15GB almacenamiento Drive
- Ilimitadas sesiones y PDFs

### Tier Fundación ($15-20/mes)
- **Para fundaciones grandes**
- Usuarias ilimitadas
- 2GB base de datos
- 100GB almacenamiento Drive
- Funciones avanzadas de reportes

## 🎯 Beneficios

### Para las Fundaciones
- **Costo predecible y bajo**
- **Datos propios** (en su Google Drive)
- **Cumplimiento profesional** (formato oficial)
- **Backup automático** y seguro
- **Escalabilidad** según crecimiento

### Para las Profesionales
- **Interfaz intuitiva** y fácil de usar
- **Acceso móvil** para trabajo de campo
- **Generación automática** de documentos
- **Búsqueda rápida** de historiales
- **Confidencialidad garantizada**

### Para las Usuarias (Beneficiarias)
- **Privacidad total** (solo códigos)
- **Seguimiento profesional** estructurado
- **Continuidad** del proceso terapéutico
- **Documentación oficial** para procesos legales

## 🔒 Seguridad y Privacidad

### Principios de Protección de Datos
- **Solo códigos anónimos** - Nunca nombres reales
- **Encriptación en tránsito** - HTTPS/TLS
- **Segregación por fundación** - Datos aislados
- **Backup automático** - Google Drive Enterprise
- **Logs auditables** - Trazabilidad completa

### Cumplimiento
- Diseñado para cumplir con protección de datos
- Formato oficial para documentación legal
- Trazabilidad completa de accesos
- Backup y recuperación automatizada

## 🤝 Contribuir

### Para Desarrolladores
```bash
# Fork del repositorio
git fork https://github.com/abueloide/registro-violeta

# Crear rama para feature
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commit
git commit -am "Agregar nueva funcionalidad"

# Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

### Para Fundaciones
- Reportar bugs o sugerir mejoras
- Compartir casos de uso específicos
- Documentar mejores prácticas
- Pruebas beta de nuevas funciones

## 📞 Soporte

### Documentación
- [**Guía de Troubleshooting**](TROUBLESHOOTING.md) - Solución de problemas
- [Guía de Usuario Completa](docs/user-guide.md)
- [API Reference](docs/api-reference.md)

### Comunidad
- [Discussions](https://github.com/abueloide/registro-violeta/discussions) - Preguntas y sugerencias
- [Issues](https://github.com/abueloide/registro-violeta/issues) - Reportar bugs

### Soporte Prioritario
Para fundaciones que requieren soporte dedicado, configuración personalizada o capacitación del equipo, contactar para opciones de soporte premium.

## 📄 Licencia

Este proyecto está licenciado bajo MIT License - ver [LICENSE](LICENSE) para detalles.

### Uso Comercial
- ✅ Uso gratuito para fundaciones sin fines de lucro
- ✅ Modificación y distribución permitida
- ✅ Uso comercial permitido con atribución

---

## 🌟 ¿Por qué Registro Violeta?

**Registro Violeta** nace de la necesidad real de fundaciones que trabajan con mujeres víctimas de violencia de género. Combina:

- 💜 **Sensibilidad social** - Diseñado específicamente para este contexto
- 🔧 **Tecnología apropiada** - Potente pero accesible
- 💰 **Sostenibilidad económica** - Costos predecibles y bajos
- 🛡️ **Seguridad por diseño** - Privacidad y confidencialidad primero
- 📈 **Escalabilidad** - Crece con la organización

### Hecho con 💜 para quienes dedican su vida a sanar y acompañar

---

**💜 ¿Listo para digitalizar tu fundación?**

**⚡ Deploy en 5 minutos:**

1. **Backend:** [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/abueloide/registro-violeta&envs=MONGO_URL,JWT_SECRET_KEY&referralCode=_registro-violeta)

2. **Frontend:** [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/abueloide/registro-violeta/tree/main/frontend)

3. **MongoDB:** [Crear cuenta Atlas gratuita](https://mongodb.com/atlas)

4. **Login:** `admin@registrovioleta.org` / `RegistroVioleta2025!`

**¿Problemas?** 👉 [**Ver Troubleshooting**](TROUBLESHOOTING.md)
