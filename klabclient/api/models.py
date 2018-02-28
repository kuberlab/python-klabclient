
from klabclient.api import base
from klabclient import utils


class Model(base.Resource):
    resource_name = 'Model'


class ModelManager(base.ResourceManager):
    resource_class = Model

    def create(self, workspace, name, published=False,
               display_name=None, picture=None):
        self._ensure_not_empty(name=name)

        if not display_name:
            display_name = name

        body = {
            'Name': name,
            'DisplayName': display_name
        }
        if picture:
            body['Picture'] = picture
        if published is not None:
            body['Published'] = published

        return self._create(
            '/workspace/%s/mlmodels' % workspace,
            body,
        )

    def update(self, workspace, name, description=None,
               display_name=None, keywords=None):
        self._ensure_not_empty(id=id, name=name)

        body = {}
        if keywords:
            body['Keywords'] = keywords
        if description:
            body['Description'] = description
        if display_name:
            body['DisplayName'] = display_name

        return self._update(
            '/workspace/%s/mlmodels' % workspace,
            body
        )

    def list(self, workspace):
        return self._list(
            '/workspace/%s/mlmodels' % workspace, response_key=None
        )

    def get(self, workspace, name):
        self._ensure_not_empty(name=name)

        return self._get(
            '/workspace/%s/mlmodels/%s' % (workspace, name)
        )

    def delete(self, workspace, name, confirm=None):
        self._ensure_not_empty(name=name)

        url = '/workspace/%s/mlmodels/%s' % (workspace, name)
        if confirm:
            url += '?confirm=%s' % confirm

        self._delete(url)

    def upload(self, workspace, name, version, path):
        url = '%s/workspace/%s/mlmodels/%s/versions/%s/upload' % (
            self.http_client.base_url, workspace, name, version
        )

        stream = utils.stream_targz(path)

        resp = self.http_client.crud_provider.post(
            url,
            # data=form_data,
            files={'model': ('%s.tar.gz' % name, stream)}
        )

        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return self.resource_class(
            self, base.extract_json(resp, response_key=None)
        )
