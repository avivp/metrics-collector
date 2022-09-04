import pytest
from postgresql_client import PostgresqlClient

@pytest.fixture
def db_client():
    client = PostgresqlClient("x", 1, "y", "z")
    yield client


class MockProducerClient():
    def __init__(self):
        self.queue = []

    def put_message(self, msg) -> bool:
        self.queue.append(msg)
        return True

    def get_messages(self) -> []:
        list = self.queue
        self.queue = []
        return list


@pytest.fixture
def mq_client():
    return MockProducerClient()   # not using yield because we want a new instance everytime
