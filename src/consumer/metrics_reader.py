# ------------------------------
# Reader class is responsible to read different types of metrics
# from msg queue and publish to a storage
# the MQ and DB clients are sent as dependency injection
# to enable mocking and future changing of underlying technology
# ------------------------------
from common.configuration import Configuration
from common.metrics import WebsiteMetrics
from resource_storage_handler import WebsiteSqlHandler
import json
import logging

logger = logging.getLogger(__name__)



class MetricsReader(object):
    def __init__(self, queue_client, db_client):
        self._queue_client = queue_client
        self._db_client = db_client
        self._resource_handlers = [WebsiteSqlHandler(self._db_client)]  # can extend to other metrics types

    def read(self):
        try:
            msgs = self._queue_client.get_messages()  # this will timeout if no msgs arrive
            # Here we should calculate the proper handler for each msg type
            # for now since we know we only support this specific metrics type we can use the only handler we have
            list = []
            for msg in msgs:
                try:
                    list.append(json.loads(msg, object_hook=WebsiteMetrics.from_json))
                except TypeError:
                    logger.exception(f'[Wrong type of message was sent and will not be processed]')
            self._resource_handlers[0].store_metrics(list)
            self._queue_client.commit_messages()  # msgs were processed and can be ack as such

        except Exception:
            logger.exception(f'[Unexpected error occurred]')
