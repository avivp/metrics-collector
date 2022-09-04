from common.metrics import Metrics
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    WEBSITE = 1


TABLE_NAME = "METRICS"  # not taken from config, those usually dont change

class ResourceStorageHandler(object):
    def __init__(self, db_client):
        self._db_client = db_client

    def store_metrics(self, list: [Metrics]):
        pass


# =========================
# This handler knows how to store website metrics into a SQL storage
# for other type of storage (e.g. nosql) and also for other type of metrics ->
# a different type of handler should be implemented
# =========================
class WebsiteSqlHandler(ResourceStorageHandler):
    INSERT_SQL = f"INSERT INTO {TABLE_NAME} " \
                 f"(RESOURCE_NAME, RESOURCE_TYPE, RESPONSE_TIME, STATUS_CODE, CONTENT, CREATED_TIME_UTC) "

    def __init__(self, db_client):
        super().__init__(db_client)

    def store_metrics(self, list: [Metrics]):
        # Should be improved by bulk insert.
        # in current implementation some metrics might be saved while other fails.
        # should return a list of the failed ones to attempt retries.
        for item in list:
            try:
                content = f"'{item.content}'" if item.content else "NULL "
                command = f"{self.INSERT_SQL} VALUES('{item.resource_name}', {ResourceType[item.resource_type].value}, " \
                          f"{item.response_time}, {item.status_code}, {content}, " \
                          f"TO_TIMESTAMP('{item.create_time_utc}', 'YYYY-MM-DD HH24:MI')) "
                self._db_client.execute(command)
            except Exception:
                logger.exception(f'[Error adding record to DB] resource:{item.resource_name}')
