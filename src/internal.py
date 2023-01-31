import functools

import requests

from constants import INTERNAL_CONFIG_API_URL, INTERNAL_EXCHANGE_API_URL


@functools.cache
def internal_retrieve_connection_config(connection_id: str) -> dict:
    return requests.get(f"{INTERNAL_CONFIG_API_URL}/connection/{connection_id}/").json()


async def internal_update_balance_data(connection_id: str, data: dict):
    return requests.post(
        f"{INTERNAL_EXCHANGE_API_URL}/balance/",
        headers={"X-Connection-Id": connection_id},
        json=data,
    )


async def internal_update_order_data(connection_id: str, data: dict):
    return requests.post(
        f"{INTERNAL_EXCHANGE_API_URL}/order/",
        headers={"X-Connection-Id": connection_id},
        json=data,
    )
