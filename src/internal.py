import functools

import requests

from settings import settings


@functools.cache
def internal_retrieve_connection_config(connection_id: str) -> dict:
    return requests.get(
        f"{settings.internal_api_base_url}/internal/config/connection/{connection_id}/",
        verify=settings.internal_ssl_verify,
    ).json()


async def internal_update_balance_data(connection_id: str, data: dict):
    return requests.post(
        f"{settings.internal_api_base_url}/internal/exchange/balance/",
        headers={"X-Connection-Id": connection_id},
        verify=settings.internal_ssl_verify,
        json=data,
    )


async def internal_update_order_data(connection_id: str, data: dict):
    return requests.post(
        f"{settings.internal_api_base_url}/internal/exchange/order/",
        headers={"X-Connection-Id": connection_id},
        verify=settings.internal_ssl_verify,
        json=data,
    )
