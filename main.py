import asyncio
import logging
from datetime import datetime
from typing import List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import BOT_TOKEN
from database import db, TransactionRepository
from src.message_parser import MessageParser

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Временное хранилище для данных пользователей
user_temp_data = {}

# Inline клавиатуры
def get_welcome_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Добавить", callback_data="add_transaction"))
    builder.add(InlineKeyboardButton(text="💰 Баланс", callback_data="show_balance"))
    builder.add(InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats"))
    builder.adjust(2)
    return builder.as_markup()

def get_transaction_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📈 Доходы", callback_data="income"))
    builder.add(InlineKeyboardButton(text="📉 Расходы", callback_data="expense"))
    builder.adjust(2)
    return builder.as_markup()

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Занести", callback_data="confirm_transaction"))
    builder.add(InlineKeyboardButton(text="✏️ Изменить", callback_data="change_transaction"))
    builder.adjust(2)
    return builder.as_markup()

def get_transaction_list_keyboard(transactions: List) -> InlineKeyboardMarkup:
    """Создать клавиатуру со списком транзакций"""
    builder = InlineKeyboardBuilder()

    for i, trans in enumerate(transactions, 1):
        type_emoji = "📈" if trans.transaction_type == 'income' else "📉"
        type_text = "Доход" if trans.transaction_type == 'income' else "Расход"
        button_text = f"{i}. {type_emoji} {type_text}: {trans.category} - {trans.amount:,.2f}₽"
        builder.add(InlineKeyboardButton(text=button_text, callback_data=f"edit_transaction_{trans.id}"))

    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    builder.adjust(1)  # Каждая кнопка на новой строке для лучшей читаемости
    return builder.as_markup()

def get_edit_transaction_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру для редактирования транзакции"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✏️ Категория", callback_data=f"edit_category_{transaction_id}"))
    builder.add(InlineKeyboardButton(text="💰 Сумма", callback_data=f"edit_amount_{transaction_id}"))
    builder.add(InlineKeyboardButton(text="🔄 Тип", callback_data=f"edit_type_{transaction_id}"))
    builder.add(InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_transaction_{transaction_id}"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="show_transactions"))
    builder.adjust(2)
    return builder.as_markup()

# Клавиатура
def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="/balance"))
    builder.add(KeyboardButton(text="/stats"))
    builder.add(KeyboardButton(text="/history"))
    builder.add(KeyboardButton(text="/help"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

async def send_welcome(message: Message):
    """Обработчик команды /start"""
    welcome_text = """
👋 Добро пожаловать в финансового бота!

Я помогу вам вести учет доходов и расходов через удобный интерфейс.

Выберите действие ниже 👇
    """
    await message.answer(welcome_text, reply_markup=get_welcome_keyboard())

async def send_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Справка по использованию бота</b>

📝 <b>Добавление транзакций:</b>
• <code>доход [категория] [сумма]</code>
  Пример: <code>доход зарплата 100000</code>
• <code>расход [категория] [сумма]</code>
  Пример: <code>расход еда 1500</code>

📊 <b>Команды:</b>
• <code>/balance</code> - Показать текущий баланс
• <code>/stats</code> - Статистика по категориям
• <code>/history</code> - История транзакций
• <code>/help</code> - Показать эту справку

💡 <b>Советы:</b>
• Используйте понятные названия категорий
• Можно использовать целые и дробные числа
• Десятичный разделитель - точка или запятая
    """
    await message.answer(help_text, parse_mode=ParseMode.HTML)

async def show_balance(message: Message):
    """Показать баланс пользователя"""
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        balance_data = await repo.get_user_balance(message.from_user.id)

        balance_text = f"""
💰 <b>Ваш финансовый баланс</b>

📈 Доходы: {balance_data['total_income']:,.2f} ₽
📉 Расходы: {balance_data['total_expense']:,.2f} ₽
💵 Баланс: {balance_data['balance']:,.2f} ₽
        """
        await message.answer(balance_text, parse_mode=ParseMode.HTML)
    finally:
        await session.close()

async def show_stats(message: Message):
    """Показать статистику по категориям"""
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        stats = await repo.get_category_statistics(message.from_user.id)

        if not stats['income'] and not stats['expense']:
            await message.answer("📊 У вас пока нет статистики. Добавьте свои первые доходы и расходы!")
            return

        stats_text = "📊 <b>Статистика за последние 30 дней</b>\n\n"

        if stats['income']:
            stats_text += "📈 <b>Доходы по категориям:</b>\n"
            for category, data in stats['income'].items():
                stats_text += f"  • {category}: {data.total:,.2f} ₽ ({data.count} шт.)\n"

        if stats['expense']:
            stats_text += "\n📉 <b>Расходы по категориям:</b>\n"
            for category, data in stats['expense'].items():
                stats_text += f"  • {category}: {data.total:,.2f} ₽ ({data.count} шт.)\n"

        await message.answer(stats_text, parse_mode=ParseMode.HTML)
    finally:
        await session.close()

async def show_history(message: Message):
    """Показать историю транзакций"""
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        transactions = await repo.get_user_transactions(message.from_user.id, days=10)

        if not transactions:
            await message.answer("📜 У вас пока нет транзакций. Добавьте свои первые доходы и расходы!")
            return

        history_text = "📜 <b>Последние транзакции:</b>\n\n"

        for trans in transactions[:15]:  # Показываем последние 15
            type_emoji = "📈" if trans.transaction_type == 'income' else "📉"
            type_text = "Доход" if trans.transaction_type == 'income' else "Расход"
            date_str = trans.created_at.strftime("%d.%m %H:%M")

            history_text += f"{type_emoji} <b>{type_text}</b> - {trans.category}\n"
            history_text += f"💵 {trans.amount:,.2f} ₽ | 📅 {date_str}\n\n"

        await message.answer(history_text, parse_mode=ParseMode.HTML)
    finally:
        await session.close()

async def handle_transaction(message: Message):
    """Обработка сообщений с транзакциями"""
    parsed = MessageParser.parse_transaction(message.text)

    if not parsed:
        await message.answer(
            "❌ Не удалось распознать команду. Пожалуйста, используйте формат:\n"
            "• `доходы [категория] [сумма]`\n"
            "• `расходы [категория] [сумма]`\n\n"
            "Пример: `доходы зарплата 100000`",
            reply_markup=get_main_keyboard()
        )
        return

    transaction_type, category, amount = parsed

    session = await db.get_session()
    try:
        repo = TransactionRepository(session)

        try:
            await repo.add_transaction(
                user_id=message.from_user.id,
                transaction_type=transaction_type,
                category=category,
                amount=amount
            )

            type_emoji = "📈" if transaction_type == 'income' else "📉"
            type_text = "доход" if transaction_type == 'income' else "расход"

            success_text = (
                f"{type_emoji} <b>{type_text.capitalize()} успешно добавлен!</b>\n\n"
                f"📂 Категория: {category}\n"
                f"💰 Сумма: {amount:,.2f} ₽\n"
                f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )

            await message.answer(success_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            await message.answer(
                "❌ Произошла ошибка при сохранении транзакции. Пожалуйста, попробуйте позже."
            )
    finally:
        await session.close()

# Обработчики inline кнопок
async def callback_add_transaction(callback: CallbackQuery):
    """Обработка кнопки 'Добавить'"""
    await callback.answer()
    text = "Выберите тип транзакции:"
    await callback.message.edit_text(text, reply_markup=get_transaction_type_keyboard())

async def callback_transaction_type(callback: CallbackQuery):
    """Обработка выбора типа транзакции (доход/расход)"""
    await callback.answer()
    user_id = callback.from_user.id

    # Сохраняем тип транзакции
    user_temp_data[user_id] = {'type': callback.data}

    type_text = "доход" if callback.data == "income" else "расход"
    text = f"Вы выбрали {type_text}.\n\nТеперь введите категорию и сумму через пробел:\nПример: `зарплата 100000`"

    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)

async def callback_confirm_transaction(callback: CallbackQuery):
    """Обработка подтверждения транзакции"""
    await callback.answer()
    user_id = callback.from_user.id

    if user_id not in user_temp_data:
        await callback.message.edit_text("❌ Ошибка! Данные не найдены. Начните заново.")
        return

    data = user_temp_data[user_id]
    transaction_type = data['type']
    category = data['category']
    amount = data['amount']

    # Сохраняем в базу данных
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        await repo.add_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            category=category,
            amount=amount
        )

        type_emoji = "📈" if transaction_type == 'income' else "📉"
        type_text = "доход" if transaction_type == 'income' else "расход"

        success_text = (
            f"{type_emoji} <b>{type_text.capitalize()} успешно добавлен!</b>\n\n"
            f"📂 Категория: {category}\n"
            f"💰 Сумма: {amount:,.2f} ₽\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        # Очищаем временные данные
        del user_temp_data[user_id]

        await callback.message.edit_text(success_text, parse_mode=ParseMode.HTML,
                                       reply_markup=get_welcome_keyboard())

    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при сохранении транзакции.")
    finally:
        await session.close()

async def callback_change_transaction(callback: CallbackQuery):
    """Обработка кнопки 'Изменить'"""
    await callback.answer()
    user_id = callback.from_user.id

    # Возвращаем к выбору типа транзакции
    if user_id in user_temp_data:
        del user_temp_data[user_id]

    text = "Выберите тип транзакции:"
    await callback.message.edit_text(text, reply_markup=get_transaction_type_keyboard())

async def callback_show_balance(callback: CallbackQuery):
    """Показать баланс через callback"""
    await callback.answer()
    user_id = callback.from_user.id

    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        balance_data = await repo.get_user_balance(user_id)

        balance_text = f"""
💰 <b>Ваш финансовый баланс</b>

📈 Доходы: {balance_data['total_income']:,.2f} ₽
📉 Расходы: {balance_data['total_expense']:,.2f} ₽
💵 Баланс: {balance_data['balance']:,.2f} ₽
        """
        await callback.message.edit_text(balance_text, parse_mode=ParseMode.HTML,
                                       reply_markup=get_welcome_keyboard())
    finally:
        await session.close()

async def callback_show_stats(callback: CallbackQuery):
    """Показать список транзакций для редактирования"""
    await callback.answer()
    user_id = callback.from_user.id

    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        transactions = await repo.get_all_user_transactions(user_id, days=30)

        if not transactions:
            await callback.message.edit_text("📊 У вас пока нет транзакций. Добавьте свои первые доходы и расходы!",
                                           reply_markup=get_welcome_keyboard())
            return

        text = "📊 <b>Ваши транзакции (последние 30 дней):</b>\n\n"
        text += "Выберите транзакцию для редактирования:"

        await callback.message.edit_text(text, parse_mode=ParseMode.HTML,
                                       reply_markup=get_transaction_list_keyboard(transactions))
    finally:
        await session.close()

# Обработчики для редактирования транзакций
async def callback_edit_transaction(callback: CallbackQuery):
    """Обработка выбора транзакции для редактирования"""
    logger.info(f"Edit transaction callback: {callback.data}")
    await callback.answer()
    user_id = callback.from_user.id
    transaction_id = int(callback.data.split('_')[-1])

    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        transactions = await repo.get_all_user_transactions(user_id, days=30)

        # Находим нужную транзакцию
        transaction = None
        for trans in transactions:
            if trans.id == transaction_id:
                transaction = trans
                break

        if not transaction:
            await callback.message.edit_text("❌ Транзакция не найдена!",
                                           reply_markup=get_welcome_keyboard())
            return

        type_emoji = "📈" if transaction.transaction_type == 'income' else "📉"
        type_text = "Доход" if transaction.transaction_type == 'income' else "Расход"

        text = f"📝 <b>Редактирование транзакции</b>\n\n"
        text += f"{type_emoji} {type_text}\n"
        text += f"📂 Категория: {transaction.category}\n"
        text += f"💰 Сумма: {transaction.amount:,.2f} ₽\n"
        text += f"📅 Дата: {transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        text += f"Что хотите изменить?"

        await callback.message.edit_text(text, parse_mode=ParseMode.HTML,
                                       reply_markup=get_edit_transaction_keyboard(transaction_id))
    finally:
        await session.close()

async def callback_back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.answer()
    text = "👋 Добро пожаловать в финансового бота!\n\nВыберите действие ниже 👇"
    await callback.message.edit_text(text, reply_markup=get_welcome_keyboard())

async def callback_back_to_transactions(callback: CallbackQuery):
    """Возврат к списку транзакций"""
    await callback.answer()
    user_id = callback.from_user.id

    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        transactions = await repo.get_all_user_transactions(user_id, days=30)

        if not transactions:
            await callback.message.edit_text("📊 У вас пока нет транзакций.",
                                           reply_markup=get_welcome_keyboard())
            return

        text = "📊 <b>Ваши транзакции:</b>\n\nВыберите транзакцию для редактирования:"
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML,
                                       reply_markup=get_transaction_list_keyboard(transactions))
    finally:
        await session.close()

async def callback_edit_field(callback: CallbackQuery):
    """Обработка нажатия на кнопки редактирования полей"""
    logger.info(f"Received callback: {callback.data}")
    await callback.answer()
    user_id = callback.from_user.id
    data = callback.data.split('_')

    if callback.data.startswith("delete_transaction_"):
        field = 'delete'
        transaction_id = int(data[2])
    else:
        field = data[1]  # category, amount, type
        transaction_id = int(data[2])

    if field == 'delete':
        # Удаление транзакции
        session = await db.get_session()
        try:
            repo = TransactionRepository(session)
            success = await repo.delete_transaction(transaction_id, user_id)

            if success:
                await callback.message.edit_text("✅ Транзакция успешно удалена!",
                                               reply_markup=get_welcome_keyboard())
            else:
                await callback.message.edit_text("❌ Не удалось удалить транзакцию!",
                                               reply_markup=get_welcome_keyboard())
        finally:
            await session.close()
    else:
        # Сохраняем данные для редактирования
        user_temp_data[user_id] = {
            'edit_mode': True,
            'transaction_id': transaction_id,
            'edit_field': field
        }

        field_names = {
            'category': 'категорию',
            'amount': 'сумму',
            'type': 'тип (доход/расход)'
        }

        instructions = {
            'category': 'Введите новую категорию:',
            'amount': 'Введите новую сумму (только число):',
            'type': 'Введите новый тип: income или expense'
        }

        await callback.message.edit_text(
            f"✏️ <b>Редактирование {field_names[field]}</b>\n\n{instructions[field]}"
        )

# Обработчики ввода категории и суммы
async def handle_category_amount(message: Message):
    """Обработка ввода категории и суммы или редактирования транзакции"""
    user_id = message.from_user.id

    # Проверяем, это режим редактирования или добавления
    if user_id in user_temp_data and user_temp_data[user_id].get('edit_mode'):
        # Режим редактирования
        edit_data = user_temp_data[user_id]
        transaction_id = edit_data['transaction_id']
        field = edit_data['edit_field']
        new_value = message.text.strip()

        session = await db.get_session()
        try:
            repo = TransactionRepository(session)

            # Валидация и преобразование данных
            update_data = {}

            if field == 'category':
                update_data['category'] = new_value
            elif field == 'amount':
                try:
                    amount = float(new_value.replace(',', '.'))
                    if amount <= 0:
                        await message.answer("❌ Сумма должна быть положительной!")
                        return
                    update_data['amount'] = amount
                except ValueError:
                    await message.answer("❌ Неверный формат суммы! Введите число.")
                    return
            elif field == 'type':
                if new_value.lower() in ['доход', 'income']:
                    update_data['transaction_type'] = 'income'
                elif new_value.lower() in ['расход', 'expense']:
                    update_data['transaction_type'] = 'expense'
                else:
                    await message.answer("❌ Неверный тип! Введите: доход или income (или расход/expense)")
                    return

            # Обновляем транзакцию
            success = await repo.update_transaction(transaction_id, user_id, **update_data)

            if success:
                await message.answer("✅ Транзакция успешно обновлена!")
                del user_temp_data[user_id]
            else:
                await message.answer("❌ Не удалось обновить транзакцию!")

        finally:
            await session.close()

    elif user_id in user_temp_data and 'type' in user_temp_data[user_id]:
        # Режим добавления транзакции
        # Парсим введенные данные
        parts = message.text.strip().split()

        if len(parts) < 2:
            await message.answer("❌ Неверный формат! Введите: `категория сумма`\nПример: `зарплата 100000`")
            return

        try:
            category = ' '.join(parts[:-1])  # Категория может содержать пробелы
            amount = float(parts[-1].replace(',', '.'))

            if amount <= 0:
                await message.answer("❌ Сумма должна быть положительной!")
                return

            # Сохраняем данные
            user_temp_data[user_id]['category'] = category
            user_temp_data[user_id]['amount'] = amount

            transaction_type = user_temp_data[user_id]['type']
            type_text = "доход" if transaction_type == 'income' else "расход"

            confirm_text = (
                f"🔍 <b>Подтверждение транзакции</b>\n\n"
                f"Тип: {type_text.capitalize()}\n"
                f"Категория: {category}\n"
                f"Сумма: {amount:,.2f} ₽\n\n"
                f"Подтверждаете добавление?"
            )

            await message.answer(confirm_text, parse_mode=ParseMode.HTML,
                               reply_markup=get_confirmation_keyboard())

        except ValueError:
            await message.answer("❌ Неверный формат суммы! Введите число.\nПример: `зарплата 100000`")

async def main():
    """Основная функция запуска бота"""
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Инициализация базы данных
    await db.init_db()

    # Регистрация обработчиков сообщений
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_help, Command("help"))
    dp.message.register(show_balance, Command("balance"))
    dp.message.register(show_stats, Command("stats"))
    dp.message.register(show_history, Command("history"))

    # Обработчик ввода категории и суммы (должен идти последним)
    dp.message.register(handle_category_amount)

    # Регистрация обработчиков inline кнопок
    dp.callback_query.register(callback_add_transaction, F.data == "add_transaction")
    dp.callback_query.register(callback_show_balance, F.data == "show_balance")
    dp.callback_query.register(callback_show_stats, F.data == "show_stats")
    dp.callback_query.register(callback_transaction_type, F.data.in_(["income", "expense"]))
    dp.callback_query.register(callback_confirm_transaction, F.data == "confirm_transaction")
    dp.callback_query.register(callback_change_transaction, F.data == "change_transaction")

    # Регистрация обработчиков редактирования
    dp.callback_query.register(callback_edit_transaction, F.data.startswith("edit_transaction_"))
    dp.callback_query.register(callback_edit_field, F.data.startswith("edit_category_"))
    dp.callback_query.register(callback_edit_field, F.data.startswith("edit_amount_"))
    dp.callback_query.register(callback_edit_field, F.data.startswith("edit_type_"))
    dp.callback_query.register(callback_edit_field, F.data.startswith("delete_transaction_"))
    dp.callback_query.register(callback_back_to_menu, F.data == "back_to_menu")
    dp.callback_query.register(callback_back_to_transactions, F.data == "show_transactions")

    # Обработка транзакций (старый способ, оставляем для совместимости)
    dp.message.register(handle_transaction,
                       lambda msg: MessageParser.is_transaction_message(msg.text))

    # Запуск бота
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")