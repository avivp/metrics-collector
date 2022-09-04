from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import json


class ResourceType(Enum):
    WEBSITE = "WEBSITE"


@dataclass
class Metrics(object):
    resource_name: str
    resource_type: ResourceType
    response_time: int
    status_code: int
    content: str
    create_time_utc: str        # i have used str and not datetime object to make json serialization easier

    # for simplicity I assume all metrics will have these 3 in common : time, code and content
    # in reality this is probably not the case so we will have derived class support for different types of resources
    # each resource has different set of metrics
    def __init__(self, resource_name: str, resource_type: ResourceType, response_time: int, status_code: int,
                 content: str = None):
        self.resource_name = resource_name
        self.resource_type = resource_type.value
        self.response_time = response_time
        self.status_code = status_code
        self.content = content
        self.create_time_utc = f'{datetime.now(timezone.utc)}'   #  ISO 8601 timeformat

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, data: []):
        obj = cls(data['resource_name'], ResourceType[data['resource_type']], data['response_time'], data['status_code'], data['content'])
        obj.create_time_utc = data['create_time_utc']
        return obj

@dataclass
class WebsiteMetrics(Metrics):

    def __init__(self, resource_name: str, response_time: int, status_code: int, content: str = None):
        super().__init__(self.normalize_name(resource_name), ResourceType.WEBSITE, response_time,
                         status_code, content)

    @classmethod
    def from_json(cls, data: []):
        obj = cls(data['resource_name'], data['response_time'],
                  data['status_code'], data['content'])
        obj.create_time_utc = data['create_time_utc']
        obj.resource_type = ResourceType.WEBSITE.value
        return obj

    def normalize_name(self, name: str):
        # Here is a very basic idea for normalizing the site name to its core domain.
        # NOTE: no validation that name is a valid domain name
        # based on assumption that www.site.com and site.com are the same
        # stripping off http prefix and trailing query - but there are extra points to consider for example removing port number
        # (to check with product manager if x.com/foo and x.com/bar are considered different resources to monitor)
        # Note: python 3.9: name.removeprefix('http://').removeprefix('https://').removeprefix('www')
        if name.startswith('http://'):
            name = name[len('http://'):]
        elif name.startswith('https://'):
            name = name[len('https://'):]
        if name.startswith('www.'):
            name = name[len('www.'):]
        return name.split('/', 1)[0]
