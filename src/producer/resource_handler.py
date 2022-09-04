from common.metrics import Metrics, WebsiteMetrics
from common.configuration import Configuration
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ResourceHandler(object):
    def get_metrics(self) -> [Metrics]:
        pass


class WebsiteResourceHandler(ResourceHandler):
    def __init__(self):
        service_config = Configuration()
        self._resources = service_config.resource_list

    def __apply_regex(self, text: str) -> Optional[str]:
        # placeholder for optionally applying a regex on website html content
        return None

    def get_metrics(self) -> [Metrics]:
        result_list = []
        for resource in self._resources:
            try:
                response = requests.get(resource if resource.startswith('http') else 'http://' + resource)
                resp_time = response.elapsed.total_seconds()
                resp_code = response.status_code
                content = self.__apply_regex(response.text)
                result_list.append(WebsiteMetrics(resource, resp_time, resp_code, content))
            except (requests.exceptions.RequestException, Exception):
                # in case of error we do not send the metrics
                # some error considerations:
                # 1) if URL is invalid we should probably log and remove from resource list since no point of retrying
                # 2) transient network issue, TooManyRedirects, timeout - we should retry. MetwricsWriter is anyway going to make another call so I didnt add a special retry mechanism.
                # 3) Other HttpErrors will be logged and another call will be executed later
                logger.exception(f'[Error in making a request] resource:{resource}')

        return result_list
