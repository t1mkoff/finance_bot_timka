# 🗄️ База Данных Финансового Бота

## 📋 Обзор

База данных для хранения финансовых транзакций пользователей, построенная на SQLite с использованием SQLAlchemy ORM. Легковесное, но мощное решение для учета личных финансов.

## 🏗️ Архитектура

### Технологический стек

- **SQLite** - встраиваемая база данных
- **SQLAlchemy 2.0.31** - ORM и работа с БД
- **aiosqlite 0.20.0** - асинхронный драйвер SQLite
- **asyncio** - асинхронные операции

### Структура файлов

```
database/
├── __init__.py                  # Экспорт модулей
├── database.py                 # Модель данных и подключение
└── transaction_repository.py   # Репозиторий для операций
```

## 📊 Модель данных

### Таблица `transactions`

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    category VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Поля таблицы

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTOINCREMENT |
| `user_id` | INTEGER | ID пользователя Telegram | NOT NULL, INDEXED |
| `transaction_type` | VARCHAR(10) | Тип транзакции | NOT NULL, CHECK IN ('income', 'expense') |
| `category` | VARCHAR(100) | Категория операции | NOT NULL |
| `amount` | FLOAT | Сумма операции | NOT NULL, CHECK (> 0) |
| `description` | TEXT | Дополнительное описание | Nullable |
| `created_at` | DATETIME | Дата создания | DEFAULT CURRENT_TIMESTAMP |

### Индексы

```sql
-- Индекс для быстрого поиска по пользователю
CREATE INDEX idx_transactions_user_id ON transactions(user_id);

-- Индекс для быстрой сортировки по дате
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-- Композитный индекс для фильтрации
CREATE INDEX idx_transactions_user_date ON transactions(user_id, created_at);
```

## 🔧 SQLAlchemy Модель

### Transaction Model (`database.py`)

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Telegram user_id
    transaction_type = Column(String)      # 'income' или 'expense'
    category = Column(String)              # Категория транзакции
    amount = Column(Float)                 # Сумма
    description = Column(String)           # Дополнительное описание
    created_at = Column(DateTime, default=func.now())
```

### Database Configuration

```python
class Database:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./finance_bot.db"):
        self.engine = create_async_engine(database_url)
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init_db(self):
        """Создание таблиц при первом запуске"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """Получить сессию для работы с БД"""
        return self.async_session()
```

## 📦 Transaction Repository

### Основные операции (`transaction_repository.py`)

#### CRUD Operations

```python
class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_transaction(
        self,
        user_id: int,
        transaction_type: str,
        category: str,
        amount: float,
        description: Optional[str] = None
    ) -> Transaction:
        """Добавить новую транзакцию"""

    async def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        category: str = None,
        amount: float = None,
        transaction_type: str = None
    ) -> bool:
        """Обновить существующую транзакцию"""

    async def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Удалить транзакцию"""
```

#### Аналитические запросы

```python
async def get_user_balance(self, user_id: int) -> dict:
    """Получить баланс пользователя"""
    # Возвращает: total_income, total_expense, balance

async def get_category_statistics(
    self,
    user_id: int,
    days: int = 30
) -> dict:
    """Статистика по категориям"""
    # Возвращает: income: {category: {total, count}}, expense: {...}

async def get_user_transactions(
    self,
    user_id: int,
    days: int = 30
) -> List[Transaction]:
    """Получить транзакции пользователя"""

async def get_all_user_transactions(
    self,
    user_id: int,
    days: int = 30
) -> List[Transaction]:
    """Все транзакции с ID для редактирования"""
```

## 🔄 Асинхронная работа с БД

### Шаблон использования сессии

```python
async def database_operation(user_id: int):
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        result = await repo.some_operation(user_id)
        return result
    finally:
        await session.close()
```

### Контекстный менеджер (альтернативный подход)

```python
# Можем добавить в будущем context manager:
@contextmanager
async def get_db_session():
    session = await db.get_session()
    try:
        yield session
    finally:
        await session.close()

# Использование:
async with get_db_session() as session:
    repo = TransactionRepository(session)
    result = await repo.some_operation()
```

## 📊 Запросы и оптимизации

### Типовые запросы

#### Баланс пользователя
```sql
SELECT
    SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
    SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense
FROM transactions
WHERE user_id = ?;
```

#### Статистика по категориям
```sql
SELECT
    category,
    SUM(amount) as total,
    COUNT(id) as count,
    AVG(amount) as avg_amount
FROM transactions
WHERE user_id = ?
    AND transaction_type = ?
    AND created_at >= ?
GROUP BY category
ORDER BY total DESC;
```

#### Последние транзакции
```sql
SELECT *
FROM transactions
WHERE user_id = ?
    AND created_at >= ?
ORDER BY created_at DESC
LIMIT ?;
```

### Оптимизации производительности

#### Индексы
```sql
-- Основные индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_user_type_date ON transactions(user_id, transaction_type, created_at);
CREATE INDEX IF NOT EXISTS idx_category_amount ON transactions(category, amount DESC);
```

#### Композитные запросы
```python
# Получение всех данных за один запрос
async def get_user_dashboard_data(user_id: int, days: int = 30):
    """Получение всех данных для дашборда за один запрос"""
    date_from = datetime.now() - timedelta(days=days)

    # Balance query
    balance_query = select(
        func.sum(case((Transaction.transaction_type == 'income', Transaction.amount), else_=0)).label('income'),
        func.sum(case((Transaction.transaction_type == 'expense', Transaction.amount), else_=0)).label('expense')
    ).where(and_(
        Transaction.user_id == user_id,
        Transaction.created_at >= date_from
    ))

    # Category stats query
    category_query = select(
        Transaction.transaction_type,
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).where(and_(
        Transaction.user_id == user_id,
        Transaction.created_at >= date_from
    )).group_by(Transaction.transaction_type, Transaction.category)
```

## 🔍 Аналитические функции

### Статистические запросы

```python
async def get_monthly_trends(self, user_id: int, months: int = 6):
    """Месячные тренды"""
    query = select(
        func.strftime('%Y-%m', Transaction.created_at).label('month'),
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).where(and_(
        Transaction.user_id == user_id,
        Transaction.created_at >= datetime.now() - timedelta(days=30*months)
    )).group_by(
        func.strftime('%Y-%m', Transaction.created_at),
        Transaction.transaction_type
    )

async def get_top_categories(self, user_id: int, transaction_type: str, limit: int = 10):
    """Топ категории по сумме"""
    query = select(
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).where(and_(
        Transaction.user_id == user_id,
        Transaction.transaction_type == transaction_type
    )).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(limit)
```

## 🛠️ Миграции и версия базы данных

### Текущая схема (v1.0)

```sql
-- Версия 1.0 - Базовая функциональность
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    category VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
```

### Планируемые миграции

#### v1.1 - Бюджеты и лимиты
```sql
ALTER TABLE transactions ADD COLUMN budget_id INTEGER;
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount_limit FLOAT NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'monthly', 'weekly', 'yearly'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### v1.2 - Теги и метки
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#000000'
);

CREATE TABLE transaction_tags (
    transaction_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (transaction_id, tag_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
```

#### v1.3 - Валюты
```sql
ALTER TABLE transactions ADD COLUMN currency VARCHAR(3) DEFAULT 'RUB';
ALTER TABLE transactions ADD COLUMN original_amount FLOAT;
ALTER TABLE transactions ADD COLUMN exchange_rate FLOAT DEFAULT 1.0;

CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL,
    rate FLOAT NOT NULL,
    date DATE NOT NULL
);
```

## 🔗 Интеграции

### с Telegram ботом
```python
# Использование в main.py
async def handle_transaction(message: Message):
    session = await db.get_session()
    try:
        repo = TransactionRepository(session)
        transaction = await repo.add_transaction(
            user_id=message.from_user.id,
            transaction_type=transaction_type,
            category=category,
            amount=amount
        )
    finally:
        await session.close()
```

### со Streamlit дашбордом
```python
# Использование в data_loader.py
class DataLoader:
    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect("finance_bot.db")

    def load_all_transactions(self, days: int = 30) -> pd.DataFrame:
        query = """
        SELECT id, user_id, transaction_type, category, amount, created_at
        FROM transactions
        WHERE created_at >= ?
        ORDER BY created_at DESC
        """
        return pd.read_sql_query(query, conn, params=(date_from,))
```

## 📈 Мониторинг производительности

### Метрики для отслеживания
- **Время ответа запросов** - среднее время выполнения
- **Количество запросов** - нагрузка на БД
- **Размер базы данных** - рост со временем
- **Индексное использование** - эффективность индексов

### Оптимизация запросов
```python
# Использование EXPLAIN QUERY PLAN
async def analyze_query_performance():
    """Анализ производительности запросов"""
    explain_query = "EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE user_id = ?"
    # Анализ плана выполнения запроса
```

## 🔐 Безопасность данных

### Защита от SQL Injection
- Использование SQLAlchemy ORM (parameterized queries)
- Валидация входных данных
- Ограничение прав доступа

### Резервное копирование
```python
import shutil
from datetime import datetime

def backup_database():
    """Резервное копирование базы данных"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"finance_bot_backup_{timestamp}.db"
    shutil.copy2('finance_bot.db', backup_path)
    return backup_path

# Планировщик резервных копий
import schedule
schedule.every().day.at("02:00").do(backup_database)
```

## 🚀 Масштабирование

### От SQLite к PostgreSQL
```python
# Конфигурация для PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/finance_bot"

# Изменения в Database классе
class Database:
    def __init__(self, database_url: str = "postgresql+asyncpg://localhost/finance_bot"):
        self.engine = create_async_engine(database_url)
        # ... остальной код без изменений
```

### Кэширование
```python
import redis
from functools import wraps

def cache_result(expire_time: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Кэширование результатов запросов
            pass
        return wrapper
    return decorator

@cache_result(expire_time=300)
async def get_user_balance_cached(user_id: int):
    """Кэшированный запрос баланса"""
```

## 🔮 Будущие улучшения

### Архитектурные улучшения
- [ ] **Connection Pooling** - пул соединений с БД
- [ ] **Read Replicas** - реплики для чтения аналитических запросов
- [ ] **Sharding** - разделение данных по пользователям
- [ ] **Time Series DB** - для аналитических данных

### Функциональные улучшения
- [ ] **Data Warehousing** - хранилище для аналитики
- [ ] **ETL Processes** - обработка и трансформация данных
- [ ] **Real-time Analytics** - анализ в реальном времени
- [ ] **Machine Learning** - прогнозирование и рекомендации

### Улучшения производительности
- [ ] **Query Optimization** - оптимизация медленных запросов
- [ ] **Indexing Strategy** - стратегия индексации
- [ ] **Caching Layer** - многоуровневое кэширование
- [ ] **Async Processing** - фоновая обработка данных

## 🔗 Связанные компоненты

- [[Telegram Bot]] - Основное приложение использующее БД
- [[Streamlit Dashboard]] - Визуализация данных из БД
- [[API]] - REST API для доступа к данным (в разработке)
- [[Data Analysis]] - Аналитические запросы и отчеты

---

**Теги:** `database` `sqlite` `sqlalchemy` `async` `orm` `finance` `data-model` `repository-pattern`