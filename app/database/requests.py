from database.engine import async_session
from database.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


async def _orm_contract_in_db(session: AsyncSession, contract_num: str):
    query = select(User).where(User.contract_num == int(contract_num))
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user is not None


async def orm_user_exists(session: AsyncSession, tg_id: str):
    query = select(User).where(User.tg_id == int(tg_id))
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user is not None


async def orm_add_contract(session: AsyncSession, contract_num: str):
    session.add(User(contract_num=int(contract_num)))
    await session.commit()
    
    
async def orm_user_bind_contract(session: AsyncSession, contract_num: str, tg_id: str):
    if not await _orm_contract_in_db(session, contract_num):
        return False
    
    query = update(User).where(User.contract_num == int(contract_num)).values(
        tg_id=int(tg_id)
    )
    await session.execute(query)
    await session.commit()
    return True
    
    
async def orm_get_contracts(session: AsyncSession):
    query = select(User.contract_num, User.tg_id)
    result = await session.execute(query)
    return result.all()
    
    
async def orm_delete_contract(session: AsyncSession, contract_num: str):
    if not await _orm_contract_in_db(session, contract_num):
        return False
    
    query = delete(User).where(User.contract_num == int(contract_num))
    await session.execute(query)
    await session.commit()
    return True