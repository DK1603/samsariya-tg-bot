import logging
import json
from telegram.ext import ApplicationBuilder, CommandHandler, JobQueue
from handlers.common import init_bot_data, help_command, set_language
from handlers.order import order_conv_handler, remind_unfinished
from handlers.feedback import feedback_handler
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    await update.message.reply_text(
        context.bot_data['texts']['welcome'],
        reply_markup=context.bot_data['keyb']['main']
    )

# Прямые команды
async def about(update, context):
    await update.message.reply_text(context.bot_data['texts']['about'])

async def promo(update, context):
    await update.message.reply_text(context.bot_data['texts']['promo'])

async def working_hours(update, context):
    await update.message.reply_text(context.bot_data['texts']['working_hours'])

async def payments_info(update, context):
    await update.message.reply_text(context.bot_data['texts']['payments'])

async def repeat_order(update, context):
    user_id = str(update.effective_user.id)
    orders = json.load(open('data/orders.json', 'r', encoding='utf-8'))
    if user_id in orders:
        prev = orders[user_id][-1]
        await update.message.reply_text(f"Повтор заказа:\n{prev['summary']}")
        # Можно сразу перенаправить в confirm-часть
    else:
        await update.message.reply_text(context.bot_data['texts']['repeat_unavailable'])

async def language_cmd(update, context):
    await set_language(update, context)

async def help_cmd(update, context):
    await help_command(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    init_bot_data(app)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('about', about))
    app.add_handler(CommandHandler('promo', promo))
    app.add_handler(CommandHandler('workinghours', working_hours))
    app.add_handler(CommandHandler('payments', payments_info))
    app.add_handler(CommandHandler('repeat', repeat_order))
    app.add_handler(CommandHandler('language', language_cmd))
    app.add_handler(CommandHandler('help', help_cmd))

    # Ручка оформления заказа
    app.add_handler(order_conv_handler)
    # Ручка отзывов
    app.add_handler(feedback_handler)

    # Напоминания о незавершенных заказах
    jq: JobQueue = app.job_queue
    jq.run_repeating(remind_unfinished, interval=900, first=900)

    app.run_polling()

if __name__ == '__main__':
    main()
