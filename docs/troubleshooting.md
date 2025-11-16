# 🐛 Траблшутинг и Решения

## 📋 Обзор

Руководство по решению распространенных проблем, которые могут возникнуть при разработке, развертывании и использовании финансового бота.

## 🚀 Запуск и развертывание

### ❌ Бот не запускается

#### Проблема: Отсутствие токена
```
ValueError: BOT_TOKEN не найден!
```

**Причина:** Отсутствует или некорректно настроен .env файл

**Решение:**
```bash
# Создать .env файл из примера
cp .env.example .env

# Редактировать .env файл
BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
```

**Проверка:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print("Token exists:", bool(os.getenv("BOT_TOKEN")))
```

#### Проблема: Несовместимость aiogram версии
```
TypeError: Passing `parse_mode` to Bot initializer is not supported anymore
```

**Причина:** Изменения API в aiogram 3.7+

**Решение:**
```python
# Было (старый синтаксис):
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

# Стало (новый синтаксис):
from aiogram import DefaultBotProperties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
```

#### Проблема: Отсутствуют зависимости
```
ModuleNotFoundError: No module named 'aiogram'
```

**Причина:** Не установлены зависимости

**Решение:**
```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Или только отсутствующего модуля
pip install aiogram==3.10.0
```

**Автоматическая установка:**
```bash
python install_dashboard_deps.py
```

### ❌ База данных не найдена

#### Проблема: Файл БД отсутствует
```
FileNotFoundError: База данных не найдена: finance_bot.db
```

**Причина:** База данных еще не создана

**Решение:**
```bash
# Запустить бота для создания БД
python main.py
# База данных создастся автоматически
```

**Проверка:**
```python
import os
print("DB exists:", os.path.exists("finance_bot.db"))
```

#### Проблема: Ошибка в SQL запросе
```
sqlite3.OperationalError: no such table: transactions
```

**Причина:** Таблицы не созданы

**Решение:**
```python
# Принудительная инициализация БД
import asyncio
from database import db

async def init_db():
    await db.init_db()
    print("Database initialized successfully")

asyncio.run(init_db())
```

### ❌ Проблемы с портами

#### Проблема: Порт уже занят (Dashboard)
```
Port 8501 is already in use
```

**Решение:**
```bash
# Изменить порт
streamlit run dashboard/app.py --server.port 8502

# Или найти и завершить процесс
lsof -i :8501
kill -9 PID
```

**Автоматический выбор порта:**
```bash
streamlit run dashboard/app.py --server.port 0
```

## 🤖 Ошибки Telegram бота

### ❌ Пользователь не получает ответ

#### Проблема: Update не обрабатывается
```
INFO:aiogram.event:Update id=123456 is not handled.
```

**Причина:** Не зарегистрирован обработчик

**Решение:**
```python
# Проверить регистрацию обработчиков
dp.message.register(handler_function, Command("command_name"))
dp.callback_query.register(callback_function, F.data == "callback_data")
```

**Отладка:**
```python
# Добавить логирование
import logging
logging.basicConfig(level=logging.INFO)

# Или детальное логирование aiogram
logging.getLogger('aiogram').setLevel(logging.DEBUG)
```

#### Проблема: Callback кнопки не работают
```
CallbackQuery exception: 'callback_data' not found
```

**Причина:** Несоответствие callback_data и обработчиков

**Решение:**
```python
# Проверить callback_data в кнопке
button = InlineKeyboardButton(
    text="Button",
    callback_data="correct_callback_data"  # должно соответствовать обработчику
)

# Проверить регистрацию обработчика
dp.callback_query.register(
    callback_handler,
    F.data == "correct_callback_data"
)
```

**Отладка callback:**
```python
async def debug_callback(callback: CallbackQuery):
    logger.info(f"Received callback: {callback.data}")
    # обработка
```

### ❌ Ошибки в работе с базой данных

#### Проблема: AsyncSession не работает как context manager
```
TypeError: 'coroutine' object does not support the asynchronous context manager protocol
```

**Причина:** Неправильное использование AsyncSession

**Решение:**
```python
# Было (неправильно):
async with db.get_session() as session:
    # операции

# Стало (правильно):
session = await db.get_session()
try:
    # операции
finally:
    await session.close()
```

**Или использовать async_sessionmaker:**
```python
# В database.py
from sqlalchemy.ext.asyncio import async_sessionmaker

class Database:
    def __init__(self):
        self.async_session = async_sessionmaker(bind=self.engine)

    async def get_session(self):
        return self.async_session()
```

#### Проблема: Сохранение не работает
```
Transaction object not bound to session
```

**Причина:** Объект создан вне сессии

**Решение:**
```python
# Правильное создание объекта в сессии
async def add_transaction(session: AsyncSession, data: dict):
    transaction = Transaction(
        user_id=data['user_id'],
        transaction_type=data['type'],
        # ...
    )
    session.add(transaction)
    await session.commit()
```

### ❌ Ошибки парсинга сообщений

#### Проблема: Неправильный формат сообщения
```
ValueError: could not convert string to float: 'abc'
```

**Причина:** Некорректный ввод пользователя

**Решение:**
```python
try:
    amount = float(message.text.split()[-1].replace(',', '.'))
    if amount <= 0:
        raise ValueError("Amount must be positive")
except (ValueError, IndexError):
    await message.answer("❌ Неверный формат! Введите: категория сумма")
    return
```

**Валидация с регулярными выражениями:**
```python
import re

def parse_transaction(text: str):
    pattern = r'^(доход|расход)\s+([а-яё\s]+)\s+(\d+(?:\.\d+)?)\s*$'
    match = re.match(pattern, text.lower().strip())
    if not match:
        return None
    return match.groups()
```

## 📊 Проблемы дашборда

### ❌ Графики не отображаются

#### Проблема: Неверные цвета в Plotly
```
ValueError: Invalid element(s) received for the 'color' property
Invalid elements include: ['positive']
```

**Причина:** Plotly ожидает конкретные цвета

**Решение:**
```python
# Было (неправильно):
colors = ['positive' if x >= 0 else 'negative' for x in data]

# Стало (правильно):
colors = ['#2E8B57' if x >= 0 else '#DC143C' for x in data]
```

**Палитра цветов:**
```python
COLOR_PALETTE = {
    'income': '#2E8B57',      # SeaGreen
    'expense': '#DC143C',     # Crimson
    'balance_positive': '#2E8B57',
    'balance_negative': '#DC143C',
    'neutral': '#1E90FF'      # DodgerBlue
}
```

#### Проблема: Пустые данные
```
KeyError: 'total' when accessing category data
```

**Причина:** Отсутствуют данные в категории

**Решение:**
```python
def safe_get_category_data(data: dict, key: str, default=0):
    """Безопасное получение данных категории"""
    try:
        return data[key].get('total', default)
    except (KeyError, AttributeError):
        return default
```

**Обработка пустых данных:**
```python
if not category_data:
    fig = go.Figure()
    fig.add_annotation(
        text="Нет данных для отображения",
        x=0.5, y=0.5, xanchor='center', yanchor='middle'
    )
    return fig
```

### ❌ Медленная загрузка

#### Проблема: Дашборд загружается слишком долго

**Причина:** Неоптимизированные запросы к БД

**Решение:**
```python
# Добавить индексы
CREATE INDEX idx_user_date ON transactions(user_id, created_at);

# Кэширование
@st.cache_data(ttl=300)  # 5 минут
def load_data(days: int):
    # загрузка данных
    pass

# Пагинация
def load_data_paginated(page: int, page_size: int = 100):
    offset = page * page_size
    # запрос с LIMIT и OFFSET
```

**Lazy loading:**
```python
# Загружать только при необходимости
@st.experimental_memo
def expensive_computation():
    return result

if st.button("Показать детальную аналитику"):
    result = expensive_computation()
    st.write(result)
```

### ❌ CSS стили не применяются

#### Проблема: Кастомные стили не работают

**Решение:**
```python
# Использовать unsafe_allow_html=True
st.markdown("""
<style>
.metric-card {
    background-color: #F9FAFB;
    padding: 1.5rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
```

**Альтернативный подход:**
```css
/* .streamlit/style.css */
.metric-card {
    background-color: #F9FAFB;
    padding: 1.5rem;
    border-radius: 10px;
}
```

## 🔒 Проблемы безопасности

### ❌ Токен бота скомпрометирован

**Признаки:**
- Неактивность бота
- Подозрительная активность
- Сообщения от незарегистрированных пользователей

**Решение:**
```bash
# 1. Получить новый токен у @BotFather
# 2. Обновить .env файл
# 3. Перезапустить бота
# 4. Отозвать старый токен
```

### ❌ Проблемы с доступом к базе данных

**Причина:** Несанкционированный доступ

**Решение:**
```python
# Шифрование БД
import sqlite3
import hashlib

def encrypt_database():
    # Шифрование файла БД
    pass

# Ограничение прав доступа
import os
os.chmod('finance_bot.db', 0o600)  # только для владельца
```

## 🔧 Диагностика и мониторинг

### 📊 Логирование

#### Настройка логирования
```python
import logging
from datetime import datetime

# Создание логгера
logger = logging.getLogger(__name__)
handler = logging.FileHandler(f'bot_{datetime.now().strftime("%Y%m%d")}.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Использование
logger.info("Bot started successfully")
logger.error(f"Error processing transaction: {error}")
```

#### Мониторинг производительности
```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f}s")
        return result
    return wrapper

@timing_decorator
async def process_transaction(user_id, data):
    # обработка транзакции
    pass
```

### 🔍 Health Checks

#### Проверка работоспособности бота
```python
async def health_check():
    """Проверка работоспособности компонентов"""
    status = {
        'database': await check_database(),
        'telegram': await check_telegram_connection(),
        'memory': check_memory_usage(),
        'disk_space': check_disk_space()
    }
    return status

async def check_database():
    """Проверка подключения к БД"""
    try:
        session = await db.get_session()
        await session.execute("SELECT 1")
        await session.close()
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False
```

### 📈 Метрики производительности

#### Сбор метрик
```python
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_response_time(self, operation: str, time_ms: float):
        self.metrics[f"{operation}_response_time"].append(time_ms)

    def record_error(self, error_type: str):
        self.metrics[f"{error_type}_errors"].append(1)

    def get_stats(self):
        stats = {}
        for key, values in self.metrics.items():
            if 'response_time' in key:
                stats[key] = {
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
            elif 'errors' in key:
                stats[key] = sum(values)
        return stats

metrics = MetricsCollector()
```

## 🆘 Экстренные ситуации

### 🔄 Восстановление после сбоя

#### Резервное копирование
```python
import shutil
from datetime import datetime
import os

def backup_database():
    """Создание резервной копии БД"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backup/finance_bot_{timestamp}.db"

    os.makedirs('backup', exist_ok=True)
    shutil.copy2('finance_bot.db', backup_path)

    # Удаление старых бэкапов (оставляем последние 10)
    backups = sorted(os.listdir('backup'))
    for backup in backups[:-10]:
        os.remove(f'backup/{backup}')

    return backup_path

# Автоматические бэкапы
import schedule
schedule.every().day.at("02:00").do(backup_database)
```

#### Восстановление из бэкапа
```python
def restore_database(backup_path: str):
    """Восстановление БД из бэкапа"""
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    shutil.copy2(backup_path, 'finance_bot.db')
    print(f"Database restored from {backup_path}")
```

### 🚨 Критические ошибки

#### Обработка глобальных ошибок
```python
import asyncio
import logging

async def main():
    try:
        # Основная логика бота
        await start_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        # Отправка уведомления администратору
        await notify_admin(f"Bot crashed: {e}")
    finally:
        # Очистка ресурсов
        await cleanup()

async def notify_admin(message: str):
    """Уведомление администратора о проблеме"""
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        await bot.send_message(admin_chat_id, f"🚨 ALERT: {message}")
```

## 📞 Поддержка и помощь

### 📝 Сбор информации об ошибках
```python
import traceback
import sys

async def handle_error(error: Exception, context: dict = None):
    """Сбор информации об ошибке для отладки"""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'context': context or {},
        'user_agent': 'Telegram Bot',
        'timestamp': datetime.now().isoformat()
    }

    # Сохранение в лог
    logger.error(f"Error details: {error_info}")

    # Отправка разработчику
    await send_error_report(error_info)
```

### 🔗 Полезные ресурсы

#### Документация
- [aiogram Documentation](https://docs.aiogram.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Plotly Documentation](https://plotly.com/python/)

#### Сообщества
- [aiogram Telegram Chat](https://t.me/aiogram)
- [Streamlit Community](https://discuss.streamlit.io/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/aiogram)
- [Reddit r/Python](https://reddit.com/r/Python)

#### Инструменты
- [Postman](https://www.postman.com/) - тестирование API
- [SQLite Browser](https://sqlitebrowser.org/) - работа с БД
- [GitKraken](https://www.gitkraken.com/) - Git клиент
- [PyCharm](https://www.jetbrains.com/pycharm/) - IDE

---

**Последнее обновление:** 2024-11-16
**Версия:** 1.0.0

---

> 💡 **Совет:** Всегда сохраняйте логи ошибок - они помогут быстро найти причину проблемы.

> 🔗 **Связанные страницы:** [[Telegram Bot]], [[Database]], [[Streamlit Dashboard]], [[Ideas and Improvements]]