
from klabclient.api import base


class Dataset(base.Resource):
    resource_name = 'Dataset'


class DatasetManager(base.ResourceManager):
    resource_class = Dataset

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
            '/workspace/%s/dataset' % workspace,
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
            '/workspace/%s/dataset' % workspace,
            body
        )

    def catalog(self, search=None, page=None, limit=None):
        return self._catalog('/catalog/dataset', search, page, limit)

    def list(self, workspace):
        return self._list(
            '/workspace/%s/dataset' % workspace, response_key=None
        )

    def get(self, workspace, name):
        self._ensure_not_empty(name=name)

        return self._get(
            '/workspace/%s/dataset/%s' % (workspace, name)
        )

    def delete(self, workspace, name, confirm=None):
        self._ensure_not_empty(name=name)

        url = '/workspace/%s/dataset/%s' % (workspace, name)
        if confirm:
            url += '?confirm=%s' % confirm

        self._delete(url)
