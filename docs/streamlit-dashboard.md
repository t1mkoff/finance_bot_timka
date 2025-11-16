# 📊 Streamlit Финансовый Дашборд

## 📋 Обзор

Интерактивный веб-дашборд для визуализации финансовых данных из Telegram бота. Построен на Streamlit с использованием Plotly для создания красивых и интерактивных графиков. Предоставляет детальный анализ доходов, расходов и финансовых трендов.

## 🏗️ Архитектура

### Технологический стек

- **Streamlit 1.39.0** - фреймворк для веб-приложений
- **Plotly 5.24.1** - интерактивные графики и диаграммы
- **Pandas 2.2.3** - обработка и анализ данных
- **SQLite** - база данных (та же, что и у Telegram бота)
- **Python 3.8+** - основной язык разработки

### Структура проекта

```
dashboard/
├── app.py                 # Основное приложение Streamlit
├── data_loader.py         # Загрузка и подготовка данных
├── charts.py              # Создание графиков и диаграмм
├── run_dashboard.py       # Скрипт для запуска
└── README.md              # Документация
```

## 🎯 Функциональность

### Основные возможности

#### 📊 Финансовые метрики
- **Общие доходы и расходы** с количеством транзакций
- **Текущий баланс** и процент экономии
- **Средние значения** на транзакцию
- **Агрегированная статистика** за выбранный период

#### 📈 Визуализация данных
- **Временные ряды** - дневные, недельные, месячные тренды
- **Категориальный анализ** - круговые и столбчатые диаграммы
- **Сравнительный анализ** - доходы vs расходы
- **Топ категории** - самые прибыльные/затратные направления

#### 🎛️ Интерактивность
- **Выбор периода** - 7 дней, 30 дней, 90 дней, год
- **Интерактивные графики** - hover эффекты, zoom, фильтры
- **Адаптивный дизайн** - работает на разных устройствах
- **Real-time данные** - автоматическое обновление

## 🎨 UI/UX Дизайн

### Основные экраны

#### Главная панель метрик
```
💰 Общие доходы    💸 Общие расходы    💵 Баланс
📈 Средний доход   📉 Средний расход   📊 Всего транзакций
```

#### Вкладки с графиками
1. **🕐 Динамика** - временные тренды
2. **🥧 Категории** - распределение по категориям
3. **🏆 Топ категории** - лидеры по суммам
4. **⚖️ Сравнения** - сравнительный анализ

### Цветовая схема
- **🟢 #2E8B57** - доходы (SeaGreen)
- **🔴 #DC143C** - расходы (Crimson)
- **🔵 #1E90FF** - баланс (DodgerBlue)
- **⚪ #FFFFFF** - акценты и рамки

### Стилизация
```css
.metric-card {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.5rem;
}

.chart-container {
    background-color: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1rem;
}
```

## 📊 Загрузка и обработка данных

### DataLoader Class (`data_loader.py`)

#### Основные методы
```python
class DataLoader:
    def __init__(self, db_path: str = "finance_bot.db"):
        self.db_path = db_path

    def load_all_transactions(self, days: int = 30) -> pd.DataFrame:
        """Загрузка всех транзакций за период"""

    def get_summary_stats(self, days: int = 30) -> Dict:
        """Основные финансовые показатели"""

    def get_category_stats(self, days: int = 30) -> Dict:
        """Статистика по категориям"""

    def get_daily_totals(self, days: int = 30) -> pd.DataFrame:
        """Дневные итоги для графиков"""

    def get_top_categories(self, transaction_type: str, days: int = 30) -> pd.DataFrame:
        """Топ категории по суммам"""
```

### Обработка данных
```python
# Добавление временных колонок
df['date'] = df['created_at'].dt.date
df['week'] = df['created_at'].dt.isocalendar().week
df['month'] = df['created_at'].dt.to_period('M')

# Агрегация данных
daily_totals = df.groupby(['date', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

# Фильтрация и сортировка
top_categories = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(10)
```

## 📈 Создание графиков

### ChartCreator Class (`charts.py`)

#### Типы графиков
```python
class ChartCreator:
    @staticmethod
    def create_daily_trend_chart(daily_data: pd.DataFrame) -> go.Figure:
        """Дневные тренды с subplots"""

    @staticmethod
    def create_category_pie_chart(category_data: Dict, transaction_type: str) -> go.Figure:
        """Круговая диаграмма распределения"""

    @staticmethod
    def create_top_categories_bar_chart(top_data: pd.DataFrame, transaction_type: str) -> go.Figure:
        """Столбчатая диаграмма топ категорий"""

    @staticmethod
    def create_comparison_chart(category_stats: Dict) -> go.Figure:
        """Сравнительная диаграмма доходов и расходов"""

    @staticmethod
    def create_weekly_trend_chart(weekly_data: pd.DataFrame) -> go.Figure:
        """Недельные тренды"""

    @staticmethod
    def create_monthly_trend_chart(monthly_data: pd.DataFrame) -> go.Figure:
        """Месячные тренды с subplots"""
```

#### Пример создания сложного графика
```python
@staticmethod
def create_daily_trend_chart(daily_data: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Дневные доходы и расходы', 'Дневной баланс'),
        vertical_spacing=0.15
    )

    # График доходов и расходов
    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['income'],
                   mode='lines+markers', name='Доходы',
                   line=dict(color='#2E8B57', width=3)),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['expense'],
                   mode='lines+markers', name='Расходы',
                   line=dict(color='#DC143C', width=3),
                   fill='tonexty', fillcolor='rgba(220, 20, 60, 0.1)'),
        row=1, col=1
    )

    # График баланса с цветовой кодировкой
    colors = ['#2E8B57' if x >= 0 else '#DC143C' for x in daily_data['balance']]
    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['balance'],
                   mode='lines+markers', name='Баланс',
                   line=dict(width=3), marker=dict(color=colors, size=8)),
        row=2, col=1
    )

    return fig
```

## 🎮 Основное приложение (app.py)

### Структура приложения
```python
# Конфигурация страницы
st.set_page_config(
    page_title="Финансовый дашборд",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кэширование данных
@st.cache_data(ttl=300)
def load_data(days: int):
    """Кэшированная загрузка данных"""
    loader = DataLoader()
    return {
        'summary': loader.get_summary_stats(days),
        'category_stats': loader.get_category_stats(days),
        'daily_data': loader.get_daily_totals(days),
        # ... другие данные
    }

# Основная логика
def main():
    # Заголовок
    # Боковая панель с настройками
    # Метрики
    # Графики (вкладки)
    # Таблица транзакций
```

### Компоненты интерфейса

#### Метрики
```python
def create_metric_card(title: str, value: str, delta: str = None, color: str = "black"):
    return f"""
    <div class='metric-card'>
        <h3>{title}</h3>
        <p class='metric-value' style='color: {color};'>{value}</p>
        <p>{delta}</p>
    </div>
    """

# Использование
st.markdown(create_metric_card(
    "💰 Общие доходы",
    format_currency(summary['total_income']),
    f"Транзакций: {summary['income_count']}",
    "#059669"
), unsafe_allow_html=True)
```

#### Вкладки с графиками
```python
tab1, tab2, tab3, tab4 = st.tabs(["🕐 Динамика", "🥧 Категории", "🏆 Топ категорий", "📅 Сравнения"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Дневная динамика")
        daily_chart = ChartCreator.create_daily_trend_chart(data['daily_data'])
        st.plotly_chart(daily_chart, use_container_width=True)

    with col2:
        st.subheader("📆 Недельные тренды")
        weekly_chart = ChartCreator.create_weekly_trend_chart(data['weekly_data'])
        st.plotly_chart(weekly_chart, use_container_width=True)
```

### Боковая панель
```python
st.sidebar.markdown("## ⚙️ Настройки")

# Выбор периода
period_options = {
    "Последние 7 дней": 7,
    "Последние 30 дней": 30,
    "Последние 90 дней": 90,
    "Последний год": 365
}
selected_period = st.sidebar.selectbox("Период анализа:", list(period_options.keys()))
days = period_options[selected_period]

# Дополнительные настройки
show_annotations = st.sidebar.checkbox("Показать аннотации", value=True)
chart_height = st.sidebar.slider("Высота графиков", 400, 1000, 600)
```

## 🚀 Запуск и развертывание

### Локальный запуск
```bash
# Способ 1: Через скрипт
python dashboard/run_dashboard.py

# Способ 2: Прямой запуск
streamlit run dashboard/app.py

# Способ 3: Через bat файл (Windows)
start_dashboard.bat
```

### Запуск через run_dashboard.py
```python
def check_database():
    """Проверка наличия базы данных"""
    if not os.path.exists("finance_bot.db"):
        print("❌ База данных не найдена!")
        return False
    return True

def install_requirements():
    """Установка зависимостей"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'Pillow']
    # Проверка и установка пакетов
```

### Production развертывание

#### Streamlit Cloud
```yaml
# .streamlit/config.toml
[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#2E8B57"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

#### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finance-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: finance-dashboard
  template:
    metadata:
      labels:
        app: finance-dashboard
    spec:
      containers:
      - name: dashboard
        image: finance-dashboard:latest
        ports:
        - containerPort: 8501
        env:
        - name: DATABASE_URL
          value: "sqlite:///finance_bot.db"
```

## 🔄 Оптимизация производительности

### Кэширование
```python
@st.cache_data(ttl=300)  # Кэш на 5 минут
def load_data(days: int):
    """Загрузка данных с кэшированием"""
    pass

@st.cache_data(ttl=3600)  # Кэш на 1 час
def load_historical_data():
    """Загрузка исторических данных"""
    pass

# Очистка кэша
if st.button("🔄 Обновить данные"):
    st.cache_data.clear()
    st.rerun()
```

### Ленивая загрузка графиков
```python
def load_chart_on_demand(chart_type: str):
    """Загрузка графика только при необходимости"""
    if chart_type == "daily":
        return ChartCreator.create_daily_trend_chart(data['daily_data'])
    elif chart_type == "weekly":
        return ChartCreator.create_weekly_trend_chart(data['weekly_data'])
```

### Оптимизация Pandas операций
```python
# Использование типов данных для экономии памяти
dtypes = {
    'id': 'int32',
    'user_id': 'int32',
    'amount': 'float32',
    'transaction_type': 'category'
}

df = pd.read_sql_query(query, conn, dtype=dtypes)

# Векторизация операций
df['amount_rub'] = df['amount'].round(2)
df['is_income'] = df['transaction_type'] == 'income'
```

## 📊 Мониторинг и аналитика

### Метрики производительности
```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def create_complex_chart():
    """Создание сложного графика с замером времени"""
    pass
```

### Google Analytics integration
```html
<!-- .streamlit/main.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔮 Будущие улучшения

### Функциональные улучшения
- [ ] **Экспорт графиков** - PNG, PDF, SVG
- [ ] **Кастомизация периодов** - произвольные даты
- [ ] **Фильтрация по категориям** - выбор конкретных категорий
- [ ] **Сравнение периодов** - месяц к месяцу, год к году
- [ ] **Прогнозирование** - ML модели для прогнозов

### Технические улучшения
- [ ] **WebSocket** - real-time обновления данных
- [ ] **База данных в памяти** - Redis для ускорения
- [ ] **Параллельная обработка** - многопоточные вычисления
- [ ] **CDN для статических файлов** - ускорение загрузки

### UI/UX улучшения
- [ ] **Темная тема** - ночной режим
- [ ] **Мобильная адаптация** - responsive design
- [ ] **Drag and drop** - интерфейс для загрузки данных
- [ ] **Голосовое управление** - голосовые команды
- [ ] **Настраиваемые дашборды** - конструктор дашбордов

### Интеграционные улучшения
- [ ] **API интеграция** - подключение банковских API
- [ ] **Уведомления** - email/push уведомления
- [ ] **Мультивалютность** - поддержка разных валют
- [ ] **Экспорт в Excel** - генерация отчетов

## 🔗 Интеграции

### с Telegram ботом
```python
# Общая база данных
BOT_DATABASE_PATH = "finance_bot.db"
DASHBOARD_DATABASE_PATH = BOT_DATABASE_PATH

# Форматы данных
def sync_data_with_bot():
    """Синхронизация данных с ботом"""
    pass
```

### с внешними API
```python
import requests

def get_currency_rates():
    """Получение курсов валют"""
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    return response.json()

def get_stock_prices():
    """Получение цен на акции"""
    pass
```

## 🔒 Безопасность

### Защита данных
```python
import hashlib

def hash_user_id(user_id: int) -> str:
    """Хеширование ID пользователя для анонимности"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()

# Ограничение доступа
def authenticate_user():
    """Аутентификация пользователя"""
    if st.session_state.get("authenticated", False):
        return True
    return False
```

### HTTPS и безопасность
```python
# Настройка HTTPS
streamlit run dashboard/app.py --server.enableCORS false --server.enableXsrfProtection false

# Заголовки безопасности
st.markdown("""
<script>
  // CSP и другие заголовки безопасности
</script>
""", unsafe_allow_html=True)
```

## 🔗 Связанные компоненты

- [[Telegram Bot]] - Источник данных для дашборда
- [[Database]] - Модель данных и SQL запросы
- [[Data Analysis]] - Аналитические методы и алгоритмы
- [[Visualization]] - Техники визуализации данных

---

**Теги:** `streamlit` `dashboard` `plotly` `data-visualization` `pandas` `finance` `interactive` `web-app`