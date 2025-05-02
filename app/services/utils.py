import uuid
import base58
from typing import Any


def generate_contract_id() -> str:
    uid = uuid.uuid4()
    encoded = base58.b58encode(uid.bytes).decode('utf-8')
    return encoded[:14]


def get_paginated_contracts(contracts: list[dict[str, Any]], page: int) -> tuple[list[dict[str, Any]], int]:
    page_size = 10
    total_pages = max(1, (len(contracts) + 9) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    return contracts[start:end], total_pages