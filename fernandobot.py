import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from telegram.ext import ChatMemberHandler

# Lista para almacenar los mensajes del grupo origen y los destinos
MESSAGE_QUEUE = []
DESTINATION_CHAT_IDS = []
ORIGIN_CHAT_ID = None  # Variable para almacenar el ID del grupo origen

# Función para manejar mensajes del grupo origen y almacenarlos
async def handle_message(update: Update, context: CallbackContext) -> None:
    if ORIGIN_CHAT_ID == update.message.chat.id:  # Solo procesar mensajes del grupo origen
        MESSAGE_QUEUE.append((update.message.chat.id, update.message.message_id))

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

# Función para manejar cuando el bot es agregado a un nuevo grupo
async def new_chat_member(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    if chat_id not in DESTINATION_CHAT_IDS and chat_id != ORIGIN_CHAT_ID:
        DESTINATION_CHAT_IDS.append(chat_id)  # Agregar el ID del grupo a la lista de destinos
        await update.message.reply_text(f"Este grupo ha sido agregado como destino. ID: {chat_id}")

# Comando /origen para establecer el grupo origen
async def set_origin(update: Update, context: CallbackContext) -> None:
    global ORIGIN_CHAT_ID
    ORIGIN_CHAT_ID = update.message.chat.id
    await update.message.reply_text(f"Este grupo ha sido establecido como el grupo origen. ID: {ORIGIN_CHAT_ID}")

# Comando /destino para agregar el grupo destino
async def add_destination(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    if chat_id != ORIGIN_CHAT_ID and chat_id not in DESTINATION_CHAT_IDS:
        DESTINATION_CHAT_IDS.append(chat_id)
        await update.message.reply_text(f"Este grupo ha sido agregado como destino. ID: {chat_id}")
    else:
        await update.message.reply_text(f"Este grupo ya es el origen o ya está en la lista de destinos.")

# Comando /start para inicializar el bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Estoy listo para programar el envío de mensajes. Usa /origen para establecer el grupo origen y /destino para agregar grupos destino.")

# Función principal
def main():
    TOKEN = "7833929400:AAE-MZNd7XwaHibg76kNcacTG2-FRfIr4B0"  # Reemplaza con el token de tu bot

    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()

    # Inicializar la JobQueue
    job_queue = application.job_queue

    # Agregar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("origen", set_origin))  # Comando para establecer el origen
    application.add_handler(CommandHandler("destino", add_destination))  # Comando para agregar destinos
    application.add_handler(MessageHandler(filters.ALL, handle_message))  # Escucha todos los mensajes
    application.add_handler(ChatMemberHandler(new_chat_member, ChatMemberHandler.CHAT_MEMBER))  # Detecta cuando el bot se une a un grupo

    # Programar el envío de mensajes
    job_queue.run_repeating(send_scheduled_messages, interval=30, first=1)  # Cada 30 segundos, iniciar en 1 seg

    # Ejecutar el bot
    print("Bot iniciado...")
    application.run_polling()

if __name__ == '__main__':
    main()
