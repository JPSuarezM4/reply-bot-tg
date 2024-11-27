import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import ALL

# Lista para almacenar mensajes del grupo origen
MESSAGE_QUEUE = []

# Reemplaza con el ID del chat o grupo destino
DESTINATION_CHAT_IDS = ["-4797802524", "-1002163091334"]


# Función para manejar mensajes del grupo origen y almacenarlos
async def handle_message(update: Update, context: CallbackContext) -> None:
    MESSAGE_QUEUE.append((update.message.chat_id, update.message.message_id))

# Función para enviar mensajes en lotes de 5 cada 30 segundos
async def send_scheduled_messages(context: CallbackContext) -> None:
    while True:
        if MESSAGE_QUEUE:
            for _ in range(5):  # Enviar 5 mensajes en cada iteración
                if MESSAGE_QUEUE:
                    from_chat_id, message_id = MESSAGE_QUEUE.pop(0)  # Obtener el mensaje más antiguo
                    for chat_id in DESTINATION_CHAT_IDS:  # Enviar a todos los grupos destino
                        await context.bot.copy_message(
                            chat_id=chat_id,
                            from_chat_id=from_chat_id,
                            message_id=message_id
                        )
        await asyncio.sleep(30)  # Esperar 30 segundos antes del siguiente lote

# Comando /start para inicializar el bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Estoy listo para programar el envío de mensajes.")

# Función principal
def main():
    TOKEN = "7833929400:AAE-MZNd7XwaHibg76kNcacTG2-FRfIr4B0"  # Reemplaza con el token de tu bot

    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()

    # Inicializar la JobQueue
    job_queue = application.job_queue

    # Agregar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(ALL, handle_message))  # Escucha todos los mensajes

    # Programar el envío de mensajes
    job_queue.run_repeating(send_scheduled_messages, interval=30, first=1)  # Cada 30 segundos, iniciar en 1 seg

    # Ejecutar el bot
    print("Bot iniciado...")
    application.run_polling()


if __name__ == '__main__':
    main()
