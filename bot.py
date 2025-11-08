import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

# Загружаем переменные из .env
load_dotenv()

# Получаем ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с ИИ от DeepSeek. Напиши мне любой вопрос — и я постараюсь ответить."
    )

# Обработка обычных текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    logging.info(f"Пользователь {user_id} написал: {user_text}")

    # Формируем запрос к DeepSeek
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_text}],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
            response.raise_for_status()  # вызовет ошибку при 4xx/5xx
            data = response.json()
            ai_reply = data["choices"][0]["message"]["content"].strip()
            await update.message.reply_text(ai_reply)
    except Exception as e:
        logging.error(f"Ошибка DeepSeek: {e}")
        await update.message.reply_text(
            "❌ Не удалось получить ответ от ИИ. Проверьте API-ключ или попробуйте позже."
        )

# Запуск бота
def main():
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        raise ValueError("❌ Отсутствует TELEGRAM_BOT_TOKEN или DEEPSEEK_API_KEY в .env!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен и ждёт сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
