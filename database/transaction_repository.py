from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from .database import Transaction

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
        transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            description=description
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_user_transactions(
        self,
        user_id: int,
        days: int = 30
    ) -> List[Transaction]:
        date_from = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.created_at >= date_from
                )
            )
            .order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_balance(self, user_id: int) -> dict:
        income_result = await self.session.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == 'income'
                )
            )
        )
        expense_result = await self.session.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == 'expense'
                )
            )
        )

        total_income = income_result.scalar() or 0
        total_expense = expense_result.scalar() or 0

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense
        }

    async def get_category_statistics(
        self,
        user_id: int,
        days: int = 30
    ) -> dict:
        date_from = datetime.now() - timedelta(days=days)

        # Статистика по категориям доходов
        income_stats = await self.session.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label('total'),
                func.count(Transaction.id).label('count')
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == 'income',
                    Transaction.created_at >= date_from
                )
            )
            .group_by(Transaction.category)
        )

        # Статистика по категориям расходов
        expense_stats = await self.session.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label('total'),
                func.count(Transaction.id).label('count')
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == 'expense',
                    Transaction.created_at >= date_from
                )
            )
            .group_by(Transaction.category)
        )

        income_data = {}
        for category, total, count in income_stats.all():
            income_data[category] = {'total': total, 'count': count}

        expense_data = {}
        for category, total, count in expense_stats.all():
            expense_data[category] = {'total': total, 'count': count}

        return {
            'income': income_data,
            'expense': expense_data
        }

    async def get_all_user_transactions(
        self,
        user_id: int,
        days: int = 30
    ) -> List[Transaction]:
        """Получить все транзакции пользователя с ID для редактирования"""
        date_from = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.created_at >= date_from
                )
            )
            .order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    async def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        category: str = None,
        amount: float = None,
        transaction_type: str = None
    ) -> bool:
        """Обновить транзакцию"""
        result = await self.session.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return False

        if category is not None:
            transaction.category = category
        if amount is not None:
            transaction.amount = amount
        if transaction_type is not None:
            transaction.transaction_type = transaction_type

        await self.session.commit()
        return True

    async def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Удалить транзакцию"""
        result = await self.session.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return False

        await self.session.delete(transaction)
        await self.session.commit()
        return True