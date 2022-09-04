# ------------------------------
# A wrapper class to postgresql
# very basic implementation with only required actions for now
# Also takes retry mechanism in to account in case of network issues
# ------------------------------
import psycopg2
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception

logger = logging.getLogger(__name__)


class PostgresqlClient(object):
    def __init__(self, host: str, port: int, user: str, pwd: str, database: str = None):
        self._host = host
        self._port = port
        self._user = user
        self._pwd = pwd
        self._database = database

    def __get_connection_url(self) -> str:
        db_name = 'defaultdb'
        if self._database:  # not None and not empty
            db_name = self._database
        return f'postgres://{self._user}:{self._pwd}@{self._host}:{self._port}/{db_name}?sslmode=require'

    def create_db(self, db_name: str):
        # special handling because create DB cannot executed in transaction and the with keyword automatically
        # creates transaction since psycopg2 v2.9
        # conn = psycopg2.connect(self.__get_connection_url())
        # try:
        #     create_db = f'CREATE DATABASE {db_name} '
        #     f'WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = \'{db_name}\') ;'
        #     conn.autocommit = False
        #     with conn.cursor() as cursor:
        #         cursor.execute(create_db)
        # finally:
        #     conn.close()
        pass  # this code is not working yet, cannot create DB within transaction although there is no transaction here

    # The idea is to retry execute the command in case of transient error (as some errors are valid and shouldnt be retried).
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(),
           retry=retry_if_exception(psycopg2.OperationalError))
    def execute(self, command: str):
        # TODO: add support for parameters to prevent SQL injection
        try:
            # this always run within transaction
            with psycopg2.connect(self.__get_connection_url()) as conn:
                # connection is only established when there's an action to minimize the time the connection is open
                with conn.cursor() as cursor:
                    cursor.execute(command)

        except psycopg2.Error as e:
            # not logging the command in case it has sensitive data
            logger.exception(f'[Error executing command] database:{self._database}')
        except Exception:
            logger.exception(f'[Unexpected Error executing command] database:{self._database}')

    def execute_with_records(self, command: str) -> []:
        try:
            # this always run within transaction
            with psycopg2.connect(self.__get_connection_url()) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(command)
                    result = cursor.fetchall()
                    return result

        except psycopg2.Error as e:
            # not logging the command in case it has sensitive data
            logger.exception(f'[Error executing command] database:{self._database}')
        except Exception:
            logger.exception(f'[Unexpected Error executing command] database:{self._database}')

        return []
