import json, time, hmac, hashlib
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from config import ADMIN_ID, PAYME_MERCHANT_ID, PAYME_SECRET_KEY, ORDERS_DB
# Функция для JobQueue: будет вызываться раз в N минут/секунд
async def remind_unfinished(context):
    # TODO: пройтись по сохранённым состояниям пользователей
    # и отправить им напоминание о незавершённом заказе
    # Пример:
    # await context.bot.send_message(chat_id=user_id, text="Вы не завершили заказ…")
    pass

MENU, CONTACT, DELIVERY, TIME_CHOICE, PAYMENT, CONFIRM = range(6)

PRICES = {
    'картофельная': 8000, 'тыквенная': 8000, 'зелень': 8000,
    'говяжья': 10000, 'куриная': 10000
}

# Загрузка/сохранение заказов
try:
    ORDERS = json.load(open(ORDERS_DB, 'r', encoding='utf-8'))
except FileNotFoundError:
    ORDERS = {}




async def order_start(update, context):
    avail = context.bot_data['avail']
    menu = '\n'.join(f"{n}: {PRICES[n]} сум" for n, ok in avail.items() if ok)
    await update.message.reply_text(f"Меню:\n{menu}\n\nВведите 'название:количество,...'")
    context.user_data.clear()
    context.user_data['start_time'] = time.time()
    return MENU

async def order_menu(update, context):
    sel = update.message.text
    items, total = {}, 0
    for part in sel.split(','):
        name, qty = part.split(':')
        name, qty = name.strip(), int(qty)
        if name in PRICES and context.bot_data['avail'].get(name):
            items[name] = qty
            total += PRICES[name] * qty
    context.user_data['items'] = items
    context.user_data['total'] = total
    await update.message.reply_text(f"Итого: {total} сум.\nВведите имя, телефон и адрес:")
    return CONTACT

async def order_contact(update, context):
    context.user_data['contact'] = update.message.text
    kb = ReplyKeyboardMarkup([['Доставка','Самовывоз']], one_time_keyboard=True)
    await update.message.reply_text('Доставка или самовывоз?', reply_markup=kb)
    return DELIVERY

async def order_delivery(update, context):
    context.user_data['delivery'] = update.message.text
    kb = ReplyKeyboardMarkup([['Как можно скорее','К времени']], one_time_keyboard=True)
    await update.message.reply_text('Когда доставить?', reply_markup=kb)
    return TIME_CHOICE

async def order_time(update, context):
    context.user_data['time'] = update.message.text
    kb = ReplyKeyboardMarkup([['Наличные','Payme']], one_time_keyboard=True)
    await update.message.reply_text('Оплата наличными или Payme?', reply_markup=kb)
    return PAYMENT

def generate_payme_link(oid, amount):
    a = amount * 100
    data = f"account[order_id]={oid}&merchant={PAYME_MERCHANT_ID}&amount={a}"
    sig = hmac.new(PAYME_SECRET_KEY.encode(), data.encode(), hashlib.sha1).hexdigest()
    return f"https://checkout.paycom.uz/{PAYME_MERCHANT_ID}?{data}&signature={sig}"

async def order_payment(update, context):
    m = update.message.text
    context.user_data['method'] = m
    if m == 'Payme':
        oid = f"{update.effective_user.id}_{int(time.time())}"
        link = generate_payme_link(oid, context.user_data['total'])
        context.user_data['pay_link'] = link
        await update.message.reply_text(f"Оплатите: {link}")
    summary = (
        f"Ваш заказ:\n{context.user_data['items']}\n"
        f"Сумма: {context.user_data['total']} сум\n"
        f"{context.user_data['delivery']} в {context.user_data['time']}\n"
        f"Контакты: {context.user_data['contact']}"
    )
    kb = ReplyKeyboardMarkup([['Подтвердить','Отменить']], one_time_keyboard=True)
    await update.message.reply_text(summary, reply_markup=kb)
    return CONFIRM

async def order_confirm(update, context):
    if update.message.text == 'Подтвердить':
        uid = str(update.effective_user.id)
        ORDERS.setdefault(uid, []).append(context.user_data.copy())
        with open(ORDERS_DB, 'w', encoding='utf-8') as f:
            json.dump(ORDERS, f, ensure_ascii=False, indent=2)
        await update.message.reply_text('Заказ принят! Скоро свяжемся.')
        await context.bot.send_message(chat_id=ADMIN_ID, text=str(context.user_data))
    else:
        await update.message.reply_text('Отменено.')
    return ConversationHandler.END

order_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('order', order_start)],
    states={
        MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_menu)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_contact)],
        DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_delivery)],
        TIME_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_time)],
        PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_payment)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_confirm)],
    },
    fallbacks=[]
)
