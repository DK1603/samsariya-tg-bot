import json
from telegram import ReplyKeyboardMarkup

# Поддерживаемые языки
LANGUAGES = ['ru', 'uz']

# Чтение наличия из файла
with open('data/availability.json', 'r', encoding='utf-8') as f:
    AVAIL = json.load(f)

# Тексты сообщений
TEXTS = {
    'ru': {
        'welcome': 'Привет! Assalomu alaykum!\n'
                   'Добро пожаловать в Samsariya — бот для домашней самсы.\n'
                   'Выберите раздел ниже.',
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
        # Переводы на узбекский
    }
}

# Клавиатуры
KEYBOARDS = {
    'main': [
        ['/order', '/reviews'],
        ['/about', '/promo'],
        ['/workinghours', '/payments'],
        ['/repeat', '/language']
    ]
}

def init_bot_data(app):
    app.bot_data['lang'] = 'ru'
    app.bot_data['texts'] = TEXTS['ru']
    app.bot_data['avail'] = AVAIL
    app.bot_data['keyb'] = {
        name: ReplyKeyboardMarkup(keys, one_time_keyboard=True)
        for name, keys in KEYBOARDS.items()
    }

async def set_language(update, context):
    markup = ReplyKeyboardMarkup([['ru', 'uz']], one_time_keyboard=True)
    await update.message.reply_text('Выберите язык / Tilni tanlang', reply_markup=markup)

async def help_command(update, context):
    cmds = [
        '/start — запуск', '/order — новый заказ', '/reviews — отзывы',
        '/about — о нас', '/promo — акции', '/workinghours — время работы',
        '/payments — оплата', '/repeat — повтор заказа',
        '/language — сменить язык', '/help — помощь'
    ]
    await update.message.reply_text('\n'.join(cmds))
