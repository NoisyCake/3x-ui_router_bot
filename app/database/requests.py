from typing import Any
from datetime import datetime

from database.models import Client

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


async def orm_contract_in_db(session: AsyncSession, contract_id: str) -> bool:
    query = select(Client).where(Client.contract_id == contract_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user is not None


async def orm_add_contract(session: AsyncSession, contract_id: str, uuid: str):
    session.add(Client(contract_id=contract_id, uuid=uuid))
    await session.commit()
    
    
async def orm_get_client_by_contract(session: AsyncSession, contract_id: str) -> Client:
    query = select(Client).where(Client.contract_id == contract_id)
    result = await session.execute(query)
    client = result.scalar_one_or_none()
    return client
    
    
async def orm_delete_contract(session: AsyncSession, contract_id: str) -> bool:
    if not await orm_contract_in_db(session, contract_id):
        return False
    
    query = delete(Client).where(Client.contract_id == contract_id)
    await session.execute(query)
    await session.commit()
    return True


async def orm_get_contracts(session: AsyncSession) -> list[dict[str, Any]]:
    query = select(Client.contract_id, Client.tg_id)
    result = await session.execute(query)
    return [dict(row._mapping) for row in result.all()]


async def orm_get_client(session: AsyncSession, tg_id: str) -> Client:
    query = select(Client).where(Client.tg_id == int(tg_id))
    result = await session.execute(query)
    client = result.scalar_one_or_none()
    return client


async def orm_client_bind_contract(session: AsyncSession, contract_id: str, tg_id: str, exp_date: int) -> bool:
    if not await orm_contract_in_db(session, contract_id):
        return False
    
    query = update(Client).where(Client.contract_id == contract_id).values(
        tg_id=int(tg_id),
        subscription=True,
        exp_date=exp_date
    )
    await session.execute(query)
    await session.commit()
    return True


async def orm_extend_subscription(session: AsyncSession, tg_id: str, new_exp_date: datetime):
    query = update(Client).where(Client.tg_id == int(tg_id)).values(
        exp_date=new_exp_date
    )
    await session.execute(query)
    await session.commit()
    return True