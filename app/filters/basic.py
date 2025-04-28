from aiogram.filters import Filter
from aiogram.types import Message


class IsAdmin(Filter):
    def __init__(self, admin_ids: str) -> None:
        self.admin_ids = admin_ids
        
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [int(admin_id) for admin_id in self.admin_ids.split()]