# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import six

from dealerclient.api import base
from dealerclient import utils


urlparse = six.moves.urllib.parse


class Workspace(base.Resource):
    resource_name = 'Workspace'


class WorkspaceManager(base.ResourceManager):
    resource_class = Workspace

    def create(self, definition):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._create(
            '/workspace',
            definition,
        )

    def update(self, definition, id):
        self._ensure_not_empty(definition=definition)

        url = '/workspace/%s' % id

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        resp = self.http_client.put(
            url,
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        if id:
            return self.resource_class(self, base.extract_json(resp, None))

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'workspaces')]

    def list(self):
        return self._list(
            '/workspace',
            response_key=None,
        )

    def get(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        return self._get('/workspace/%s' % identifier)

    def delete(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        self._delete('/workspace/%s' % identifier)
