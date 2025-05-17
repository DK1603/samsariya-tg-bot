import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')  # строковый идентификатор или числовой

# Payme
PAYME_MERCHANT_ID = os.getenv('PAYME_MERCHANT_ID')
PAYME_SECRET_KEY = os.getenv('PAYME_SECRET_KEY')
PAYME_CALLBACK_PATH = os.getenv('PAYME_CALLBACK_PATH', '/payme-callback')

# Рабочее время
WORK_START_HOUR = int(os.getenv('WORK_START_HOUR', '9'))
WORK_END_HOUR   = int(os.getenv('WORK_END_HOUR',   '19'))

# Data files
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
REVIEWS_FILE     = os.path.join(DATA_DIR, 'reviews.json')
AVAILABILITY_FILE = os.path.join(DATA_DIR, 'availability.json')
ORDERS_DB        = os.path.join(DATA_DIR, 'orders.json')
