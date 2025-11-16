import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict

class ChartCreator:
    """Класс для создания графиков и диаграмм"""

    @staticmethod
    def create_daily_trend_chart(daily_data: pd.DataFrame) -> go.Figure:
        """Создать график дневных трендов"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Дневные доходы и расходы', 'Дневной баланс'),
            vertical_spacing=0.15
        )

        # График доходов и расходов
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['income'],
                mode='lines+markers',
                name='Доходы',
                line=dict(color='#2E8B57', width=3),
                fill=None
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['expense'],
                mode='lines+markers',
                name='Расходы',
                line=dict(color='#DC143C', width=3),
                fill='tonexty',
                fillcolor='rgba(220, 20, 60, 0.1)'
            ),
            row=1, col=1
        )

        # График баланса
        colors = ['#2E8B57' if x >= 0 else '#DC143C' for x in daily_data['balance']]
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['balance'],
                mode='lines+markers',
                name='Баланс',
                line=dict(width=3),
                marker=dict(
                    color=colors,
                    size=8
                )
            ),
            row=2, col=1
        )

        fig.update_layout(
            title='Динамика финансов',
            height=800,
            showlegend=True,
            template='plotly_white'
        )

        fig.update_xaxes(title_text="Дата", row=2, col=1)
        fig.update_yaxes(title_text="Сумма (₽)", row=1, col=1)
        fig.update_yaxes(title_text="Баланс (₽)", row=2, col=1)

        return fig

    @staticmethod
    def create_category_pie_chart(category_data: Dict, transaction_type: str) -> go.Figure:
        """Создать круговую диаграмму по категориям"""
        if not category_data:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20, color="#666666")
            )
            return fig

        labels = list(category_data.keys())
        values = [data['total'] for data in category_data.values()]

        # Фильтруем нулевые значения
        filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]

        if not filtered_data:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20, color="#666666")
            )
            return fig

        labels, values = zip(*filtered_data)

        title = "Распределение доходов" if transaction_type == 'income' else "Распределение расходов"

        # Определяем цвета
        try:
            colors_income = px.colors.qualitative.Set3[:len(labels)]
            colors_expense = px.colors.qualitative.Pastel1[:len(labels)]
            colors = colors_income if transaction_type == 'income' else colors_expense
        except:
            # Fallback цвета если что-то пошло не так
            colors = ['#2E8B57', '#3CB371', '#66CDAA', '#8FBC8F', '#228B22'] if transaction_type == 'income' else ['#DC143C', '#FF6B6B', '#FFA07A', '#FA8072', '#E9967A']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent:.1%}<br>₽{value:,.0f}',
            marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
        )])

        fig.update_layout(
            title=title,
            height=600,
            showlegend=True,
            template='plotly_white',
            margin=dict(t=80, b=80, l=80, r=80)
        )

        return fig

    @staticmethod
    def create_top_categories_bar_chart(top_data: pd.DataFrame, transaction_type: str) -> go.Figure:
        """Создать столбчатую диаграмму топ категорий"""
        if top_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20, color="#666666")
            )
            return fig

        title = "Топ категории доходов" if transaction_type == 'income' else "Топ категории расходов"
        color = '#2E8B57' if transaction_type == 'income' else '#DC143C'

        # Проверяем наличие необходимых колонок
        required_columns = ['amount', 'category', 'count']
        for col in required_columns:
            if col not in top_data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Ошибка: отсутствует колонка '{col}'",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    font=dict(size=20, color="#DC143C")
                )
                return fig

        # Фильтруем нулевые значения
        filtered_data = top_data[top_data['amount'] > 0].copy()

        if filtered_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20, color="#666666")
            )
            return fig

        # Сортируем по убыванию для лучшего отображения
        filtered_data = filtered_data.sort_values('amount', ascending=True)

        fig = go.Figure(data=[go.Bar(
            x=filtered_data['amount'],
            y=filtered_data['category'],
            orientation='h',
            marker=dict(
                color=color,
                line=dict(color='white', width=1)
            ),
            text=filtered_data['amount'].apply(lambda x: f'₽{x:,.0f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Сумма: ₽%{x:,.0f}<br>Количество: %{customdata}<extra></extra>',
            customdata=filtered_data['count']
        )])

        fig.update_layout(
            title=title,
            height=max(600, len(filtered_data) * 40 + 100),  # Адаптивная высота
            xaxis_title="Сумма (₽)",
            yaxis_title="Категория",
            yaxis={'categoryorder': 'total ascending'},
            template='plotly_white',
            margin=dict(t=80, b=80, l=200, r=80)  # Увеличиваем левый отступ для длинных названий
        )

        return fig

    @staticmethod
    def create_comparison_chart(category_stats: Dict) -> go.Figure:
        """Создать сравнительную диаграмму доходов и расходов по категориям"""
        income_data = category_stats.get('income', {})
        expense_data = category_stats.get('expense', {})

        all_categories = set(income_data.keys()) | set(expense_data.keys())

        if not all_categories:
            return go.Figure().add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20)
            )

        categories = list(all_categories)
        income_amounts = [income_data.get(cat, {}).get('total', 0) for cat in categories]
        expense_amounts = [expense_data.get(cat, {}).get('total', 0) for cat in categories]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Доходы',
            x=categories,
            y=income_amounts,
            marker_color='#2E8B57'
        ))

        fig.add_trace(go.Bar(
            name='Расходы',
            x=categories,
            y=expense_amounts,
            marker_color='#DC143C'
        ))

        fig.update_layout(
            title='Сравнение доходов и расходов по категориям',
            xaxis_title='Категория',
            yaxis_title='Сумма (₽)',
            barmode='group',
            height=600,
            template='plotly_white'
        )

        # Поворот labels для лучшей читаемости
        fig.update_xaxes(tickangle=45)

        return fig

    @staticmethod
    def create_weekly_trend_chart(weekly_data: pd.DataFrame) -> go.Figure:
        """Создать график недельных трендов"""
        if weekly_data.empty:
            return go.Figure().add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20)
            )

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=weekly_data['week'],
            y=weekly_data['income'],
            mode='lines+markers',
            name='Доходы',
            line=dict(color='#2E8B57', width=4),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=weekly_data['week'],
            y=weekly_data['expense'],
            mode='lines+markers',
            name='Расходы',
            line=dict(color='#DC143C', width=4),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=weekly_data['week'],
            y=weekly_data['balance'],
            mode='lines+markers',
            name='Баланс',
            line=dict(color='#1E90FF', width=4),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title='Недельные тренды',
            xaxis_title='Неделя',
            yaxis_title='Сумма (₽)',
            height=500,
            template='plotly_white',
            showlegend=True
        )

        return fig

    @staticmethod
    def create_monthly_trend_chart(monthly_data: pd.DataFrame) -> go.Figure:
        """Создать график месячных трендов"""
        if monthly_data.empty:
            return go.Figure().add_annotation(
                text="Нет данных для отображения",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=20)
            )

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Месячные доходы и расходы', 'Месячный баланс'),
            vertical_spacing=0.15
        )

        # Доходы и расходы
        fig.add_trace(
            go.Scatter(
                x=monthly_data['month'],
                y=monthly_data['income'],
                mode='lines+markers',
                name='Доходы',
                line=dict(color='#2E8B57', width=4)
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_data['month'],
                y=monthly_data['expense'],
                mode='lines+markers',
                name='Расходы',
                line=dict(color='#DC143C', width=4)
            ),
            row=1, col=1
        )

        # Баланс
        colors = ['#2E8B57' if x >= 0 else '#DC143C' for x in monthly_data['balance']]
        fig.add_trace(
            go.Scatter(
                x=monthly_data['month'],
                y=monthly_data['balance'],
                mode='lines+markers',
                name='Баланс',
                line=dict(width=4),
                marker=dict(
                    size=10,
                    color=colors
                )
            ),
            row=2, col=1
        )

        fig.update_layout(
            title='Месячные тренды',
            height=800,
            showlegend=True,
            template='plotly_white'
        )

        return fig