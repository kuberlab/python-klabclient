import six


from dealerclient.api import base


urlparse = six.moves.urllib.parse


class CatalogChart(base.Resource):
    resource_name = 'CatalogChart'


class CatalogManager(base.ResourceManager):
    resource_class = CatalogChart

    def _charts(self, url, search=None, type=None, page=None, limit=None):
        qparams = {}

        if search:
            qparams['search'] = search

        if type:
            qparams['type'] = type

        if limit:
            qparams['limit'] = limit

        if page:
            qparams['page'] = page

        query_string = (
            "?%s" % urlparse.urlencode(list(qparams.items()))
            if qparams else ""
        )

        return self._list(
            '%s%s' % (url, query_string), response_key=None
        )

    def catalog(self, search=None, type=None, page=None, limit=None):
        return self._charts('/catalog/charts', search, type, page, limit)

    def list(self, workspace, search=None, type=None, page=None, limit=None):
        url = '/workspace/%s/charts' % workspace

        return self._charts(url, search, type, page, limit)

    def get(self, workspace, chart_name):
        url = '/workspace/%s/charts/%s' % (workspace, chart_name)

        return self._get(url)

    def delete(self, workspace, chart_name):
        url = '/workspace/%s/charts/%s' % (workspace, chart_name)

        return self._delete(url)
