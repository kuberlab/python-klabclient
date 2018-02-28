
from klabclient.api import base
from klabclient import exceptions


class SharedCluster(base.Resource):
    resource_name = 'SharedCluster'

    # "ID": "221",
    # "DisplayName": "testshare",
    # "From": {
    #             "WorkspaceName": "kuberlab-demo",
    #             "ProjectName": "demotest",
    #             "ClusterName": "minikube"
    #         },
    # "Active": true,
    # "WorkspaceName": "kuberlab-demo"


class SharedClusterManager(base.ResourceManager):
    resource_class = SharedCluster

    def share(self, id, emails=None, workspaces=None):
        self._ensure_not_empty(id=id)

        if not emails and not workspaces:
            raise exceptions.IllegalArgumentException(
                'Provide either emails or workspace names.'
            )

        if emails and not isinstance(emails, list):
            raise exceptions.IllegalArgumentException(
                'Emails must be list.'
            )
        if workspaces and not isinstance(workspaces, list):
            raise exceptions.IllegalArgumentException(
                'Workspaces must be list.'
            )
        body = {}
        if emails:
            body['Emails'] = ','.join(emails)
        if workspaces:
            body['WorkspaceNames'] = ','.join(workspaces)

        return self._create(
            '/sharedclusters/own/%s/share' % id,
            body,
        )

    def list_available(self):
        url = '/sharedclusters/available'
        return self._list(url, response_key=None)

    def list_own(self):
        url = '/sharedclusters/own'
        return self._list(url, response_key=None)

    def get_available(self, workspace, id):
        self._ensure_not_empty(workspace=workspace, id=id)

        return self._get('/sharedclusters/available/%s/%s' % (workspace, id))

    def get_own(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/sharedclusters/own/%s' % id)

    def delete_available(self, workspace, id):
        self._ensure_not_empty(workspace=workspace, id=id)

        self._delete('/sharedclusters/available/%s/%s' % (workspace, id))

    def delete_own(self, id):
        self._ensure_not_empty(id=id)

        self._delete('/sharedclusters/own/%s' % id)
