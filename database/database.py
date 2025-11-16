import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, func

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    transaction_type = Column(String)  # 'income' или 'expense'
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())

class Database:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./finance_bot.db"):
        self.engine = create_async_engine(database_url)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        return self.async_session()

# Глобальный экземпляр базы данных
db = Database()