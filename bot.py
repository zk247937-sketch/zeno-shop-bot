import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8794958180:AAHLxydQggyH4BCZUiMQj-EmAysWngdxGW8"
ADMIN_CHAT_ID = "1918804688"
CHANNEL_ID = "@zeno_X_shop"

CHOOSING_CAT, CHOOSING_PACK, ENTERING_GAME_ID, SENDING_RECEIPT, SENDING_POST = range(5)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Diamond ဝယ်ယူရန်'], ['📢 Channel သို့ Post တင်ရန် (Admin)']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 မင်္ဂလာပါရှင်။ Zeno X Shop မှ ကြိုဆိုပါတယ်။\nအောက်က Menu ကိုနှိပ်ပြီး စိတ်ကြိုက် ဝယ်ယူနိုင်ပါတယ်ရှင်။",
        reply_markup=reply_markup
    )

async def buy_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Weekly Pass (WP)", callback_query_data='cat_wp')],
        [InlineKeyboardButton("🔥 Double Dia (နှစ်ဆ)", callback_query_data='cat_double')],
        [InlineKeyboardButton("💎 Normal Diamonds", callback_query_data='cat_normal')]
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
        keyboard = [[InlineKeyboardButton("🎫 5WP - 6,700 ks", callback_query_data='pk_5WP_6700ks')]]
    elif cat == 'double':
        packs = [("50+ Dia", "4,100"), ("150+ Dia", "12,000"), ("250+ Dia", "17,500"), ("500+ Dia", "34,000")]
        for name, price in packs:
            keyboard.append([InlineKeyboardButton(f"🎁 {name} - {price} ks", callback_query_data=f'pk_{name}_{price}ks')])
    elif cat == 'normal':
        packs = [
            ("86 Dia", "5,700"), ("172 Dia", "11,500"), ("257 Dia", "16,500"), ("343 Dia", "22,000"),
            ("429 Dia", "26,500"), ("514 Dia", "32,000"), ("600 Dia", "36,500"), ("706 Dia", "42,500"),
            ("878 Dia", "53,000"), ("963 Dia", "59,000"), ("1049 Dia", "62,500"), ("1135 Dia", "68,500"),
            ("1412 Dia", "84,000"), ("2195 Dia", "130,000"), ("3688 Dia", "210,000"), ("5532 Dia", "312,000"),
            ("9288 Dia", "515,000")
        ]
        for name, price in packs:
            keyboard.append([InlineKeyboardButton(f"💎 {name} - {price} ks", callback_query_data=f'pk_{name}_{price}ks')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔹 ဝယ်ယူလိုသည့် ပမာဏကို ရွေးချယ်ပေးပါ-", reply_markup=reply_markup)
    return CHOOSING_PACK

async def pack_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, pack_name, pack_price = query.data.split('_')
    context.user_data['pack_name'] = pack_name
    context.user_data['pack_price'] = pack_price
    await query.edit_message_text(
        text=f"📋 သင်ရွေးချယ်ထားသည်: {pack_name} ({pack_price})\n\n👉 ကျေးဇူးပြု၍ သင်၏ Game ID နှင့် Server ID ကို ရိုက်ထည့်ပေးပါရှင်-\n(ဥပမာ - 12345678 (1234) )"
    )
    return ENTERING_GAME_ID

async def game_id_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['game_id'] = update.message.text
    payment_msg = (
        "💰 **ငွေပေးချေမှုစနစ်**\n\n"
        "📱 **Kpay** - `09697725071`\n"
        "👤 အမည် - Zin Ko Aung\n\n"
        "📱 **Wave Pay** - `09697725071`\n"
        "👤 အမည် - Zin Ko Aung\n\n"
        "⚠️ Ngwe lwal pee par ka **Ngwe lwal pyay sar (Screenshot)** ko dat pone pone san hpyint po pay par shin."
    )
    await update.message.reply_text(payment_msg, parse_mode="Markdown")
    return SENDING_RECEIPT

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ငွေလွှဲပြေစာ ဓာတ်ပုံကိုသာ ပို့ပေးပါရှင်။")
        return SENDING_RECEIPT
    photo_file = update.message.photo[-1].file_id
    user = update.message.from_user
    await update.message.reply_text("✅ လူကြီးမင်း၏ Order ကို လက်ခံရရှိပါပြီ။ ခေတ္တစောင့်ဆိုင်းပေးပါရှင်။")
    cat_title = "Weekly Pass" if context.user_data['category'] == 'wp' else ("Double Dia" if context.user_data['category'] == 'double' else "Normal Dia")
    order_text = (
        "🚨 **ORDER အသစ် ရောက်လာပါပြီ!**\n\n"
        f"👤 ဝယ်သူ: {user.first_name} (Username: @{user.username if user.username else 'မရှိပါ'})\n"
        f"🗂 အမျိုးအစား: {cat_title}\n"
        f"💎 ပမာဏ: {context.user_data['pack_name']}\n"
        f"💵 ဈေးနှုန်း: {context.user_data['pack_price']}\n"
        f"🎮 Game ID: `{context.user_data['game_id']}`\n"
    )
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file, caption=order_text, parse_mode="Markdown")
    return ConversationHandler.END

async def admin_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.chat_id) != str(ADMIN_CHAT_ID):
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်သဖြင့် ဤလုပ်ဆောင်ချက်ကို သုံးခွင့်မရှိပါ။")
        return ConversationHandler.END
    await update.message.reply_text("📢 Channel မှာ တင်ချင်တဲ့ စာ (သို့မဟုတ်) Promotion ကို ရိုက်ထည့်ပေးပါ-")
    return SENDING_POST

async def admin_post_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_text = update.message.text
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        await update.message.reply_text("✅ Channel ထဲသို့ Post အောင်မြင်စွာ တင်ပြီးပါပြီရှင်။")
    except Exception as e:
        await update.message.reply_text(f"❌ Post တင်ရတာ အဆင်မပြေပါ။ အကြောင်းရင်း: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("လုပ်ဆောင်ချက်ကို ဖျက်သိမ်းလိုက်ပါပြီ။")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    buy_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Diamond ဝယ်ယူရန်'), buy_diamond)],
        states={
            CHOOSING_CAT: [CallbackQueryHandler(cat_chosen)],
            CHOOSING_PACK: [CallbackQueryHandler(pack_chosen)],
            ENTERING_GAME_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_id_entered)],
            SENDING_RECEIPT: [MessageHandler(filters.PHOTO, receipt_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    post_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📢 Channel သို့ Post တင်ရန် \(Admin\)$'), admin_post_start)],
        states={
            SENDING_POST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_post_send)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(buy_conv)
    app.add_handler(post_conv)
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
