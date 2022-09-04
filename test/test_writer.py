import pytest
import requests
import json
from datetime import timedelta
from metrics_writer import MetricsWriter
from common.configuration import Configuration

class MockHttpResponse:
    def __init__(self):
        self.elapsed = timedelta(milliseconds=43)
        self.status_code = 200


def test_write_msg(monkeypatch, mq_client):
    def mock_get(*args, **kwargs):
        return MockHttpResponse()

    service_config = Configuration()
    resource_list = service_config.resource_list

    monkeypatch.setattr(requests, "get", mock_get)

    writer = MetricsWriter(mq_client)
    writer.write()
    assert len(mq_client.queue) == len(resource_list), "queue has missing messages"
    data = json.loads(mq_client.queue[0])
    assert data['response_time'] == 0.043, "response time is incorrect"
    assert data['status_code'] == 200, "status code is incorrect"


def test_no_write_msg_on_network_error(monkeypatch, mq_client):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(requests, "get", mock_get)

    writer = MetricsWriter(mq_client)
    writer.write()
    assert len(mq_client.queue) == 0, "queue has missing messages"
