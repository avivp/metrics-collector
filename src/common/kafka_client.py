# ------------------------------
# A wrapper class to kafka
# As kafka clients already support retry mechanism I didnt add one
# ------------------------------
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import kafka.errors
import logging

logger = logging.getLogger(__name__)
GROUP_ID = "metrics_group"

class KafkaClient(object):

    def __init__(self, host:str, port:int, api_version: tuple, topic_name:str,
                 ssl_cafile: str = None, ssl_certfile: str = None, ssl_keyfile: str = None):
        self._host = f'{host}:{port}'
        self._topic_name = topic_name
        self._ssl_cafile = ssl_cafile
        self._ssl_certfile = ssl_certfile
        self._ssl_keyfile = ssl_keyfile
        self._api_version = api_version

    def create_topic(self, topic_name: str, num_partitions: int, replication_factor: int):
        # KafkaAdminClient has a built is retry mechanism with backoff interval
        # admin_client = KafkaAdminClient(
        #     bootstrap_servers=self._host,
        #     ssl_cafile=self._ssl_cafile,
        #     ssl_certfile=self._ssl_certfile,
        #     ssl_keyfile=self._ssl_keyfile
        # )
        # topic_list = []
        # topic_list.append(NewTopic(name=topic_name,
        #                            num_partitions=num_partitions,
        #                            replication_factor=replication_factor))
        # admin_client.create_topics(new_topics=topic_list, validate_only=False)
            pass  # this code is not working yet


class KafkaProducerClient(KafkaClient):
    def __init__(self, host: str, port: int, api_version: tuple, topic_name: str,
                 ssl_cafile: str = None, ssl_certfile: str = None, ssl_keyfile: str = None):
        super().__init__(host, port, api_version, topic_name, ssl_cafile, ssl_certfile, ssl_keyfile)
        # keep connection with kafka open
        self._producer = KafkaProducer(
            bootstrap_servers=self._host,
            security_protocol="SSL",
            ssl_cafile=self._ssl_cafile,
            ssl_certfile=self._ssl_certfile,
            ssl_keyfile=self._ssl_keyfile
        )

    def __del__(self):
        if self._producer:
            self._producer.close()

    def put_message(self, msg) -> bool:
        # KafkaProducer has by default retry mechanism with backoff interval
        # and expects ack on sent msgs to prevent data loss
        try:
            self._producer.send(self._topic_name, msg.encode('utf-8'))
            self._producer.flush()
            return True
        except kafka.errors.KafkaTimeoutError:
            # this error is raised after retries
            logger.error(f'[Timeout in sending msg] topic:{self._topic_name}')
        except Exception:
            # TODO: add support for different types of errors
            # not logging msg content as it may contain sensitive data
            logger.exception(f'[Error in sending msg] topic:{self._topic_name}')
        return False

class KafkaConsumerClient(KafkaClient):
    def __init__(self, host: str, port: int, api_version: tuple, topic_name: str,
                 ssl_cafile: str = None, ssl_certfile: str = None, ssl_keyfile: str = None):
        super().__init__(host, port, api_version, topic_name, ssl_cafile, ssl_certfile, ssl_keyfile)
        self._timeout = 2000
        # keeping connection with kafka open
        self._consumer = KafkaConsumer(
            bootstrap_servers=self._host,
            auto_offset_reset='latest',
            group_id=GROUP_ID,
            security_protocol="SSL",
            ssl_cafile=self._ssl_cafile,
            ssl_certfile=self._ssl_certfile,
            ssl_keyfile=self._ssl_keyfile,
            consumer_timeout_ms=self._timeout
        )

        self._consumer.subscribe([self._topic_name])

    def __del__(self):
        if self._consumer:
            self._consumer.close()

    def get_messages(self) -> []:
        list = []
        for message in self._consumer:
            list.append(message.value.decode('utf-8'))
        self._consumer.commit()
        return list
