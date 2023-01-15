import asyncio
import logging

from client import get_redis_client
from constants import INTERNAL_CONNECTION_CONFIG_KEY
from util import get_exchange_connection_config, get_exchange_websocket_client
from websocket.service import WebsocketService


class WebsocketServiceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.redis = get_redis_client()

        self.services = {}

    async def start(self):
        while True:
            await self.manage_services()
            await asyncio.sleep(5)

    async def get_connection_ids(self):
        connection_ids = self.redis.hgetall(INTERNAL_CONNECTION_CONFIG_KEY)
        return [connection_id.decode() for connection_id in connection_ids]

    async def manage_services(self):
        connection_ids = await self.get_connection_ids()

        for remote_connection_id in connection_ids:
            if remote_connection_id not in self.services:
                await self.start_service(remote_connection_id)

        for local_connection_id in self.services:
            if local_connection_id not in connection_ids:
                await self.stop_service(local_connection_id)

    async def start_service(self, connection_id: str):
        self.logger.info("starting service with connection ID - %s", connection_id)

        service = WebsocketService(connection_id)

        loop = asyncio.get_running_loop()
        loop.create_task(service.start())

        self.services[connection_id] = service

    async def stop_service(self, connection_id: str):
        self.logger.info("stopping service with connection ID - %s", connection_id)

        service: WebsocketService = self.services[connection_id]

        await service.stop()
        del self.services[connection_id]

        get_exchange_connection_config.cache_clear()
        get_exchange_websocket_client.cache_clear()
