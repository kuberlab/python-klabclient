
from dealerclient.api import base


class App(base.Resource):
    resource_name = 'App'

    # "Name": "styles-set",
    # "DisplayName": "styles-set",
    # "Description": "Style Tranfer demo",
    # "Environment": "master",
    # "ClusterName": "minikube",
    # "Enabled": true,
    # "WorkspaceName": "kuberlab-demo",
    # "WorkspaceDisplayName": "KuberLab Demo",
    # "ProjectName": "demotest",
    # "ProjectDisplayName": "demotest"


class AppManager(base.ResourceManager):
    resource_class = App

    def list(self, workspace):
        url = '/workspace/%s/application' % workspace
        return self._list(url, response_key=None)

    def get(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)

        return self._get('/workspace/%s/application/%s' % (workspace, name))

    def delete(self, workspace, name, force=False):
        self._ensure_not_empty(workspace=workspace, name=name)

        self._delete(
            '/workspace/%s/application/%s?%s' % (workspace, name, force)
        )
