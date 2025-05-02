import os
import dotenv

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from database.models import Base

dotenv.load_dotenv()

engine = create_async_engine(url=os.getenv('DATABASE'))

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)