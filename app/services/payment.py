import os
import uuid

from yookassa import Configuration, Payment


Configuration.account_id = os.getenv('YOOKASSA_ACCOUNT_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')

def create_yookassa_payment(amount: str | int, chat_id: int):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
        "value": f'{amount}.00',
        "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/hfk_routers_robot"
        },
        "capture": True,
        "metadata": {
            "chat_id": chat_id
        },
        "description": "Оплата подписки на пользование VPN через роутер"
    }, id_key)
    
    return payment.confirmation.confirmation_url, payment.id


def check_yookassa_payment(payment_id):
    payment = Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False