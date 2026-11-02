"""Database cleanup script - drops all tables and alembic version tracking."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def cleanup():
    """Drop all tables and alembic version."""
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        # Drop all tables in correct order (reverse of creation due to FKs)
        await conn.execute(text("DROP TABLE IF EXISTS bookings CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS members CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS inventory CASCADE"))
        # Drop alembic version table
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

    await engine.dispose()
    print("Database cleaned up successfully")


if __name__ == "__main__":
    asyncio.run(cleanup())