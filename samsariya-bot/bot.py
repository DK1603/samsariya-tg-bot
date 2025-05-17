import logging
import json
from datetime import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, JobQueue
from handlers.common import init_bot_data, help_command, set_language, main_menu
from handlers.order import order_conv_handler, remind_unfinished
from handlers.feedback import feedback_handler
from config import BOT_TOKEN, WORK_START_HOUR, WORK_END_HOUR

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    now = datetime.now().hour
    if not (WORK_START_HOUR <= now < WORK_END_HOUR):
        return await update.message.reply_text(context.bot_data['texts']['off_hours_preorder'])
    # выбор языка
    kb = ReplyKeyboardMarkup([['ru','uz']], one_time_keyboard=True)
    await update.message.reply_text('Выберите язык / Tilni tanlang', reply_markup=kb)

async def about(update, context):
    await update.message.reply_text(context.bot_data['texts']['about'], reply_markup=context.bot_data['keyb']['main'])

async def promo(update, context):
    await update.message.reply_text(context.bot_data['texts']['promo'], reply_markup=context.bot_data['keyb']['main'])

async def working_hours(update, context):
    await update.message.reply_text(context.bot_data['texts']['working_hours'], reply_markup=context.bot_data['keyb']['main'])

async def payments_info(update, context):
    await update.message.reply_text(context.bot_data['texts']['payments'], reply_markup=context.bot_data['keyb']['main'])

async def repeat_order(update, context):
    user_id = str(update.effective_user.id)
    orders = json.load(open('data/orders.json', 'r', encoding='utf-8'))
    if user_id in orders:
        prev = orders[user_id][-1]
        await update.message.reply_text(f"Повтор заказа:\n{prev['summary']}", reply_markup=context.bot_data['keyb']['main'])
    else:
        await update.message.reply_text(context.bot_data['texts']['repeat_unavailable'], reply_markup=context.bot_data['keyb']['main'])

async def language_cmd(update, context):
    await set_language(update, context)

async def help_cmd(update, context):
    await help_command(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    init_bot_data(app)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('main', main_menu))
    app.add_handler(CommandHandler('about', about))
    app.add_handler(CommandHandler('promo', promo))
    app.add_handler(CommandHandler('workinghours', working_hours))
    app.add_handler(CommandHandler('payments', payments_info))
    app.add_handler(CommandHandler('repeat', repeat_order))
    app.add_handler(CommandHandler('language', language_cmd))
    app.add_handler(CommandHandler('help', help_cmd))

    app.add_handler(order_conv_handler)
    app.add_handler(feedback_handler)

    jq: JobQueue = app.job_queue
    jq.run_repeating(remind_unfinished, interval=7*24*3600, first=7*24*3600)  # напоминание через 7 дней

    app.run_polling()

if __name__ == '__main__':
    main()
