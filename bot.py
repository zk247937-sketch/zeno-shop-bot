import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# သင့်ရဲ့ Token ကို အောက်ပါအတိုင်း ထည့်ပေးထားပါတယ်
TOKEN = "8794958180:AAFkkpuznWjQZvBBj-PuLkWxOFBeoxq8qAY"
ADMIN_CHAT_ID = "1918804688"
CHANNEL_ID = "@zeno_X_shop"

CHOOSING_CAT = 1

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Diamond ဝယ်ယူရန်'], ['📣 Channel သို့ Post တင်ရန် (Admin)']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 မင်္ဂလာပါရှင်။ Zeno X Shop မှ ကြိုဆိုပါတယ်။", reply_markup=reply_markup)
    return CHOOSING_CAT

async def buy_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Weekly Pass", callback_data='weekly')],
        [InlineKeyboardButton("🔥 Double Diamond", callback_data='double')],
        [InlineKeyboardButton("💎 Normal Diamond", callback_data='normal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("💎 Diamond ပက်ကေ့ခ်ျတစ်ခုကို ရွေးချယ်ပါ -", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Diamond ဝယ်ယူရန်':
        await buy_diamond(update, context)
    elif text == '📣 Channel သို့ Post တင်ရန် (Admin)':
        await update.message.reply_text("Channel မှာ တင်ချင်တဲ့ စာကို ရိုက်ထည့်ပေးပါ-")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
