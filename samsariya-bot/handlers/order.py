import json
import time
import hmac
import hashlib
from datetime import datetime
from telegram import ReplyKeyboardMarkup, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from config import ADMIN_ID, PAYME_MERCHANT_ID, PAYME_SECRET_KEY, ORDERS_DB, WORK_START_HOUR, WORK_END_HOUR

from handlers.common import main_menu

# Шаги
MENU, CONTACT, DELIVERY, TIME_CHOICE, PAYMENT, CONFIRM = range(6)

# Цены
PRICES = {
    'картофельная': 8000, 'тыквенная': 8000, 'зелень': 8000,
    'говяжья': 10000, 'куриная': 10000
}

# Загрузка заказов
try:
    ORDERS = json.load(open(ORDERS_DB, 'r', encoding='utf-8'))
except FileNotFoundError:
    ORDERS = {}

async def remind_unfinished(context):
    # Реализация напоминаний по расписанию
    pass

async def order_start(update, context):
    now = datetime.now().hour
    # Проверка времени работы
    if not (WORK_START_HOUR <= now < WORK_END_HOUR):
        return await update.message.reply_text(context.bot_data['texts']['off_hours_preorder'])
    # Фото-меню с кнопками ➕
    for name, ok in context.bot_data['avail'].items():
        if ok:
            price = PRICES[name]
            photo = open(f'data/img/{name}.jpg', 'rb')
            btn = InlineKeyboardMarkup([[InlineKeyboardButton(f'➕ {price} сум', callback_data=f'add:{name}')]])
            await update.message.reply_photo(photo=photo, caption=f'{name} – {price} сум', reply_markup=btn)
    await update.message.reply_text('Нажмите ➕ рядом с нужным названием.')
    context.user_data.clear()
    return MENU

async def add_item(query, context):
    name = query.data.split(':')[1]
    items = context.user_data.setdefault('items', {})
    items[name] = items.get(name, 0) + 1
    await query.answer(f'{name} добавлено ({items[name]})')

async def order_menu(update, context):
    # После нажатия “Сделать заказ”
    total = sum(PRICES[n] * q for n, q in context.user_data.get('items', {}).items())
    context.user_data['total'] = total
    await update.message.reply_text(f'Итого: {total} сум.\nВведите имя, телефон и адрес:')
    return CONTACT

async def order_contact(update, context):
    context.user_data['contact'] = update.message.text
    kb = ReplyKeyboardMarkup([['Доставка', 'Самовывоз']], one_time_keyboard=True)
    await update.message.reply_text('Доставка или самовывоз?', reply_markup=kb)
    return DELIVERY

async def order_delivery(update, context):
    context.user_data['delivery'] = update.message.text
    kb = ReplyKeyboardMarkup([['Как можно скорее', 'К конкретному времени']], one_time_keyboard=True)
    await update.message.reply_text('Когда доставить?', reply_markup=kb)
    return TIME_CHOICE

async def order_time(update, context):
    choice = update.message.text
    if choice == 'К конкретному времени':
        await update.message.reply_text('Введите время (например, 14:30):', reply_markup=ForceReply())
        return TIME_CHOICE
    context.user_data['time'] = choice
    kb = ReplyKeyboardMarkup([['Наличные', 'Добавить карту']], one_time_keyboard=True)
    await update.message.reply_text('Способ оплаты?', reply_markup=kb)
    return PAYMENT

def generate_payme_link(oid, amount):
    a = amount * 100
    data = f"account[order_id]={oid}&merchant={PAYME_MERCHANT_ID}&amount={a}"
    sig = hmac.new(PAYME_SECRET_KEY.encode(), data.encode(), hashlib.sha1).hexdigest()
    return f"https://checkout.paycom.uz/{PAYME_MERCHANT_ID}?{data}&signature={sig}"

async def order_payment(update, context):
    method = update.message.text
    context.user_data['method'] = method
    total = context.user_data['total']
    if method == 'Добавить карту':
        oid = f"{update.effective_user.id}_{int(time.time())}"
        link = generate_payme_link(oid, total)
        context.user_data['pay_link'] = link
        await update.message.reply_text(f"Оплатите по ссылке: {link}")
    summary = (
        f"Ваш заказ:\n{context.user_data.get('items')}\n"
        f"Сумма: {total} сум\n"
        f"{context.user_data['delivery']} в {context.user_data.get('time')}\n"
        f"Контакт: {context.user_data['contact']}"
    )
    context.user_data['summary'] = summary
    kb = ReplyKeyboardMarkup([['Подтвердить', 'Отменить']], one_time_keyboard=True)
    await update.message.reply_text(summary, reply_markup=kb)
    return CONFIRM

async def order_confirm(update, context):
    if update.message.text == 'Подтвердить':
        uid = str(update.effective_user.id)
        ORDERS.setdefault(uid, []).append(context.user_data.copy())
        with open(ORDERS_DB, 'w', encoding='utf-8') as f:
            json.dump(ORDERS, f, ensure_ascii=False, indent=2)
        await update.message.reply_text('Ваш заказ принят! С вами скоро свяжутся.')
        await context.bot.send_message(chat_id=ADMIN_ID, text=context.user_data['summary'])
    else:
        await update.message.reply_text('Заказ отменён.')
    return ConversationHandler.END

order_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('order', order_start)],
    states={
        MENU:   [CallbackQueryHandler(add_item, pattern=r'^add:')],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_menu)],
        DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_contact)],
        TIME_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_time)],
        PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_payment)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_confirm)],
    },
    fallbacks=[CommandHandler('main', main_menu)]
)
