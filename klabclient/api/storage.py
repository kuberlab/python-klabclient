
from klabclient.api import base


class Storage(base.Resource):
    resource_name = 'Storage'


class StorageManager(base.ResourceManager):
    resource_class = Storage

    def list(self, workspace, cluster_id):
        return self._list(
            '/workspace/%s/clusters/%s/storage' % (workspace, cluster_id),
            response_key=None,
        )
