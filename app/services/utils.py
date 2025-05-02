import uuid
import base58


def generate_contract_id() -> str:
    uid = uuid.uuid4()
    encoded = base58.b58encode(uid.bytes).decode('utf-8')
    return encoded[:14]


def get_paginated_contracts(contracts: list[tuple[str]], page: int) -> tuple[list[tuple[str]], int]:
    total_pages = max(1, (len(contracts) + 9) // 10)
    start = (page - 1) * 10
    end = start + 10
    return contracts[start:end], total_pages