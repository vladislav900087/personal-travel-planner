from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_session_executes_query(db_session: AsyncSession):
    # verify that the test db connection works and executes a query
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


async def test_test_database_is_isolated(db_session: AsyncSession):
    # verify we are connected to travel_test_db, not production/dev db
    result = await db_session.execute(text("SELECT current_database()"))
    current_db = result.scalar()
    assert current_db == "travel_test_db"
