import json
import yaml

import six

from klabclient.api import app_tasks
from klabclient.api import base
from klabclient.api import charts
from klabclient import exceptions


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
            self.full_config = data

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
                'config': yaml.safe_dump(t, default_flow_style=False),
                'app_config': yaml.safe_dump(
                    self.full_config,
                    default_flow_style=False
                ),
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

        raise exceptions.KuberlabClientException(
            'App task [name=%s] not found.' % name
        )

    def set_config_task(self, task_config):
        if not isinstance(task_config, dict):
            raise exceptions.KuberlabClientException(
                'App task config must be dict, not %s.'
                % task_config.__class__.__name__
            )
        name = task_config.get('name')
        if not name:
            raise exceptions.KuberlabClientException(
                'App task config name required, missing "name" key.'
            )
        # Check if task exists
        try:
            self.get_config_task(name)
        except exceptions.KuberlabClientException:
            # Task doesn't exist. Add a new task.
            self.config['spec']['tasks'].append(task_config)
        else:
            # Replace task.
            tasks = self.config['spec']['tasks']
            self.config['spec']['tasks'] = [
                task_config if x['name'] == name else x for x in tasks
            ]

        return self.update_with_config(self.config)

    def update_with_config(self, config):
        if not isinstance(config, dict):
            raise exceptions.KuberlabClientException(
                'App config must be dict, not %s.'
                % config.__class__.__name__
            )

        self.full_config['Configuration'] = config
        return self.manager.update(
            self.WorkspaceName, self.Name, self.full_config
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

    def catalog(self, search=None, page=None, limit=None):
        return self._catalog('/catalog/chart-mlapp-v2', search, page, limit)

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

        return AppStatus(self, base.extract_json(resp, None))

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

    def update(self, workspace, name, config):
        # PUT /workspace/{workspace}/application/{application}
        self._ensure_not_empty(workspace=workspace, name=name)
        url = '/workspace/%s/application/%s' % (workspace, name)
        return self._update(url, config)

    def get_destinations(self, workspace):
        self._ensure_not_empty(workspace=workspace)

        url = '/workspace/%s/appdestinations' % workspace
        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [
            AppDestination(self, d) for d in base.extract_json(resp, None)
        ]

    def get_yaml(self, workspace, chart_name, version=None):
        url = '/workspace/%s/chart-mlapp-v2/%s' % (workspace, chart_name)

        if not version:
            version = 'latest'

        url += '/versions/%s/yaml' % version

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return resp.text

    def list_versions(self, workspace, chart_name):
        url = (
            '/workspace/%s/chart-mlapp-v2/%s/versions'
            % (workspace, chart_name)
        )

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [
            charts.ChartVersion(self, v)
            for v in base.extract_json(resp, None)
        ]

    def get_values(self, workspace, chart_name, version='latest'):
        url = '/workspace/%s/chart-mlapp-v2/%s/versions/%s/values/yaml' % (
            (workspace, chart_name, version)
        )

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return resp.text

    def install(self, from_workspace, to_workspace, chart_name,
                app_name, values, project=None, version='latest',
                cluster_name=None, shared_cluster_id=None,
                cluster_id=None, env="master"):
        install_chart_request = {
            "target_application": app_name,
            "environment": env,
            "workspace_name": to_workspace,
        }

        if project:
            install_chart_request["project_name"] = project

        if isinstance(values, dict):
            install_chart_request['values_yaml'] = yaml.safe_dump(values)
        if isinstance(values, six.string_types):
            install_chart_request['values_yaml'] = values

        if cluster_id:
            install_chart_request['cluster_id'] = cluster_id
        elif cluster_name:
            install_chart_request['clusters'] = [cluster_name]
        elif shared_cluster_id:
            install_chart_request['shared_cluster_id'] = shared_cluster_id

        url = '/workspace/%s/chart-mlapp-v2/%s/versions/%s/install' % (
            from_workspace, chart_name, version
        )
        return self._create(url, install_chart_request)
