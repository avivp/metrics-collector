# ------------------------------
# Writer class is responsible to get different types of metrics
# from different resource handlers and publish to a message queue
# the MQ client is sent as dependency injection
# to enable mocking and future changing of underlying technology
# ------------------------------
import logging
from common.configuration import Configuration
from resource_handler import WebsiteResourceHandler


logger = logging.getLogger(__name__)


class MetricsWriter(object):
    def __init__(self, queue_client):
        self._queue_client = queue_client
        self._resource_handlers = [WebsiteResourceHandler()]  # can extend to other metrics types
        service_config = Configuration()
        # self.ping_interval_second = service_config.ping_interval_second

    def write(self):
        try:
            # consider sending messages in batches to reduce no. of requests (reduce load and cost)
            for handler in self._resource_handlers:
                metrics_list = handler.get_metrics()
                published = []
                not_published = []
                for metrics in metrics_list:
                    if not self._queue_client.put_message(metrics.to_json()):
                        not_published.append(metrics.resource_name)
                    else:
                        published.append(metrics.resource_name)
                logger.info(f'[Metrics were published] resources: {",".join(published)}. '
                            f'[The following metrics were failed to be published. please retry. resources: {",".join(not_published)}')

        except Exception:
            # TODO: add different handling for different error cases
            logger.exception(f'[Unexpected error occurred]')

