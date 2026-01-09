"""
Manejador de Telegram para Multibot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

logger = logging.getLogger(__name__)

class TelegramMultibot:
    def __init__(self):
        self.token = None
        self.application = None
        self.core = None
        
    async def start(self):
        """Inicia el bot de Telegram"""
        from core.config import settings
        
        self.token = settings.MULTIBOT_TELEGRAM_TOKEN
        if not self.token:
            logger.warning("Token de Telegram no configurado para Multibot")
            return False
        
        # Importar core
        from .core import MultibotCore
        self.core = MultibotCore()
        await self.core.start()
        
        # Configurar aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Manejadores
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("stats", self.handle_stats))
        self.application.add_handler(CommandHandler("modules", self.handle_modules))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Iniciar polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("✅ Telegram Multibot iniciado")
        return True
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /start"""
        user = update.effective_user
        message = await self.core.welcome_message(str(user.id))
        
        keyboard = [
            [InlineKeyboardButton("📊 Estadísticas", callback_data='stats')],
            [InlineKeyboardButton("🛠️ Módulos", callback_data='modules')],
            [InlineKeyboardButton("🚀 Comenzar", callback_data='start_bot')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /help"""
        help_text = """
🤖 *AYUDA MULTIBOT*

*Comandos principales:*
• /start - Inicia el bot
• /help - Muestra esta ayuda
• /stats - Ver estadísticas
• /modules - Listar módulos

*Funciones avanzadas:*
• Generación de contenido
• Programación de tareas
• Análisis de datos
• Gestión de usuarios

*Soporte:* @tu_soporte
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /stats"""
        stats = await self.core.show_stats(str(update.effective_user.id))
        await update.message.reply_text(stats, parse_mode='Markdown')
    
    async def handle_modules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /modules"""
        modules = await self.core.list_modules(str(update.effective_user.id))
        await update.message.reply_text(modules, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks de botones"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'stats':
            stats = await self.core.show_stats(str(query.from_user.id))
            await query.edit_message_text(stats, parse_mode='Markdown')
        elif query.data == 'modules':
            modules = await self.core.list_modules(str(query.from_user.id))
            await query.edit_message_text(modules, parse_mode='Markdown')
