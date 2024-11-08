import os
import sys

# Telegram API credentials
APP_ID = os.getenv('APP_ID')
APP_HASH = os.getenv('APP_HASH')
TOKEN = os.getenv('TOKEN')

# Optional configurations
OWNER = os.getenv('OWNER', 'default_owner')

# Проверка обязательных переменных
missing_vars = []
if not APP_ID:
    missing_vars.append('APP_ID')
if not APP_HASH:
    missing_vars.append('APP_HASH')
if not TOKEN:
    missing_vars.append('TOKEN')

if missing_vars:
    print(f"Ошибка: Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
    sys.exit(1)
