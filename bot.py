import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

# ---- ပြင်ဆင်ရန် အချက်အလက်များ ----
TOKEN = "YOUR_BOT_TOKEN_HERE"  # `@BotFather` မှရသော Token ထည့်ရန်
ADMIN_CHAT_ID = "YOUR_TELEGRAM_ID_HERE"  # သင့်ဆီ Order ရောက်လာမည့် ID ထည့်ရန်
CHANNEL_ID = "@your_channel_username"  # သင့် Channel Username (သို့) ID ထည့်ရန်
# --------------------------------

# Conversation States
CHOOSING_PACK, ENTERING_GAME_ID, SENDING_RECEIPT, SENDING_POST = range(4)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Customer အတွက် Reply Keyboard
    keyboard = [['💎 Diamond ဝယ်ယူရန်', '📢 Channel သို့ Post တင်ရန် (Admin)']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "မင်္ဂလာပါရှင်။ Diamond ဆိုင် Bot မှ ကြိုဆိုပါတယ်။\nအောက်က Menu ကိုနှိပ်ပြီး ဝယ်ယူနိုင်ပါတယ်ရှင်။",
        reply_markup=reply_markup
    )

# Diamond ဝယ်ယူရန် နှိပ်ခြင်း
async def buy_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Diamond Packages များပြရန်
    keyboard = [
        [InlineKeyboardButton("💎 50 Diamonds - 1,500 MMK", callback_query_data='pack_50')],
        [InlineKeyboardButton("💎 100 Diamonds - 3,000 MMK", callback_query_data='pack_100')],
        [InlineKeyboardButton("💎 500 Diamonds - 14,000 MMK", callback_query_data='pack_500')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ဝယ်ယူလိုသည့် Diamond ပမာဏကို ရွေးချယ်ပေးပါ-", reply_markup=reply_markup)
    return CHOOSING_PACK

# Package ရွေးချယ်မှု လက်ခံခြင်း
async def pack_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # ရွေးလိုက်တဲ့ pack ကို မှတ်ထားမယ်
    context.user_data['pack'] = query.data.split('_')[1]
    
    await query.edit_message_text(text=f"🔹 သင်ရွေးချယ်ထားသော ပမာဏ: {context.user_data['pack']} Diamonds\n\nကျေးဇူးပြု၍ သင်၏ Game ID နှင့် Server ID ကို ရိုက်ထည့်ပေးပါ- (ဥပမာ - 12345678 (1234) )")
    return ENTERING_GAME_ID

# Game ID လက်ခံခြင်း
async def game_id_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['game_id'] = update.message.text
    
    await update.message.reply_text(
        "🔹 ငွေပေးချေမှုစနစ်\nKpay / Wave - 09xxxxxxxxx (U Mg Mg)\n\nငွေလွှဲပြောင်းပြီးပါက ငွေလွှဲပြေစာ (Screenshot) ကို ဓာတ်ပုံပုံစံဖြင့် ပို့ပေးပါရှင်-"
    )
    return SENDING_RECEIPT

# ပြေစာပုံ လက်ခံခြင်း နှင့် သင့်ဆီ Order ပို့ခြင်း
async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    user = update.message.from_user
    
    # Customer ဆီ စာပြန်ခြင်း
    await update.message.reply_text("✅ လူကြီးမင်း၏ Order ကို လက်ခံရရှိပါပြီ။ ခေတ္တစောင့်ဆိုင်းပေးပါရှင်။")
    
    # သင့်ဆီ (Admin ဆီ) Order အချက်အလက် လှမ်းပို့ခြင်း
    order_text = (
        "🔔 **Order အသစ် ရောက်ရှိလာပါပြီ!**\n\n"
        f"👤 ဝယ်သူ: {user.first_name} (Username: @{user.username})\n"
        f"💎 ပမာဏ: {context.user_data['pack']} Diamonds\n"
        f"🎮 Game ID: {context.user_data['game_id']}\n"
    )
    
    # သင့်ဆီကို ပုံရော စာရော ပို့ပေးမယ်
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file, caption=order_text, parse_mode="Markdown")
    return ConversationHandler.END

# ---- ADMIN SECTION: CHANNEL POST ----
async def admin_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # စစ်ဆေးချက် - မည်သူမဆို post တင်လို့မရအောင် သင့် ID ဖြစ်မှ ခွင့်ပြုမယ်
    if str(update.message.chat_id) != str(ADMIN_CHAT_ID):
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်သဖြင့် ဤလုပ်ဆောင်ချက်ကို သုံးခွင့်မရှိပါ။")
        return ConversationHandler.END
        
    await update.message.reply_text("📢 Channel မှာ တင်ချင်တဲ့ စာ သို့မဟုတ် Promotion အကြောင်းအရာကို ရိုက်ထည့်ပေးပါ-")
    return SENDING_POST

async def admin_post_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_text = update.message.text
    
    try:
        # Channel ထဲကို တိုက်ရိုက် လှမ်းတင်ခြင်း
        await context.bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        await update.message.reply_text("✅ Channel ထဲသို့ Post အောင်မြင်စွာ တင်ပြီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Post တင်ရက် အဆင်မပြေပါ။ အမှား: {e}")
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("အလုပ်လုပ်ဆောင်မှု ရပ်တန့်လိုက်ပါပြီ။")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    # User Order Flow
    buy_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^💎 Diamond ဝယ်ယူရန်$'), buy_diamond)],
        states={
            CHOOSING_PACK: [CallbackQueryHandler(pack_chosen)],
            ENTERING_GAME_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_id_entered)],
            SENDING_RECEIPT: [MessageHandler(filters.PHOTO, receipt_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Admin Channel Post Flow
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

    print("Bot 💥 စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
