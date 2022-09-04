import pytest
from metrics import WebsiteMetrics
from metrics_reader import MetricsReader
from resource_storage_handler import WebsiteSqlHandler

def test_read_valid_metrics_and_store(monkeypatch, mq_client, db_client):

    table = []
    def mock_store_metrics(*args, **kwargs):
        table.extend(args[1])

    monkeypatch.setattr(WebsiteSqlHandler, "store_metrics", mock_store_metrics)
    metrics = WebsiteMetrics("site.com", 0.4, 404)
    mq_client.put_message(metrics.to_json())
    metrics = WebsiteMetrics("site.com", 0.32, 200)
    mq_client.put_message(metrics.to_json())
    reader = MetricsReader(mq_client, db_client)
    reader.read()
    assert len(table) == 2, "missing records in metrics table"
    assert table[0].status_code == 404, "status code is incorrect"
    assert table[1].response_time == 0.32, "response time is incorrect"



def test_read_invalid_metrics_and_not_store(monkeypatch, mq_client, db_client):
    table = []

    def mock_store_metrics(*args, **kwargs):
        table.extend(args[1])

    monkeypatch.setattr(WebsiteSqlHandler, "store_metrics", mock_store_metrics)
    mq_client.put_message("invalid msg")
    reader = MetricsReader(mq_client, db_client)
    reader.read()
    assert len(table) == 0, "metrics table should be empty"

