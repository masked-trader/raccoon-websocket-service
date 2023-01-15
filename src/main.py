#!/usr/bin/env python

import asyncio
import logging

from constants import SERVICE_LOG_LEVEL
from websocket.manager import WebsocketServiceManager

logging.basicConfig(
    level=getattr(logging, SERVICE_LOG_LEVEL),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


def main():
    manager = WebsocketServiceManager()

    asyncio.run(manager.start())


if __name__ == "__main__":
    main()
