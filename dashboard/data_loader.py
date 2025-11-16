import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class DataLoader:
    """Класс для загрузки данных из базы данных в формате pandas DataFrame"""

    def __init__(self, db_path: str = "finance_bot.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"База данных не найдена: {self.db_path}")
        return sqlite3.connect(self.db_path)

    def load_all_transactions(self, days: int = 30) -> pd.DataFrame:
        """Загрузить все транзакции за последние дни"""
        conn = self.get_connection()
        try:
            date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

            query = """
            SELECT
                id,
                user_id,
                transaction_type,
                category,
                amount,
                description,
                created_at
            FROM transactions
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """

            df = pd.read_sql_query(query, conn, params=(date_from,))
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
            df['week'] = df['created_at'].dt.isocalendar().week
            df['month'] = df['created_at'].dt.to_period('M')

            return df
        finally:
            conn.close()

    def get_summary_stats(self, days: int = 30) -> Dict:
        """Получить сводную статистику"""
        df = self.load_all_transactions(days)

        if df.empty:
            return {
                'total_income': 0,
                'total_expense': 0,
                'balance': 0,
                'transaction_count': 0,
                'income_count': 0,
                'expense_count': 0
            }

        income_df = df[df['transaction_type'] == 'income']
        expense_df = df[df['transaction_type'] == 'expense']

        return {
            'total_income': income_df['amount'].sum(),
            'total_expense': expense_df['amount'].sum(),
            'balance': income_df['amount'].sum() - expense_df['amount'].sum(),
            'transaction_count': len(df),
            'income_count': len(income_df),
            'expense_count': len(expense_df),
            'avg_income': income_df['amount'].mean() if not income_df.empty else 0,
            'avg_expense': expense_df['amount'].mean() if not expense_df.empty else 0
        }

    def get_category_stats(self, days: int = 30) -> Dict:
        """Получить статистику по категориям"""
        df = self.load_all_transactions(days)

        if df.empty:
            return {'income': {}, 'expense': {}}

        category_stats = {}

        for trans_type in ['income', 'expense']:
            type_df = df[df['transaction_type'] == trans_type]
            if not type_df.empty:
                category_summary = type_df.groupby('category').agg({
                    'amount': ['sum', 'count', 'mean']
                }).round(2)

                category_summary.columns = ['total', 'count', 'avg']
                category_stats[trans_type] = category_summary.to_dict('index')
            else:
                category_stats[trans_type] = {}

        return category_stats

    def get_daily_totals(self, days: int = 30) -> pd.DataFrame:
        """Получить ежедневные итоги для графиков"""
        df = self.load_all_transactions(days)

        if df.empty:
            return pd.DataFrame()

        daily_totals = df.groupby(['date', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

        if 'income' not in daily_totals.columns:
            daily_totals['income'] = 0
        if 'expense' not in daily_totals.columns:
            daily_totals['expense'] = 0

        daily_totals['balance'] = daily_totals['income'] - daily_totals['expense']
        daily_totals = daily_totals.reset_index()
        daily_totals['date'] = pd.to_datetime(daily_totals['date'])

        return daily_totals

    def get_weekly_trends(self, days: int = 30) -> pd.DataFrame:
        """Получить недельные тренды"""
        df = self.load_all_transactions(days)

        if df.empty:
            return pd.DataFrame()

        weekly_totals = df.groupby(['week', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

        if 'income' not in weekly_totals.columns:
            weekly_totals['income'] = 0
        if 'expense' not in weekly_totals.columns:
            weekly_totals['expense'] = 0

        weekly_totals['balance'] = weekly_totals['income'] - weekly_totals['expense']
        weekly_totals = weekly_totals.reset_index()

        return weekly_totals

    def get_monthly_trends(self, days: int = 90) -> pd.DataFrame:
        """Получить месячные тренды"""
        df = self.load_all_transactions(days)

        if df.empty:
            return pd.DataFrame()

        monthly_totals = df.groupby(['month', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

        if 'income' not in monthly_totals.columns:
            monthly_totals['income'] = 0
        if 'expense' not in monthly_totals.columns:
            monthly_totals['expense'] = 0

        monthly_totals['balance'] = monthly_totals['income'] - monthly_totals['expense']
        monthly_totals = monthly_totals.reset_index()
        monthly_totals['month'] = monthly_totals['month'].dt.to_timestamp()

        return monthly_totals

    def get_top_categories(self, transaction_type: str, days: int = 30, top_n: int = 10) -> pd.DataFrame:
        """Получить топ категорий"""
        df = self.load_all_transactions(days)

        if df.empty:
            return pd.DataFrame()

        type_df = df[df['transaction_type'] == transaction_type]

        if type_df.empty:
            return pd.DataFrame()

        top_categories = type_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(top_n)

        return pd.DataFrame({
            'category': top_categories.index,
            'amount': top_categories.values,
            'count': type_df.groupby('category')['amount'].count()[top_categories.index].values
        }).round(2)