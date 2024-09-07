import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from tokens import TG_BOT_API_KEY, HFT_API_KEY

TOKEN = TG_BOT_API_KEY

HUGGINGFACE_API_KEY = HFT_API_KEY
API_URL = "https://api-inference.huggingface.co/models/gpt2"

def query_huggingface(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data[0]["generated_text"]
    else:
        return "Произошла ошибка при обращении к Hugging Face API."

menu_keyboard = [
    ["Студент", "IT-технології"],
    ["Контакти", "Prompt ChatGPT"]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Вітаю! Оберіть пункт меню:",
        reply_markup=menu_markup
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "Студент":
        await update.message.reply_text("ПІБ: Сенюк Єгор Олександрович, Група: ІО-11")
    elif text == "IT-технології":
        await update.message.reply_text("Основи WEB-технологій")
    elif text == "Контакти":
        await update.message.reply_text("Телефон: +380933724700, E-mail: seniuk.yehor@gmail.com")
    elif text == "Prompt ChatGPT":
        await update.message.reply_text("Напишіть запит до ChatGPT:")
        context.user_data['awaiting_prompt'] = True
    elif context.user_data.get('awaiting_prompt'):
        context.user_data['awaiting_prompt'] = False
        await update.message.reply_text("Отримую відповідь від ChatGPT...")

        response = query_huggingface(text)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Будь ласка, оберіть пункт меню.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    application.run_polling()
