import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
from pymongo import MongoClient
from bson import ObjectId
import asyncio

# Importar servicios
from services.drive_service import drive_service
from services.pdf_service import pdf_service

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.mongo_url = os.getenv('MONGO_URL')
        self.authorized_users = self.load_authorized_users()
        
        # Conexión a MongoDB
        self.client = MongoClient(self.mongo_url)
        self.db = self.client.registro_violeta
        self.users_collection = self.db.users
        self.sessions_collection = self.db.sessions
        self.voice_notes_collection = self.db.voice_notes
        
        # Inicializar aplicación
        self.application = None
        if self.token:
            self.application = Application.builder().token(self.token).build()
            self.setup_handlers()
    
    def load_authorized_users(self):
        """Cargar lista de usuarios autorizados desde variable de entorno"""
        users_json = os.getenv('TELEGRAM_AUTHORIZED_USERS', '[]')
        try:
            return json.loads(users_json)
        except json.JSONDecodeError:
            logger.warning("Invalid TELEGRAM_AUTHORIZED_USERS format")
            return []
    
    def is_user_authorized(self, user_id):
        """Verificar si el usuario está autorizado"""
        return str(user_id) in [str(u) for u in self.authorized_users]
    
    def setup_handlers(self):
        """Configurar manejadores del bot"""
        if not self.application:
            return
        
        # Comandos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Mensajes de voz
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        
        # Mensajes de texto con códigos de usuaria
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        
        if not self.is_user_authorized(user_id):
            await update.message.reply_text(
                "❌ No tienes autorización para usar este bot.\n"
                "Contacta al administrador del sistema."
            )
            return
        
        welcome_message = (
            "🟣 *Registro Violeta Bot*\n\n"
            "¡Hola! Soy tu asistente para registro rápido de notas terapéuticas.\n\n"
            "*¿Cómo usarme?*\n"
            "• Envía una nota de voz con tus observaciones\n"
            "• Menciona el código de usuaria (ej: MV-001)\n"
            "• Automáticamente transcribiré y organizaré la información\n\n"
            "*Comandos disponibles:*\n"
            "/help - Ver esta ayuda\n"
            "/stats - Ver estadísticas\n\n"
            "_Recuerda: Usa siempre códigos, nunca nombres reales._"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        if not self.is_user_authorized(update.effective_user.id):
            return
        
        help_message = (
            "🔧 *Ayuda - Registro Violeta Bot*\n\n"
            "*Notas de voz:*\n"
            "1. Graba tu nota de voz\n"
            "2. Menciona el código de usuaria\n"
            "3. Describe brevemente la sesión o observación\n\n"
            "*Ejemplo de nota de voz:*\n"
            "\"Código MV-001, sesión de seguimiento del 15 de enero. "
            "La usuaria mostró avances en manejo de ansiedad. "
            "Se aplicaron técnicas de respiración.\"\n\n"
            "*Notas de texto:*\n"
            "También puedes enviar notas escritas mencionando el código.\n\n"
            "*¿Problemas?*\n"
            "Contacta al administrador del sistema."
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats"""
        if not self.is_user_authorized(update.effective_user.id):
            return
        
        try:
            # Obtener usuario del sistema
            telegram_user_id = str(update.effective_user.id)
            system_user = self.users_collection.find_one({"telegram_user_id": telegram_user_id})
            
            if not system_user:
                await update.message.reply_text(
                    "❌ No estás vinculado a ningún usuario del sistema.\n"
                    "Contacta al administrador."
                )
                return
            
            # Contar notas de voz del usuario
            voice_notes_count = self.voice_notes_collection.count_documents({
                "telegram_user_id": telegram_user_id
            })
            
            # Contar sesiones del usuario
            sessions_count = self.sessions_collection.count_documents({
                "created_by": str(system_user["_id"])
            })
            
            stats_message = (
                f"📊 *Tus estadísticas*\n\n"
                f"🎙️ Notas de voz enviadas: {voice_notes_count}\n"
                f"📝 Sesiones registradas: {sessions_count}\n"
                f"👤 Usuario: {system_user.get('nombre', 'No disponible')}\n"
                f"🏢 Fundación: {system_user.get('fundacion', 'No disponible')}"
            )
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await update.message.reply_text("❌ Error obteniendo estadísticas.")
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar mensajes de voz"""
        if not self.is_user_authorized(update.effective_user.id):
            await update.message.reply_text("❌ No autorizado.")
            return
        
        try:
            await update.message.reply_text("🎙️ Procesando nota de voz...")
            
            # Obtener información del mensaje de voz
            voice = update.message.voice
            file = await context.bot.get_file(voice.file_id)
            
            # Descargar archivo de voz
            voice_data = await file.download_as_bytearray()
            
            # TODO: Implementar transcripción con Whisper local
            # Por ahora, guardamos la información básica
            
            voice_note = {
                "telegram_user_id": str(update.effective_user.id),
                "telegram_message_id": update.message.message_id,
                "file_id": voice.file_id,
                "duration": voice.duration,
                "file_size": voice.file_size,
                "created_at": datetime.utcnow(),
                "processed": False,
                "transcription": None,  # Se llenará cuando se implemente Whisper
                "codigo_usuaria": None,  # Se extraerá de la transcripción
                "fundacion": None
            }
            
            # Guardar en MongoDB
            result = self.voice_notes_collection.insert_one(voice_note)
            
            await update.message.reply_text(
                "✅ Nota de voz guardada correctamente.\n"
                "🔄 La transcripción se procesará en breve.\n\n"
                "_ID de nota: " + str(result.inserted_id) + "_",
                parse_mode='Markdown'
            )
            
            logger.info(f"Voice note saved with ID: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await update.message.reply_text("❌ Error procesando la nota de voz.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar mensajes de texto con notas rápidas"""
        if not self.is_user_authorized(update.effective_user.id):
            return
        
        try:
            text = update.message.text
            
            # Buscar códigos de usuaria en el mensaje (formato: XXX-###)
            import re
            codigo_pattern = r'\b[A-Z]{1,3}-\d{3}\b'
            codigos = re.findall(codigo_pattern, text.upper())
            
            if not codigos:
                await update.message.reply_text(
                    "ℹ️ No detecté ningún código de usuaria válido.\n"
                    "Formato esperado: MV-001, CV-002, etc."
                )
                return
            
            # Obtener usuario del sistema
            telegram_user_id = str(update.effective_user.id)
            system_user = self.users_collection.find_one({"telegram_user_id": telegram_user_id})
            
            if not system_user:
                await update.message.reply_text(
                    "❌ No estás vinculado a ningún usuario del sistema."
                )
                return
            
            # Guardar nota de texto
            text_note = {
                "telegram_user_id": telegram_user_id,
                "telegram_message_id": update.message.message_id,
                "content": text,
                "codigos_usuaria": codigos,
                "fundacion": system_user.get("fundacion"),
                "created_by": str(system_user["_id"]),
                "created_at": datetime.utcnow(),
                "type": "text_note"
            }
            
            result = self.voice_notes_collection.insert_one(text_note)
            
            await update.message.reply_text(
                f"✅ Nota guardada para: {', '.join(codigos)}\n"
                f"📝 {len(text)} caracteres registrados\n\n"
                f"_ID: {str(result.inserted_id)}_",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("❌ Error procesando la nota de texto.")
    
    async def run_bot(self):
        """Ejecutar el bot"""
        if not self.application:
            logger.error("Bot not initialized - missing token")
            return
        
        logger.info("Starting Telegram bot...")
        
        # Configurar webhook o polling según el entorno
        if os.getenv('WEBHOOK_URL'):
            # Modo webhook para producción
            webhook_url = os.getenv('WEBHOOK_URL')
            await self.application.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv('PORT', 8080)),
                webhook_url=webhook_url
            )
        else:
            # Modo polling para desarrollo
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Instancia global del bot
telegram_bot = TelegramBot()

# Función para ejecutar el bot como servicio independiente
async def main():
    """Función principal para ejecutar el bot"""
    await telegram_bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())
