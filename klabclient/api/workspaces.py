
from klabclient.api import base


class Workspace(base.Resource):
    resource_name = 'Workspace'


class WorkspaceManager(base.ResourceManager):
    resource_class = Workspace

    def list(self):
        return self._list(
            '/workspace',
            response_key=None,
        )

    def get(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        return self._get('/workspace/%s' % identifier)
