from typing import Any, Awaitable, Callable, Dict

from httpx import AsyncClient
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.xui import XUIApi


class XUIMiddleware(BaseMiddleware):
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.client = AsyncClient(base_url=base_url)
        self.api = XUIApi(self.client, username, password)
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        if not self.api.is_authenticated:
            await self.api.login()
        
        data['xui'] = self.api
        return await handler(event, data)