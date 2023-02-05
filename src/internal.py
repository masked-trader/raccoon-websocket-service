import functools

import requests

from constants import INTERNAL_API_BASE_URL, INTERNAL_SSL_VERIFY


@functools.cache
def internal_retrieve_connection_config(connection_id: str) -> dict:
    return requests.get(
        f"{INTERNAL_API_BASE_URL}/internal/config/connection/{connection_id}/",
        verify=INTERNAL_SSL_VERIFY,
    ).json()


async def internal_update_balance_data(connection_id: str, data: dict):
    return requests.post(
        f"{INTERNAL_API_BASE_URL}/internal/exchange/balance/",
        headers={"X-Connection-Id": connection_id},
        verify=INTERNAL_SSL_VERIFY,
        json=data,
    )


async def internal_update_order_data(connection_id: str, data: dict):
    return requests.post(
        f"{INTERNAL_API_BASE_URL}/internal/exchange/order/",
        headers={"X-Connection-Id": connection_id},
        verify=INTERNAL_SSL_VERIFY,
        json=data,
    )
