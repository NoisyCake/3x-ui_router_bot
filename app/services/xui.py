import uuid
import json
from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database import requests
from database.models import Client


class XUIApi():
    def __init__(self, client: AsyncClient, username: str, password: str):
        self.client = client
        self.username = username
        self.password = password
        self.is_authenticated = False


    async def login(self):
        response = await self.client.post(
            "/login",
            data={"username": self.username, "password": self.password}
        )
        if response.status_code == 200:
            self.is_authenticated = True
        else:
            raise Exception("Login failed")


    async def add_client(self, session: AsyncSession, contract_id: str):
        client_uuid = str(uuid.uuid4())
        
        client_settings = {
            'clients': [{
                'id': client_uuid,
                'flow': "xtls-rprx-vision",
                'email': contract_id,
                'limitIp': 1,
                'totalGB': 0,
                'expiryTime': 0,
                'enable': True,
                'tgId': "",
                'subId': contract_id,
                'reset': 0
            }]
        }
        
        payload = {
            'id': 2,
            'settings': json.dumps(client_settings)
        }
        
        await self.client.post(
            "/panel/api/inbounds/addClient",
            json=payload,
            headers={"Accept": "application/json"}
        )
        
        await requests.orm_add_contract(session, contract_id, client_uuid)
        
        
    async def update_client(self, session: AsyncSession, contract_id: str, tg_id: str):
        client = await requests.orm_get_client_by_contract(session, contract_id)
        expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        expiry_timestamp = int(expiry_date.timestamp() * 1000)
        
        client_settings = {
            'clients': [{
                'id':  client.uuid,
                'flow': "xtls-rprx-vision",
                'email': contract_id,
                'limitIp': 1,
                'totalGB': 0,
                'expiryTime': expiry_timestamp,
                'enable': True,
                'tgId': tg_id,
                'subId': contract_id,
                'reset': 0
            }]
        }
        
        payload = {
            'id': 2,
            'settings': json.dumps(client_settings)
        }
        
        await self.client.post(
            f"/panel/api/inbounds/updateClient/{client.uuid}",
            json=payload,
            headers={"Accept": "application/json"}
        )
        
        await requests.orm_client_bind_contract(session, contract_id, tg_id, expiry_date)
        
        
    async def delete_client(self, session: AsyncSession, client: Client):
        await self.client.post(
            f"/panel/api/inbounds/{2}/delClient/{client.uuid}",
            headers={"Accept": "application/json"}
        )
            
        await requests.orm_delete_contract(session, client.contract_id)
        
        
    async def extend_subscription(self, session: AsyncSession, tg_id: str, period: str | int):
        client = await requests.orm_get_client(session, int(tg_id))
        if client.exp_date < datetime.now(timezone.utc):
            expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expiry_date = client.exp_date + timedelta(days=int(period))
        expiry_timestamp = int(expiry_date.timestamp() * 1000)
        
        client_settings = {
            'clients': [{
                'id':  client.uuid,
                'flow': "xtls-rprx-vision",
                'email': client.contract_id,
                'limitIp': 1,
                'totalGB': 0,
                'expiryTime': expiry_timestamp,
                'enable': True,
                'tgId': tg_id,
                'subId': client.contract_id,
                'reset': 0
            }]
        }
        
        payload = {
            'id': 2,
            'settings': json.dumps(client_settings)
        }
        
        await self.client.post(
            f"/panel/api/inbounds/updateClient/{client.uuid}",
            json=payload,
            headers={"Accept": "application/json"}
        )
        
        await requests.orm_extend_subscription(session, tg_id, expiry_date)