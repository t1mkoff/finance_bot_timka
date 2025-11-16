import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

# Добавляем путь к основному проекту для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.data_loader import DataLoader
from dashboard.charts import ChartCreator

# Настройка страницы
st.set_page_config(
    page_title="Финансовый дашборд",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1F2937;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        color: #6B7280;
        font-size: 1rem;
    }
    .positive {
        color: #059669;
    }
    .negative {
        color: #DC2626;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Кэширование на 5 минут
def load_data(days: int):
    """Загрузить и кэшировать данные"""
    try:
        loader = DataLoader()
        return {
            'summary': loader.get_summary_stats(days),
            'category_stats': loader.get_category_stats(days),
            'daily_data': loader.get_daily_totals(days),
            'weekly_data': loader.get_weekly_trends(days),
            'monthly_data': loader.get_monthly_trends(90),  # Всегда 90 дней для месячных трендов
            'top_income': loader.get_top_categories('income', days, 10),
            'top_expense': loader.get_top_categories('expense', days, 10)
        }
    except FileNotFoundError:
        st.error("❌ База данных не найдена! Убедитесь, что бот запущен и создал базу данных.")
        return None
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {str(e)}")
        return None

def format_currency(amount: float) -> str:
    """Форматировать сумму в рубли"""
    return f"₽{amount:,.2f}".replace(',', ' ')

def create_metric_card(title: str, value: str, delta: str = None, color: str = "black"):
    """Создать карточку метрики"""
    delta_html = f"<p class='metric-label'>{delta}</p>" if delta else ""
    return f"""
    <div class='metric-card'>
        <h3 style='margin: 0; color: #6B7280;'>{title}</h3>
        <p class='metric-value' style='color: {color}; margin: 0.5rem 0;'>{value}</p>
        {delta_html}
    </div>
    """

def main():
    # Заголовок
    st.markdown('<h1 class="main-header">💰 Финансовый дашборд</h1>', unsafe_allow_html=True)

    # Боковая панель с настройками
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

    # Загрузка данных
    with st.spinner("🔄 Загрузка данных..."):
        data = load_data(days)

    if not data:
        st.stop()

    # Основные метрики
    st.markdown("## 📊 Основные показатели")
    summary = data['summary']

    # Вычисляем дополнительные метрики
    economy_rate = 0
    if summary['total_income'] > 0:
        economy_rate = (summary['total_income'] - summary['total_expense']) / summary['total_income'] * 100

    # Первая строка метрик
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(create_metric_card(
            "💰 Общие доходы",
            format_currency(summary['total_income']),
            f"Транзакций: {summary['income_count']}",
            "#059669"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_card(
            "💸 Общие расходы",
            format_currency(summary['total_expense']),
            f"Транзакций: {summary['expense_count']}",
            "#DC2626"
        ), unsafe_allow_html=True)

    with col3:
        balance_color = "#059669" if summary['balance'] >= 0 else "#DC2626"
        st.markdown(create_metric_card(
            "💵 Баланс",
            format_currency(summary['balance']),
            f"Экономия: {economy_rate:.1f}%",
            balance_color
        ), unsafe_allow_html=True)

    # Вторая строка метрик
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(create_metric_card(
            "📈 Средний доход",
            format_currency(summary['avg_income']),
            f"На транзакцию",
            "#059669"
        ), unsafe_allow_html=True)

    with col5:
        st.markdown(create_metric_card(
            "📉 Средний расход",
            format_currency(summary['avg_expense']),
            f"На транзакцию",
            "#DC2626"
        ), unsafe_allow_html=True)

    with col6:
        st.markdown(create_metric_card(
            "📊 Всего транзакций",
            str(summary['transaction_count']),
            f"За {days} дней",
            "#1E90FF"
        ), unsafe_allow_html=True)

    # Графики
    st.markdown("## 📈 Графики и анализ")

    # Вкладки для разных типов графиков
    tab1, tab2, tab3, tab4 = st.tabs(["🕐 Динамика", "🥧 Категории", "🏆 Топ категорий", "📅 Сравнения"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📅 Дневная динамика")
            if not data['daily_data'].empty:
                daily_chart = ChartCreator.create_daily_trend_chart(data['daily_data'])
                st.plotly_chart(daily_chart, use_container_width=True)
            else:
                st.info("Нет данных за выбранный период")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📆 Недельные тренды")
            if not data['weekly_data'].empty:
                weekly_chart = ChartCreator.create_weekly_trend_chart(data['weekly_data'])
                st.plotly_chart(weekly_chart, use_container_width=True)
            else:
                st.info("Недостаточно данных для недельных трендов")
            st.markdown('</div>', unsafe_allow_html=True)

        # Месячные тренды
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🗓️ Месячные тренды")
        if not data['monthly_data'].empty:
            monthly_chart = ChartCreator.create_monthly_trend_chart(data['monthly_data'])
            st.plotly_chart(monthly_chart, use_container_width=True)
        else:
            st.info("Недостаточно данных для месячных трендов")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("💰 Распределение доходов")
            income_pie = ChartCreator.create_category_pie_chart(
                data['category_stats']['income'],
                'income'
            )
            st.plotly_chart(income_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("💸 Распределение расходов")
            expense_pie = ChartCreator.create_category_pie_chart(
                data['category_stats']['expense'],
                'expense'
            )
            st.plotly_chart(expense_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🏆 Топ категории доходов")
            if not data['top_income'].empty:
                top_income_chart = ChartCreator.create_top_categories_bar_chart(
                    data['top_income'],
                    'income'
                )
                st.plotly_chart(top_income_chart, use_container_width=True)
            else:
                st.info("Нет данных о доходах")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🏆 Топ категории расходов")
            if not data['top_expense'].empty:
                top_expense_chart = ChartCreator.create_top_categories_bar_chart(
                    data['top_expense'],
                    'expense'
                )
                st.plotly_chart(top_expense_chart, use_container_width=True)
            else:
                st.info("Нет данных о расходах")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⚖️ Сравнение по категориям")
        comparison_chart = ChartCreator.create_comparison_chart(data['category_stats'])
        st.plotly_chart(comparison_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Таблица с последними транзакциями
    st.markdown("## 📋 Последние транзакции")

    try:
        loader = DataLoader()
        recent_transactions = loader.load_all_transactions(days)

        if not recent_transactions.empty:
            # Форматируем данные для отображения
            display_df = recent_transactions[['created_at', 'transaction_type', 'category', 'amount']].copy()
            display_df['created_at'] = display_df['created_at'].dt.strftime('%d.%m.%Y %H:%M')
            display_df['transaction_type'] = display_df['transaction_type'].map({
                'income': '📈 Доход',
                'expense': '📉 Расход'
            })
            display_df['amount'] = display_df['amount'].apply(format_currency)
            display_df.columns = ['📅 Дата', '📊 Тип', '📂 Категория', '💰 Сумма']

            # Отображаем последние 20 транзакций
            st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.info("Нет транзакций за выбранный период")
    except Exception as e:
        st.error(f"Ошибка загрузки транзакций: {str(e)}")

    # Информация в футере
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #6B7280; margin-top: 2rem;'>
            📊 Данные актуальны на {datetime.now().strftime('%d.%m.%Y %H:%M')} |
            Период анализа: {selected_period.lower()} |
            💰 Финансовый дашборд
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()