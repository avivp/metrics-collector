import pytest
from common.metrics import WebsiteMetrics


def test_normalize():
    sites = []
    sites.append("www.hbo.com")
    sites.append("hbo.com/foor/bar")
    sites.append("http://hbo.com/foo?bar")
    sites.append("https://www.hbo.com")

    for s in sites:
        metrics = WebsiteMetrics(s, 1, 200)
        assert metrics.resource_name == "hbo.com", f"website name {s} not normalized"
