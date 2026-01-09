"""
Telegram Bot para Afiliados
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

logger = logging.getLogger(__name__)

class AffiliateTelegramBot:
    def __init__(self, hotmart_client):
        self.token = None
        self.application = None
        self.hotmart = hotmart_client
        self.affiliate_core = None
        
    async def start(self):
        """Inicia el bot de Telegram para afiliados"""
        from core.config import settings
        
        self.token = settings.AFFILIATE_TELEGRAM_TOKEN
        if not self.token:
            logger.warning("Token de Telegram no configurado para Afiliados")
            return False
        
        # Importar core
        from .core import AffiliateBot
        self.affiliate_core = AffiliateBot(self.hotmart)
        await self.affiliate_core.start()
        
        # Configurar aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Manejadores
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("afiliados", self.handle_affiliates))
        self.application.add_handler(CommandHandler("dashboard", self.handle_dashboard))
        self.application.add_handler(CommandHandler("productos", self.handle_products))
        self.application.add_handler(CommandHandler("comisiones", self.handle_commissions))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Iniciar polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("✅ Telegram Bot Afiliados iniciado")
        return True
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /start para afiliados"""
        welcome_text = """
💰 *BOT AFILIADOS NEURAFORGE*

¡Bienvenido al sistema de afiliados con Hotmart!

*Comandos disponibles:*
• /afiliados - Información afiliados
• /dashboard - Tu panel de control
• /productos - Productos disponibles
• /comisiones - Ver comisiones

*Gana comisiones promocionando:*
✅ Cursos digitales
✅ Plantillas profesionales
✅ Software AI
✅ Ebooks exclusivos

*Comisiones desde 30% hasta 70%*
"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Convertirme en Afiliado", callback_data='become_affiliate')],
            [InlineKeyboardButton("📊 Ver Dashboard", callback_data='dashboard')],
            [InlineKeyboardButton("🛒 Ver Productos", callback_data='products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_affiliates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /afiliados"""
        affiliate_info = """
🤝 *PROGRAMA DE AFILIADOS*

*Beneficios:*
• Comisiones altas (30%-70%)
• Links de seguimiento
• Dashboard en tiempo real
• Pagos semanales
• Soporte dedicado

*Cómo funciona:*
1. Te registras como afiliado
2. Obtienes links únicos
3. Compartes productos
4. Ganas comisiones por cada venta
5. Retiras tus ganancias

*Requisitos:*
✅ Tener audiencia digital
✅ Seguir políticas de Hotmart
✅ Promover honestamente

*¡Gana hasta $5,000 mensuales!*
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Registrarme", callback_data='register_affiliate')],
            [InlineKeyboardButton("📚 Políticas", callback_data='policies')],
            [InlineKeyboardButton("❓ Preguntas Frecuentes", callback_data='faq')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            affiliate_info,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /dashboard"""
        user_id = str(update.effective_user.id)
        
        # Obtener datos del dashboard
        dashboard_data = await self.affiliate_core.get_dashboard_data(user_id)
        
        dashboard_text = f"""
📊 *TU DASHBOARD DE AFILIADO*

*Resumen General:*
• Ventas totales: {dashboard_data['total_sales']}
• Comisión total: ${dashboard_data['total_commission']:.2f}
• Pago pendiente: ${dashboard_data['pending_payout']:.2f}
• Tasa conversión: {dashboard_data['conversion_rate']}

*Productos más vendidos:*
"""
        for product in dashboard_data['top_products']:
            dashboard_text += f"• {product['product']}: {product['sales']} ventas (${product['commission']:.2f})\n"
        
        dashboard_text += f"""
*Rendimiento:*
• Hoy: {dashboard_data['performance']['today']['sales']} ventas (${dashboard_data['performance']['today']['commission']:.2f})
• Semana: {dashboard_data['performance']['week']['sales']} ventas (${dashboard_data['performance']['week']['commission']:.2f})
• Mes: {dashboard_data['performance']['month']['sales']} ventas (${dashboard_data['performance']['month']['commission']:.2f})

*Próximo pago:* Semanal
"""
        keyboard = [
            [InlineKeyboardButton("🔄 Actualizar", callback_data='refresh_dashboard')],
            [InlineKeyboardButton("📈 Ver Detalles", callback_data='details')],
            [InlineKeyboardButton("💳 Retirar Fondos", callback_data='withdraw')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            dashboard_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /productos"""
        products_text = """
🛒 *PRODUCTOS DISPONIBLES*

*Categorías principales:*

🤖 *Inteligencia Artificial*
• Curso Completo de IA - $297 (50% comisión)
• Bot Builder Pro - $197 (40% comisión)
• Plantillas AI - $97 (60% comisión)

💼 *Marketing Digital*
• Master en Facebook Ads - $397 (35% comisión)
• Estrategias TikTok - $247 (45% comisión)
• Email Marketing Pro - $147 (50% comisión)

🎨 *Diseño & Creatividad*
• Photoshop desde Cero - $197 (40% comisión)
• Figma para Negocios - $147 (50% comisión)
• Plantillas Canva - $67 (70% comisión)

*Precios en USD - Comisiones sobre venta bruta*
"""
        
        keyboard = [
            [InlineKeyboardButton("🤖 Ver Cursos IA", callback_data='category_ai')],
            [InlineKeyboardButton("💼 Marketing", callback_data='category_marketing')],
            [InlineKeyboardButton("🎨 Diseño", callback_data='category_design')],
            [InlineKeyboardButton("🔗 Obtener Links", callback_data='get_links')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            products_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_commissions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja /comisiones"""
        commissions_text = """
💰 *SISTEMA DE COMISIONES*

*Niveles de Afiliado:*

🥉 *Standard (30% comisión)*
• Requisito: 0 ventas
• Beneficios: Acceso básico
• Soporte: Email

🥈 *Premium (50% comisión)*
• Requisito: 10+ ventas
• Beneficios: Links personalizados
• Soporte: Telegram prioritario

🥇 *VIP (70% comisión)*
• Requisito: 50+ ventas
• Beneficios: Mentoría personal
• Soporte: 24/7 directo

*Ejemplos de ganancias:*

Producto de $100:
• Standard: $30 por venta
• Premium: $50 por venta  
• VIP: $70 por venta

*Promociones especiales:*
🎯 Bono por primera venta: +$20
🔥 Bono mensual por volumen
👥 Bono por referir afiliados

*Pagos:* Cada semana via PayPal/Payoneer
"""
        
        await update.message.reply_text(
            commissions_text,
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'become_affiliate':
            await query.edit_message_text(
                "📝 *REGISTRO DE AFILIADO*\n\n"
                "Para registrarte como afiliado:\n"
                "1. Visita: https://affiliates.hotmart.com\n"
                "2. Busca 'NeuraForge AI'\n"
                "3. Completa el formulario\n"
                "4. Te enviaremos acceso en 24h\n\n"
                "O escribe a: afiliados@neuraforge.ai",
                parse_mode='Markdown'
            )
        elif query.data == 'dashboard':
            await self.handle_dashboard(
                Update(update_id=update.update_id, message=query.message),
                context
            )
        elif query.data == 'get_links':
            user_id = str(query.from_user.id)
            
            # Generar link de ejemplo
            link_data = await self.affiliate_core.generate_affiliate_link(
                product_id="curso-ia-pro",
                affiliate_id=user_id
            )
            
            await query.edit_message_text(
                f"🔗 *TU LINK DE AFILIADO*\n\n"
                f"*Producto:* Curso IA Pro\n"
                f"*Tu link:* {link_data['short_link']}\n"
                f"*Link completo:* {link_data['link']}\n\n"
                f"*Código de seguimiento:* {link_data['hash']}\n\n"
                f"¡Comparte este link y gana comisiones!",
                parse_mode='Markdown'
            )
