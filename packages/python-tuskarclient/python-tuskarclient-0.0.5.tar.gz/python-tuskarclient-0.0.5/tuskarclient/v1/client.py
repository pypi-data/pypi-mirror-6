#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tuskarclient.common import http
from tuskarclient.v1 import data_centers
from tuskarclient.v1 import flavors
from tuskarclient.v1 import nodes
from tuskarclient.v1 import overclouds
from tuskarclient.v1 import racks
from tuskarclient.v1 import resource_classes


class Client(http.HTTPClient):
    """Client for the Tuskar v1 HTTP API.

    :param string endpoint: Endpoint URL for the tuskar service.
    :param string token: Keystone authentication token.
    :param integer timeout: Timeout for client http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.racks = racks.RackManager(self)
        self.resource_classes = resource_classes.ResourceClassManager(self)
        self.flavors = flavors.FlavorManager(self)
        self.nodes = nodes.NodeManager(self)
        self.data_centers = data_centers.DataCenterManager(self)
        self.overclouds = overclouds.OvercloudManager(self)
