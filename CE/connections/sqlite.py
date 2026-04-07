from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from typing import AsyncGenerator
from config import settings

core_engine = create_async_engine(settings.CORE_DATABASE_URL, echo=True)
pc_engine = create_async_engine(settings.PC_DATABASE_URL, echo=True)

@event.listens_for(core_engine.sync_engine, "connect")
def enable_sqlite_fk_core(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@event.listens_for(pc_engine.sync_engine, "connect")
def enable_sqlite_fk_pc(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

core_session_maker = sessionmaker(core_engine, class_=AsyncSession, expire_on_commit=False)
pc_session_maker = sessionmaker(pc_engine, class_=AsyncSession, expire_on_commit=False)

async def init_core_db() -> None:
    async with core_engine.begin() as conn:
        from models import core
        await conn.run_sync(SQLModel.metadata.create_all)

async def init_pc_db() -> None:
    async with pc_engine.begin() as conn:
        from models import pc
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_core_session() -> AsyncGenerator[AsyncSession, None]:
    async with core_session_maker() as session:
        yield session

async def get_pc_session() -> AsyncGenerator[AsyncSession, None]:
    async with pc_session_maker() as session:
        yield session