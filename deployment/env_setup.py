import psycopg2
from common.postgresql_client import PostgresqlClient
from common.kafka_client import KafkaClient
import logging
from common.configuration import Configuration

logger = logging.getLogger(__name__)
DB_NAME = 'ANALYTICS'

if __name__ == '__main__':
    try:
        config = Configuration()
        create_tbl_type = "CREATE TABLE IF NOT EXISTS METRIC_TYPE  " \
                          "( ID INT PRIMARY KEY, TYPE VARCHAR (255) NOT NULL) ;"
        insert_tbl_types = "INSERT INTO METRIC_TYPE (ID, TYPE) VALUES(1, 'website'); "
        create_tbl_metrics = 'CREATE TABLE IF NOT EXISTS METRICS ( ' \
                             'ID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, ' \
                             'RESOURCE_NAME VARCHAR (255) NOT NULL, ' \
                             'RESOURCE_TYPE INT NOT NULL, ' \
                             'RESPONSE_TIME REAL, ' \
                             'STATUS_CODE INT, ' \
                             'CONTENT TEXT, ' \
                             'CREATED_TIME_UTC TIMESTAMP, ' \
                             'CONSTRAINT fk_type ' \
                             'FOREIGN KEY(RESOURCE_TYPE) ' \
                             'REFERENCES METRIC_TYPE(ID) ' \
                             ');'
        db_client = PostgresqlClient(config.db_host, config.db_port, config.db_user, config.db_password)  # connect while DB doesnt exist yet
        db_client.create_db(DB_NAME)
        db_client = PostgresqlClient(config.db_host, config.db_port, config.db_user, config.db_password, DB_NAME)
        db_client.execute(create_tbl_type)
        db_client.execute(create_tbl_metrics)
        db_client.execute(insert_tbl_types)  # will fail and do nothing if same key already exits so setup can be executed several times


        # if kafka topic doesnt exist - create it
        kafka_client = KafkaClient(config.mq_host, config.mq_port, config.mq_api_version, config.mq_topic_name,
                                   config.ssl_cafile, config.ssl_certfile, config.ssl_keyfile)
        kafka_client.create_topic(config.mq_topic_name, config.mq_num_partitions, config.mq_replication_factor)

    except psycopg2.Error:
        logger.exception("[Error in setting up environment]")
    except Exception:
        # TODO: worth checking different types of errors and act accordingly
        logger.exception("[Error in setting up environment]")
