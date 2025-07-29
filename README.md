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
- **Vercel** - Frontend (ilimitado gratuito)
- **Railway** - Backend ($5 crédito mensual gratis)
- **MongoDB Atlas** - Base de datos (512MB gratis)
- **Google Drive** - Almacenamiento (15GB gratis)

## 🚀 Instalación y Despliegue

### Opción 1: Despliegue Automático (Recomendado)

#### Backend en Railway
1. Fork este repositorio
2. Ir a [railway.app](https://railway.app)
3. "Deploy from GitHub" → Seleccionar tu fork
4. Configurar variables de entorno (ver `.env.example`)
5. Deploy automático ✅

#### Frontend en Vercel
1. Ir a [vercel.com](https://vercel.com)
2. "Import Git Repository" → Seleccionar `frontend/`
3. Build Command: `npm run build`
4. Deploy automático ✅

### Opción 2: Desarrollo Local

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

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# MongoDB
MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/registro_violeta

# JWT
JWT_SECRET_KEY=tu-clave-secreta-muy-segura

# Google Drive (Opcional pero recomendado)
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}

# Telegram Bot (Opcional)
TELEGRAM_BOT_TOKEN=tu-token-de-bot
TELEGRAM_AUTHORIZED_USERS=["123456789","987654321"]
```

### Configuración de Google Drive

1. Ir a [Google Cloud Console](https://console.cloud.google.com)
2. Crear proyecto nuevo
3. Habilitar Google Drive API
4. Crear Service Account
5. Descargar clave JSON
6. Pegar el contenido JSON en `GOOGLE_DRIVE_CREDENTIALS`

### Configuración del Bot de Telegram

1. Hablar con [@BotFather](https://t.me/botfather)
2. Crear bot: `/newbot`
3. Obtener token
4. Agregar token a variables de entorno
5. Agregar IDs de usuarios autorizados

## 📱 Uso del Sistema

### Para Terapeutas

1. **Crear Perfil de Usuaria**
   - Código anónimo (ej: MV-001)
   - Información básica sin datos personales
   - Asignación de terapeuta

2. **Registrar Sesión Terapéutica**
   - Formulario estructurado profesional
   - Objetivo, desarrollo, actividades, herramientas
   - Avances y cierre de sesión
   - Generación automática de PDF

3. **Bot de Telegram (Opcional)**
   - Enviar nota de voz mencionando código
   - Sistema transcribe y organiza automáticamente
   - Respaldo en Google Drive

### Para Administradores

1. **Dashboard Ejecutivo**
   - Estadísticas en tiempo real
   - Estado de servicios (DB, Drive, PDF)
   - Reportes por fundación

2. **Gestión de Usuarios**
   - Crear cuentas por rol
   - Asignar fundaciones
   - Control de acceso

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
- [Guía de Usuario Completa](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Guía de Despliegue](docs/deployment-guide.md)

### Comunidad
- [Discussions](https://github.com/abueloide/registro-violeta/discussions) - Preguntas y sugerencias
- [Issues](https://github.com/abueloide/registro-violeta/issues) - Reportar bugs
- Email: registro.violeta@fundacion.org

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

**¿Listo para digitalizar tu fundación?** 

[![Deploy Backend](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/abueloide/registro-violeta&envs=MONGO_URL,JWT_SECRET_KEY&referralCode=_registro-violeta)

[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/abueloide/registro-violeta/tree/main/frontend)
