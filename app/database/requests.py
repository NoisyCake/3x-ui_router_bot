from database.engine import async_session
from database.models import Client

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


async def orm_contract_in_db(session: AsyncSession, contract_num: str) -> bool:
    query = select(Client).where(Client.contract_num == int(contract_num))
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user is not None


# Запросы админа

async def orm_add_contract(session: AsyncSession, contract_num: str, uuid: str):
    session.add(Client(contract_num=int(contract_num), uuid=uuid))
    await session.commit()
    
    
async def orm_get_client_by_contract(session: AsyncSession, contract_num: str) -> Client:
    query = select(Client).where(Client.contract_num == int(contract_num))
    result = await session.execute(query)
    client = result.scalar_one_or_none()
    return client
    
    
async def orm_delete_contract(session: AsyncSession, contract_num: str) -> bool:
    if not await orm_contract_in_db(session, contract_num):
        return False
    
    query = delete(Client).where(Client.contract_num == int(contract_num))
    await session.execute(query)
    await session.commit()
    return True


async def orm_get_contracts(session: AsyncSession):
    query = select(Client.contract_num, Client.tg_id)
    result = await session.execute(query)
    return result.all()


# Запросы пользователя

async def orm_get_client(session: AsyncSession, tg_id: str) -> Client:
    query = select(Client).where(Client.tg_id == int(tg_id))
    result = await session.execute(query)
    client = result.scalar_one_or_none()
    return client


async def orm_client_bind_contract(session: AsyncSession, contract_num: str, tg_id: str, exp_date: int) -> bool:
    if not await orm_contract_in_db(session, contract_num):
        return False
    
    query = update(Client).where(Client.contract_num == int(contract_num)).values(
        tg_id=int(tg_id),
        subscription=True,
        exp_date=exp_date
    )
    await session.execute(query)
    await session.commit()
    return True