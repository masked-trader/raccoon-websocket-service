#!/usr/bin/env python

import asyncio
import logging

from settings import settings
from websocket.manager import WebsocketServiceManager

logging.basicConfig(
    level=getattr(logging, settings.service_log_level.upper()),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


def main():
    manager = WebsocketServiceManager()

    asyncio.run(manager.start())


if __name__ == "__main__":
    main()
