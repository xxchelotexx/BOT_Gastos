import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from sheets import append_row
from parser_ai import parse_message

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto entrantes."""
    text = update.message.text
    await process_input(update, text)


async def process_input(update: Update, text: str):
    """Procesa el texto, lo parsea y lo guarda en Google Sheets."""
    data = parse_message(text)

    if not data:
        await update.message.reply_text(
            "❌ No pude interpretar el mensaje.\n"
            "Formato esperado: *Nombre, Categoría, Producto, Precio*\n"
            "Ejemplo: `Marcelo, Mercado, Banana, 5Bs`",
            parse_mode="Markdown"
        )
        return

    try:
        append_row(data)

        await update.message.reply_text(
            f"✅ *Registro guardado*\n\n"
            f"👤 Nombre: {data['nombre']}\n"
            f"📂 Categoría: {data['categoria']}\n"
            f"🛒 Producto: {data['producto']}\n"
            f"💰 Precio: {data['precio']}\n"
            f"📅 Fecha: {data['fecha']}\n"
            f"🕐 Hora: {data['hora']}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error al guardar en Google Sheets: {e}")
        await update.message.reply_text(
            "❌ Error al guardar en la hoja de cálculo."
        )


def main():
    # Obtener token de variables de entorno
    token = os.getenv("TELEGRAM_TOKEN")
    
    if not token:
        logger.error("No se encontró la variable de entorno TELEGRAM_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()

    # Solo registramos el manejador de texto
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    logger.info("Bot iniciado (Solo texto)...")
    
    # He bajado el poll_interval a un valor más estándar (1.0), 
    # 60 segundos era demasiado lento para responder.
    app.run_polling(poll_interval=10)


if __name__ == "__main__":
    main()