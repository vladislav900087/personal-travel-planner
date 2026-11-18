from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_session_executes_query(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


async def test_test_database_is_isolated(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT current_database()"))
    assert result.scalar() == "travel_test_db"
