import functools

import requests

from settings import settings


@functools.cache
def internal_retrieve_connection_config(connection_id: str) -> dict:
    resp = requests.get(
        f"{settings.internal_api_base_url}/internal/config/connection/{connection_id}/",
        verify=settings.internal_ssl_verify,
    )

    resp.raise_for_status()
    return resp.json()


async def internal_update_balance_data(connection_id: str, data: dict):
    resp = requests.post(
        f"{settings.internal_api_base_url}/internal/exchange/balance/sync/",
        headers={"X-Connection-Id": connection_id},
        verify=settings.internal_ssl_verify,
        json=data,
    )

    resp.raise_for_status()


async def internal_update_order_data(connection_id: str, data: dict):
    resp = requests.post(
        f"{settings.internal_api_base_url}/internal/exchange/order/sync/",
        headers={"X-Connection-Id": connection_id},
        verify=settings.internal_ssl_verify,
        json=data,
    )

    resp.raise_for_status()
