import json
from datetime import datetime
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# Поддерживаемые языки
LANGUAGES = ['ru', 'uz']

# Чтение наличия из файла
with open('data/availability.json', 'r', encoding='utf-8') as f:
    AVAIL = json.load(f)

# Тексты сообщений
TEXTS = {
    'ru': {
        'welcome': 'Assalomu alaykum!\n'
                   'Добро пожаловать в Samsariya — бот для домашней самсы.\n'
                   '+998880009099',
        'off_hours_preorder': 'Сейчас мы не работаем, но Вы можете оформить предзаказ',
        'about': 'Samsariya — это домашняя самса по семейным рецептам, без жира и добавок.',
        'promo': 'Акции и новинки:\n'
                 '- Самса с тыквой (сезонная)\n'
                 '- Скидка 10% при оплате через Payme',
        'working_hours': 'Заказы принимаем с 10:00 до 20:00. Доставка по Ташкенту — 1–2 часа.',
        'payments': 'Оплатить наличными или картой через Payme (100% предоплата со скидкой).',
        'repeat_unavailable': 'У вас ещё нет предыдущих заказов.',
        'ask_review': 'Оставьте отзыв (текст или голосовое).',
        'thank_review': 'Спасибо! Ваш отзыв отправлен.',
        'show_reviews': 'Отзывы клиентов:'
    },
    'uz': {
        'welcome': 'Assalomu alaykum!\n'
                   'Samsariya – uy sharoitida pishirilgan somsa botiga xush kelibsiz.\n'
                   '+998880009099',
        'off_hours_preorder': 'Hozir faoliyatimiz to‘xtagan, oldindan buyurtma bera olasiz',
        'about': 'Samsariya oila retsepti bo‘yicha, yog‘siz va qo‘shimchasiz tayyorlangan somsa.',
        'promo': 'Aksiya va yangiliklar:\n'
                 '- Qovoqli somsa (fasliy)\n'
                 '- Payme orqali to‘lovda 10% chegirma',
        'working_hours': 'Buyurtmalar 9:00–19:00 qabul qilinadi. Toshkent bo‘ylab 1–2 soat ichida yetkazib beramiz.',
        'payments': 'Naqd yoki Payme orqali (100% oldindan to‘lov, chegirma bilan).',
        'repeat_unavailable': 'Avvalgi buyurtmangiz yo‘q.',
        'ask_review': 'Fikr-mulohazangizni matn yoki ovozli xabar sifatida yuboring.',
        'thank_review': 'Rahmat! Fikringiz qabul qilindi.',
        'show_reviews': 'Mijozlar fikrlari:'
    }
}

# Клавиатуры
KEYBOARDS = {
    'main': [
        ['/order', '/reviews'],
        ['/about', '/promo'],
        ['/workinghours', '/payments'],
        ['/repeat', '/language']
    ],
    'back': [['/main']]
}

def init_bot_data(app):
    app.bot_data['lang']  = 'ru'
    app.bot_data['texts'] = TEXTS['ru']
    app.bot_data['avail'] = AVAIL
    app.bot_data['keyb']  = {
        name: ReplyKeyboardMarkup(keys, one_time_keyboard=True)
        for name, keys in KEYBOARDS.items()
    }

async def set_language(update, context):
    kb = ReplyKeyboardMarkup([['ru', 'uz']], one_time_keyboard=True)
    await update.message.reply_text('Выберите язык / Tilni tanlang', reply_markup=kb)

async def help_command(update, context):
    cmds = [
        '/start — запуск', '/order — новый заказ', '/reviews — отзывы',
        '/about — о нас', '/promo — акции', '/workinghours — время работы',
        '/payments — оплата', '/repeat — повтор заказа',
        '/language — сменить язык', '/help — помощь'
    ]
    await update.message.reply_text('\n'.join(cmds))

async def main_menu(update, context):
    await update.message.reply_text(
        context.bot_data['texts']['welcome'],
        reply_markup=context.bot_data['keyb']['main']
    )
