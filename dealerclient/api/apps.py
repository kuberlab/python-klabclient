import json
import yaml

from dealerclient.api import app_tasks
from dealerclient.api import base
from dealerclient.api import charts
from dealerclient import exceptions


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
    # "Configuration": {"spec": {...}}
    def __init__(self, manager, data):
        super(App, self).__init__(manager, data)
        self.config = None

        if hasattr(self, 'Configuration'):
            self.config = self.Configuration

    def get_sources(self):
        if not self.config:
            return []

        sources = []
        for source_raw in self.config.get('spec', {}).get('volumes'):
            sources += [AppSource(self, source_raw)]

        return sources

    def get_config_tasks(self):
        m = app_tasks.AppTaskManager(self.manager.http_client)
        tasks = []
        for t in self.config['spec']['tasks']:
            task_dict = {
                'app': self.Name,
                'config': yaml.safe_dump(t),
                'name': t.get('name'),
                'workspace': self.WorkspaceName
            }
            task = app_tasks.AppTask(m, task_dict)
            tasks.append(task)

        return tasks

    def get_config_task(self, name):
        tasks = self.get_config_tasks()
        for t in tasks:
            if t.name == name:
                return t

        raise exceptions.DealerClientException(
            'App task [name=%s] not found.' % name
        )

    def upload_data(self, source_name, data, target_path):
        url = (
            '/workspace/%s/application/%s/upload'
            % (self.WorkspaceName, self.Name)
        )
        resp = self.manager.http_client.post_file(
            url,
            {'source': source_name},
            target_path,
            data
        )
        if resp.status_code >= 400:
            self.manager._raise_api_exception(resp)

        return resp.text

    def upload_file(self, source_name, filepath):
        url = (
            '/workspace/%s/application/%s/upload'
            % (self.WorkspaceName, self.Name)
        )
        base_path = filepath.split('/')[-1]
        with open(filepath, 'rb') as f:
            resp = self.manager.http_client.post_file(
                url,
                {'source': source_name},
                base_path,
                f
            )
        if resp.status_code >= 400:
            self.manager._raise_api_exception(resp)

        return resp.text


class AppSource(base.Resource):
    resource_name = 'AppSource'


class AppDestination(base.Resource):
    resource_name = 'AppDestination'


class AppStatus(base.Resource):
    resource_name = 'AppStatus'


class AppPackage(base.Resource):
    resource_name = 'AppPackage'


class AppManager(base.ResourceManager):
    resource_class = App

    def list(self, workspace):
        url = '/workspace/%s/application' % workspace
        return self._list(url, response_key=None)

    def get(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)

        return self._get('/workspace/%s/application/%s' % (workspace, name))

    def status(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)

        url = '/workspace/%s/application/%s/status' % (workspace, name)
        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [
            AppStatus(self, d) for d in base.extract_json(resp, None)
        ]

    def packages_list(self, workspace, name, all=False):
        self._ensure_not_empty(workspace=workspace, name=name)

        url = (
            '/workspace/%s/application/%s/packages?all=%s'
            % (workspace, name, all)
        )
        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [
            AppPackage(self, d) for d in base.extract_json(resp, None)
        ]

    def packages_install(self, workspace, name, manager, packages):
        self._ensure_not_empty(workspace=workspace, name=name)

        url = '/workspace/%s/application/%s/packages' % (workspace, name)

        body = {
            'manager': manager,
            'packages': packages
        }

        resp = self.http_client.crud_provider.post(
            self.http_client.base_url + url,
            data=json.dumps(body),
            headers={'Content-Type': 'application/json'},
            stream=True,
        )
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        # Return iterator
        return resp.iter_lines()

    def delete(self, workspace, name, force=False):
        self._ensure_not_empty(workspace=workspace, name=name)

        self._delete(
            '/workspace/%s/application/%s?%s' % (workspace, name, force)
        )

    def disable(self, workspace, name, force=False):
        self._ensure_not_empty(workspace=workspace, name=name)
        url = (
            '/workspace/%s/application/%s/disable?force=%s'
            % (workspace, name, force)
        )
        return self._create(url, {})

    def enable(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)
        url = '/workspace/%s/application/%s/enable' % (workspace, name)
        return self._create(url, {})

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
