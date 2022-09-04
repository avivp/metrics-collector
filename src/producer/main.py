import logging
from common.configuration import Configuration
from common.kafka_client import KafkaProducerClient
from metrics_writer import MetricsWriter
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # TODO: set level from configuration

if __name__ == '__main__':
    service_config = Configuration()
    interval = service_config.ping_interval_second
    mq_client = KafkaProducerClient(service_config.mq_host, service_config.mq_port, service_config.mq_api_version,
                            service_config.mq_topic_name, service_config.ssl_cafile, service_config.ssl_certfile,
                            service_config.ssl_keyfile)
    logger.info(f'[Producer start executing] topic:{service_config.mq_topic_name}')
    writer = MetricsWriter(mq_client)
    while True:
        # consider using threads for scaling this work
        writer.write()
        sleep(interval)
