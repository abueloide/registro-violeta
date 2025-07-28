# Registro Violeta

**Registro Violeta** es una herramienta digital diseñada para organizaciones que apoyan a mujeres víctimas de violencia. Permite registrar notas de voz terapéuticas o de acompañamiento legal vía Telegram, transcribirlas automáticamente, organizarlas por caso y almacenarlas de manera segura.

Su enfoque es **confidencial, accesible y humano**: busca facilitar el trabajo de psicólogas, abogadas y trabajadoras sociales que no siempre tienen tiempo para capturar notas estructuradas.

---

## 🎯 Funcionalidades

- Envío de **nota de voz** vía Telegram.
- Transcripción automática usando IA.
- Estructuración del contenido en secciones útiles (objetivo, avances, tareas).
- Almacenamiento en **Google Sheet** y **Drive** (por código de usuaria).
- Preparado para análisis posterior por abogadas o supervisoras.

---

## 🛠️ Tecnologías usadas

- Python 3.10+
- Telegram Bot API
- Whisper (OpenAI) o alternativa local
- Google Drive + Sheets API
- Google Cloud o Firebase (opcional)
- Posible despliegue en Replit / Railway

---

## 🛡️ Principios clave

- **Privacidad:** solo se usan códigos de usuaria, sin nombres reales.
- **Accesibilidad:** se opera desde Telegram, sin apps adicionales.
- **Costo mínimo:** diseñado para ONGs con recursos limitados.
- **Enfoque social:** pensado para situaciones de violencia de género.

---

## 📦 Instalación rápida

1. Clona el repositorio
2. Crea un archivo `.env` con tus claves
3. Instala dependencias:

```bash
pip install -r requirements.txt
