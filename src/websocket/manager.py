import asyncio
import logging

from client import get_redis_client
from websocket.service import WebsocketService

INTERNAL_CONNECTION_CONFIG_KEY = "connection-config"


class WebsocketServiceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.redis = get_redis_client()

        self.services = {}

    async def start(self):
        while True:
            await self.manage_services()
            await asyncio.sleep(5)

    def get_connection_configuration_ids(self) -> list:
        connection_ids = self.redis.smembers(INTERNAL_CONNECTION_CONFIG_KEY)
        return [connection_id.decode() for connection_id in connection_ids]

    async def manage_services(self):
        connection_ids = self.get_connection_configuration_ids()

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
