import json
import logging

from constants import get_connection_name, get_connection_unique_name
from websocket.client import get_redis_client

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"


class WebsocketHandler:

    handler_type = "base"
    subscription_key = "base-subs"

    def __init__(self, logger=None) -> None:
        self.logger = logging.getLogger(__name__) if logger is None else logger

        self.redis = get_redis_client()

        self.db_prefix = get_connection_name()
        self.db_prefix_private = get_connection_unique_name()

        self.subscriptions = {}

    def get_db_key(self, *args):
        return "-".join([self.db_prefix, *args])

    def get_db_key_private(self, *args):
        return "-".join([self.db_prefix_private, *args])

    def get_subscription(self, sub_key: str):
        return self.subscriptions[sub_key]

    def get_subscriptions(self):
        return dict(self.subscriptions)

    def manage_subscriptions(self, db_key: str):
        raw_data = self.redis.get(db_key)
        db_subs = json.loads(raw_data) if raw_data else []

        for db_sub in db_subs:
            if db_sub not in self.subscriptions:
                self.add_subscription(db_sub)

        for local_sub in self.subscriptions:
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
