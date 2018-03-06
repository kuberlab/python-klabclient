import six
import yaml

from klabclient.api import base


urlparse = six.moves.urllib.parse


class CatalogChart(base.Resource):
    resource_name = 'CatalogChart'


class ChartVersion(base.Resource):
    resource_name = 'ChartVersion'


class ChartManager(base.ResourceManager):
    resource_class = CatalogChart

    def catalog(self, search=None, page=None, limit=None):
        return self._catalog('/catalog/chart-app', search, page, limit)

    def list(self, workspace, search=None, page=None, limit=None):
        url = '/workspace/%s/chart-app' % workspace

        return self._catalog(url, search, page, limit)

    def get(self, workspace, chart_name, version=None):
        url = '/workspace/%s/chart-app/%s' % (workspace, chart_name)

        if version:
            url += '/versions/%s' % version

        return self._get(url)

    def get_yaml(self, workspace, chart_name, version=None):
        url = '/workspace/%s/chart-app/%s' % (workspace, chart_name)

        if not version:
            version = 'latest'

        url += '/versions/%s/yaml' % version

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return resp.text

    def delete(self, workspace, chart_name):
        url = '/workspace/%s/chart-app/%s' % (workspace, chart_name)

        return self._delete(url)

    def create(self, workspace, name, repo_url, repo_dir=None):
        url = '/workspace/%s/chart' % workspace

        body = {
            'Name': name,
            'RepositoryURL': repo_url,
            'RepositoryDir': repo_dir if repo_dir else '/'
        }

        return self._create(url, body)

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

        url = '/workspace/%s/chart-app/%s/versions/%s/install' % (
            from_workspace, chart_name, version
        )
        return self._create(url, install_chart_request)

    def list_versions(self, workspace, chart_name):
        url = '/workspace/%s/chart-app/%s/versions' % (workspace, chart_name)

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [ChartVersion(self, v) for v in base.extract_json(resp, None)]

    def get_values(self, workspace, chart_name, version='latest'):
        url = '/workspace/%s/chart-app/%s/versions/%s/values/yaml' % (
            (workspace, chart_name, version)
        )

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return resp.text
