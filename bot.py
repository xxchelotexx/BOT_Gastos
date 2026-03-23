import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from sheets import append_row
from parser_ai import parse_message
from voice import transcribe_voice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await process_input(update, text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    # Crear carpeta temp_audio si no existe
    os.makedirs("temp_audio", exist_ok=True)

    file_path = os.path.join("temp_audio", f"{voice.file_id}.ogg")

    # Descargar audio
    await file.download_to_drive(file_path)

    # Transcribir audio
    text = transcribe_voice(file_path)

    if not text:
        await update.message.reply_text(
            "❌ No pude transcribir el mensaje de voz. Intenta de nuevo."
        )
        return

    await update.message.reply_text(
        f"🎙️ Transcripción: _{text}_",
        parse_mode="Markdown"
    )

    await process_input(update, text)


async def process_input(update: Update, text: str):
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
    token = os.environ["TELEGRAM_TOKEN"]

    app = ApplicationBuilder().token(token).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    app.add_handler(
        MessageHandler(filters.VOICE, handle_voice)
    )

    logger.info("Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()