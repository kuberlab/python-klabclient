
from klabclient.api import base


class Organization(base.Resource):
    resource_name = 'Organization'


class OrganizationManager(base.ResourceManager):
    resource_class = Organization

    def create(self, name, display_name=None,
               picture=None, url=None, phone=None):
        self._ensure_not_empty(name=name)

        if not display_name:
            display_name = name

        body = {
            'Name': name,
            'DisplayName': display_name
        }
        if picture:
            body['Picture'] = picture
        if url:
            body['Url'] = url
        if phone:
            body['Phone'] = phone

        return self._create(
            '/org',
            body,
        )

    def update(self, id, name, display_name=None,
               picture=None, url=None, phone=None):
        self._ensure_not_empty(id=id, name=name)

        if not display_name:
            display_name = name

        body = {
            'Name': name,
            'DisplayName': display_name
        }
        if picture:
            body['Picture'] = picture
        if url:
            body['Url'] = url
        if phone:
            body['Phone'] = phone

        return self._update('/org/%s' % id, body)

    def list(self):
        return self._list('/org', response_key=None)

    def get(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        return self._get('/org/%s' % identifier)

    def delete(self, identifier, confirm=None):
        self._ensure_not_empty(identifier=identifier)

        url = '/org/%s' % identifier
        if confirm:
            url += '?confirm=%s' % confirm

        self._delete(url)
