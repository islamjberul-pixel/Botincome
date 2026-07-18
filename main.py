import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import *
from database import *

LEVELS = [0.25, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id, user.username)
    ref = context.args[0] if context.args else None # Refer system

    keyboard = [
        [InlineKeyboardButton("💰 Account", callback_data='account')],
        [InlineKeyboardButton("👥 Refer", callback_data='refer')],
        [InlineKeyboardButton("🏦 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("📞 Support", url='https://t.me/admin')]
    ]
    await update.message.reply_text(f"👋 Welcome {user.first_name}!", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID: return await update.message.reply_text("⛔ Access Denied")

    keyboard = [
        [InlineKeyboardButton("📊 Dashboard", callback_data='ad_dash')],
        [InlineKeyboardButton("✅ Activation Requests", callback_data='ad_active')],
        [InlineKeyboardButton("💸 Withdraw Requests", callback_data='ad_with')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='ad_set')]
    ]
    await update.message.reply_text("🔐 Admin Panel", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user = await get_user(user_id)

    if data == 'withdraw':
        if user['is_active'] == 0:
            text = f"⚠️ Account Activate করুন\nWallet: `{WALLET_ADDRESS}`\nNetwork: USDT BEP20\nAmount: {ACTIVATION_FEE}$\n\nPayment করে নিচের বাটনে SS দিন"
            keyboard = [[InlineKeyboardButton("📸 Payment Verify", callback_data='verify_ss')]]
            return await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

        # Level দেখাও
        text = "🏦 Withdraw Levels\n"
        for i, lvl in enumerate(LEVELS):
            if i == user['current_level']:
                text += f"Level {i+1}: {lvl}$ [Withdraw]\n"
            else:
                text += f"Level {i+1}: {lvl}$ [Locked]\n"
        await query.edit_message_text(text)

    if data == 'verify_ss':
        await query.edit_message_text("0.15$ পাঠিয়ে Screenshot টা এখানে পাঠান")

    if data == 'ad_active' and user_id == ADMIN_ID:
        conn = await get_conn()
        reqs = await conn.fetch("SELECT * FROM activations WHERE status='pending'")
        await conn.close()
        if not reqs: return await query.edit_message_text("No Pending Activation")
        for r in reqs:
            keyboard = [[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{r['user_id']}")]]
            await context.bot.send_photo(ADMIN_ID, photo=r['ss_file_id'], caption=f"User: {r['user_id']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    file_id = update.message.photo[-1].file_id
    conn = await get_conn()
    await conn.execute("INSERT INTO activations (user_id, ss_file_id) VALUES ($1, $2)", user_id, file_id)
    await conn.close()
    await update.message.reply_text("⏳ 1 Hour এর মধ্যে Verify হবে")
    await context.bot.send_message(ADMIN_ID, f"New Activation Request: {user_id}")

async def post_init(app: Application):
    await init_db()

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot Running...")
    app.run_polling()

if __name__ == '__main__':
    main()
