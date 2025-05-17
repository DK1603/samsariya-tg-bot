import json
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from handlers.common import main_menu
from config import REVIEWS_FILE, ADMIN_ID

SHOW, COLLECT = range(2)

def load_reviews():
    try:
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_review(text):
    rs = load_reviews()
    rs.append(text)
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(rs, f, ensure_ascii=False, indent=2)

async def reviews_start(update, context):
    reviews = load_reviews()[-5:]
    await update.message.reply_text(context.bot_data['texts']['show_reviews'], reply_markup=context.bot_data['keyb']['back'])
    await update.message.reply_text('\n\n'.join(reviews))
    await update.message.reply_text(context.bot_data['texts']['ask_review'])
    return COLLECT

async def reviews_collect(update, context):
    text = update.message.text or '<voice message>'
    save_review(text)
    await update.message.reply_text(context.bot_data['texts']['thank_review'])
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Новый отзыв:\n{text}")
    return ConversationHandler.END

feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('reviews', reviews_start)],
    states={COLLECT: [MessageHandler(filters.ALL & ~filters.COMMAND, reviews_collect)]},
    fallbacks=[CommandHandler('main', main_menu)]
)
