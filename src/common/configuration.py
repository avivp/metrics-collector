# ------------------------------
# Singleton class which reads configuration from a file
# currently config is read once when service starts up
# in real development we should provide an api to change configuration while service is running
# ------------------------------
import configparser
import os


class Configuration(object):
    __instance = None

    def __load(self):
        service_config = configparser.ConfigParser()
        service_config.read(os.path.dirname(__file__) + '/configurations.ini')
        self.db_host = service_config["Settings"]["db_host"]
        self.db_port = int(service_config["Settings"]["db_port"])
        self.db_user = os.getenv("DB_USER", service_config["Settings"]["db_user"])
        self.db_password = os.getenv("DB_PASSWORD", service_config["Settings"]["db_password"])
        self.mq_client_id = service_config["Settings"]["mq_client_id"]
        self.mq_host = service_config["Settings"]["mq_host"]
        self.mq_port = service_config["Settings"]["mq_port"]
        self.mq_topic_name = service_config["Settings"]["mq_topic_name"]
        self.mq_num_partitions = int(service_config["Settings"]["mq_num_partitions"])
        self.mq_replication_factor = int(service_config["Settings"]["mq_replication_factor"])
        self.mq_api_version = tuple(map(int, service_config["Settings"]["mq_api_version"].split(',')))
        self.ssl_cafile = os.getenv("SSL_CAFILE_PATH", os.path.dirname(__file__) + '/cert.pem')
        self.ssl_certfile = os.getenv("SSL_CERTFILE_PATH", os.path.dirname(__file__) + '/access_key.cert')
        self.ssl_keyfile = os.getenv("SSL_KEYFILE_PATH", os.path.dirname(__file__) + '/access_key.key')
        self.resource_list = list(map(str.strip, service_config["Settings"]["resource_list"].split(',')))
        self.ping_interval_second = int(service_config["Settings"]["ping_interval_second"])


    def __new__(cls, *args, **kwargs):
        # TODO: thread safety is required here using threading.Lock()
        if not Configuration.__instance:
            Configuration.__instance = object.__new__(cls)
            Configuration.__instance.__load()

        return Configuration.__instance

