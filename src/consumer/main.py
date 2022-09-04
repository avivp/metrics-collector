import logging
from common.configuration import Configuration
from common.kafka_client import KafkaConsumerClient
from common.postgresql_client import PostgresqlClient
from metrics_reader import MetricsReader
from time import sleep


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # TODO: set level from configuration
DB_NAME = 'ANALYTICS'  # not taken from config, those usually dont change


if __name__ == '__main__':
    service_config = Configuration()
    interval = service_config.ping_interval_second
    mq_client = KafkaConsumerClient(service_config.mq_host, service_config.mq_port, service_config.mq_api_version,
                                    service_config.mq_topic_name, service_config.ssl_cafile,
                                    service_config.ssl_certfile,
                                    service_config.ssl_keyfile)

    db_client = PostgresqlClient(service_config.db_host, service_config.db_port, service_config.db_user,
                                 service_config.db_password, DB_NAME)
    logger.info(f'[Consumer start executing] topic:{service_config.mq_topic_name}')
    reader = MetricsReader(mq_client, db_client)
    while True:
        # consider using threads for scaling this work and process messages in parallel
        # note this will also cause parallel connections to the DB
        reader.read()
        sleep(interval)
