import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8794958180:AAF_osdS0l1nzMpr-njvfL8RQxcG076vxPA"
ADMIN_CHAT_ID = "1918804688"
CHANNEL_ID = "@zeno_X_shop"

CHOOSING_CAT, CHOOSING_PACK, ENTERING_GAME_ID, SENDING_RECEIPT, SENDING_POST = range(5)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Diamond ဝယ်ယူရန်'], ['📢 Channel သို့ Post တင်ရန် (Admin)']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 မင်္ဂလာပါရှင်။ Zeno X Shop မှ ကြိုဆိုပါတယ်။", reply_markup=reply_markup)

async def buy_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Weekly Pass (WP)", callback_data='cat_wp')],
        [InlineKeyboardButton("🔥 Double Dia (နှစ်ဆ)", callback_data='cat_double')],
        [InlineKeyboardButton("💎 Normal Diamonds", callback_data='cat_normal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 ဝယ်ယူလိုသည့် အမျိုးအစားကို ရွေးချယ်ပေးပါ-", reply_markup=reply_markup)
    return CHOOSING_CAT

async def cat_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.split('_')[1]
    context.user_data['category'] = cat
    keyboard = []
    if cat == 'wp':
        keyboard = [[InlineKeyboardButton("🎫 5WP - 6,700 ks", callback_data='pk_5WP_6700ks')]]
    elif cat == 'double':
        packs = [("50+Dia", "4100"), ("150+Dia", "12000"), ("250+Dia", "17500"), ("500+Dia", "34000")]
        for name, price in packs:
            keyboard.append([InlineKeyboardButton(f"🎁 {name} - {price} ks", callback_data=f'pk_{name}_{price}')])
    elif cat == 'normal':
        packs = [("86Dia", "5700"), ("172Dia", "11500"), ("257Dia", "16500"), ("343Dia", "22000")]
        for name, price in packs:
            keyboard.append([InlineKeyboardButton(f"💎 {name} - {price} ks", callback_data=f'pk_{name}_{price}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔹 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပေးပါ-", reply_markup=reply_markup)
    return CHOOSING_PACK

async def pack_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, pack_name, pack_price = query.data.split('_')
    context.user_data['pack_name'] = pack_name
    context.user_data['pack_price'] = pack_price
    await query.edit_message_text(text=f"📋 ရွေးချယ်ထားသည်: {pack_name} ({pack_price} ks)\n\n👉 Game ID နှင့် Server ID ကို ရိုက်ထည့်ပေးပါ-")
    return ENTERING_GAME_ID

async def game_id_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['game_id'] = update.message.text
    await update.message.reply_text("⚠️ ငွေလွှဲပြီးပါက ပြေစာ (Screenshot) ကို ပို့ပေးပါရှင်။")
    return SENDING_RECEIPT

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    cat_title = context.user_data.get('category', 'N/A')
    order_text = f"🚨 ORDER အသစ်!\n\nဝယ်သူ: {update.message.from_user.first_name}\nအမျိုးအစား: {cat_title}\nပမာဏ: {context.user_data['pack_name']}\nဈေး: {context.user_data['pack_price']}\nGame ID: {context.user_data['game_id']}"
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file, caption=order_text)
    await update.message.reply_text("✅ Order ကို လက်ခံရရှိပါပြီရှင်။")
    return ConversationHandler.END

async def admin_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📢 Channel တွင်တင်ရန် စာကို ရိုက်ထည့်ပေးပါ-")
    return SENDING_POST

async def admin_post_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHANNEL_ID, text=update.message.text)
    await update.message.reply_text("✅ Post တင်ပြီးပါပြီ။")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    buy_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Diamond ဝယ်ယူရန်$'), buy_diamond)],
        states={
            CHOOSING_CAT: [CallbackQueryHandler(cat_chosen)],
            CHOOSING_PACK: [CallbackQueryHandler(pack_chosen)],
            ENTERING_GAME_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_id_entered)],
            SENDING_RECEIPT: [MessageHandler(filters.PHOTO, receipt_received)],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )
    post_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📢 Channel သို့ Post တင်ရန် \(Admin\)$'), admin_post_start)],
        states={SENDING_POST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_post_send)]},
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(buy_conv)
    app.add_handler(post_conv)
    app.run_polling()

if __name__ == '__main__':
    main()
