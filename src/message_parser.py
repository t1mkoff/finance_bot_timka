import re
from typing import Optional, Tuple

class MessageParser:
    """Парсер для обработки сообщений о транзакциях"""

    @staticmethod
    def parse_transaction(message: str) -> Optional[Tuple[str, str, float]]:
        """
        Парсит сообщение и возвращает кортеж (тип, категория, сумма)
        Примеры:
        - "доходы зарплата 100000" -> ("income", "зарплата", 100000.0)
        - "расходы еда 1500" -> ("expense", "еда", 1500.0)
        - "доход продажа 50000" -> ("income", "продажа", 50000.0)
        """
        message = message.lower().strip()

        # Регулярное выражение для парсинга
        pattern = r'^(доход|доходы|расход|расходы)\s+([а-яё0-9\s]+)\s+(\d+(?:[.,]\d+)?)\s*$'
        match = re.match(pattern, message, re.IGNORECASE)

        if not match:
            return None

        transaction_type_raw, category_raw, amount_raw = match.groups()

        # Определяем тип транзакции
        if transaction_type_raw in ['доход', 'доходы']:
            transaction_type = 'income'
        elif transaction_type_raw in ['расход', 'расходы']:
            transaction_type = 'expense'
        else:
            return None

        # Очищаем категорию от лишних пробелов
        category = category_raw.strip()

        # Конвертируем сумму в float
        try:
            amount = float(amount_raw.replace(',', '.'))
        except ValueError:
            return None

        # Валидация
        if amount <= 0:
            return None

        if not category:
            return None

        return transaction_type, category, amount

    @staticmethod
    def is_transaction_message(message: str) -> bool:
        """Проверяет, является ли сообщение транзакцией"""
        return MessageParser.parse_transaction(message) is not None