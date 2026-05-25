import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

# သင့်ရဲ့ Token ကို အောက်ပါအတိုင်း ထည့်ပေးထားပါတယ်
TOKEN = "8794958180:AAFkkpuznWjQZvBBj-PuLkWxOFBeoxq8qAY"
ADMIN_CHAT_ID = "1918804688"
CHANNEL_ID = "@zeno_X_shop"

CHOOSING_CAT, CHOOSING_PACK, ENTERING_GAME_ID = range(3)

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

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_CAT: [MessageHandler(filters.Text(['Diamond ဝယ်ယူရန်']), buy_diamond)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
