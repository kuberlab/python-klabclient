from dealerclient.api import base
from dealerclient.api import charts


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


class AppDestination(base.Resource):
    resource_name = 'AppDestination'


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

    def get_destinations(self, workspace):
        self._ensure_not_empty(workspace=workspace)

        url = '/workspace/%s/appdestinations' % workspace
        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [
            AppDestination(self, d) for d in base.extract_json(resp, None)
        ]

    def install(self, from_workspace, to_workspace, chart_name,
                project, app_name, values, version='latest',
                cluster_name=None, shared_cluster_id=None, env="master"):
        return charts.ChartManager(self.http_client).install(
            from_workspace,
            to_workspace,
            chart_name,
            project,
            app_name,
            values,
            version,
            cluster_name,
            shared_cluster_id,
            env
        )
