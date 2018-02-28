
from klabclient.api import base


class Cluster(base.Resource):
    resource_name = 'Cluster'


class ClusterManager(base.ResourceManager):
    resource_class = Cluster

    def list(self, workspace):
        return self._list(
            '/workspace/%s/clusters' % workspace,
            response_key=None,
        )

    def get(self, workspace, identifier):
        self._ensure_not_empty(identifier=identifier)

        return self._get(
            '/workspace/%s/clusters/%s' % (workspace, identifier)
        )
