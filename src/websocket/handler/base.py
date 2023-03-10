import asyncio
import logging

from api import internal_retrieve_connection_config
from client import get_redis_client

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"


def get_connection_name(connection_id: str):
    config = internal_retrieve_connection_config(connection_id)

    return (
        "-".join([config["exchange"], "sandbox"])
        if config["sandbox"]
        else config["exchange"]
    )


def get_connection_unique_name(connection_id: str):
    connection_name = get_connection_name(connection_id)
    return "-".join([connection_name, connection_id])


class WebsocketHandler:

    handler_type = "base"
    subscription_key = "base-subs"

    def __init__(self, connection_id: str) -> None:
        self.logger = logging.getLogger(f"websocket.handler {connection_id}")

        self.redis = get_redis_client()
        self.connection_id = connection_id

        self.db_prefix = get_connection_name(connection_id)
        self.db_prefix_private = get_connection_unique_name(connection_id)

        self.subscriptions = {}

    def get_db_key(self, *args):
        return "-".join([self.db_prefix, *args])

    def get_db_key_private(self, *args):
        return "-".join([self.db_prefix_private, *args])

    def get_subscription(self, sub_key: str):
        return self.subscriptions[sub_key]

    def get_subscriptions(self):
        return dict(self.subscriptions)

    def dispatch_task(self, func):
        loop = asyncio.get_running_loop()
        loop.create_task(func())

    def manage_subscriptions(self, db_key: str):
        db_subs = {sub.decode() for sub in self.redis.smembers(db_key)}

        for db_sub in db_subs:
            if db_sub not in dict(self.subscriptions):
                self.add_subscription(db_sub)

        for local_sub in dict(self.subscriptions):
            if local_sub not in db_subs:
                self.remove_subscription(local_sub)

    def update_subscription(self, sub_key: str, status: bool):
        if sub_key in self.get_subscriptions():
            self.subscriptions[sub_key] = status

            self.logger.info(
                "updated %s subscription status - %s",
                self.handler_type,
                STATUS_ACTIVE if status else STATUS_INACTIVE,
            )

    def add_subscription(self, sub_key: str):
        if sub_key not in self.get_subscriptions():
            self.subscriptions[sub_key] = False

            self.logger.info(
                "added %s subscription - %s",
                self.handler_type,
                STATUS_INACTIVE,
            )

    def remove_subscription(self, sub_key: str):
        if sub_key in self.get_subscriptions():
            del self.subscriptions[sub_key]

            self.logger.info("removed %s subscription - %s", self.handler_type, sub_key)
