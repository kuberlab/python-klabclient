import copy
import requests
import six

from klabclient.api import app_tasks
from klabclient.api import apps
from klabclient.api import charts
from klabclient.api import clusters
from klabclient.api import datasets
from klabclient.api import httpclient
from klabclient.api import models
from klabclient.api import organizations
from klabclient.api import projects
from klabclient.api import sharedclusters
from klabclient.api import storage
from klabclient.api import workspaces
from klabclient import exceptions

parse = six.moves.urllib.parse
_DEFAULT_KUBERLAB_URL = "https://go.kuberlab.io/api/v0.2"


class Client(object):
    def __init__(self, session=requests, **kwargs):
        # We get the session at this point, as some instances of session
        # objects might have mutexes that can't be deep-copied.
        req = copy.deepcopy(kwargs)
        kuberlab_url = req.get('kuberlab_url')

        if kuberlab_url and not isinstance(kuberlab_url, six.string_types):
            raise RuntimeError('Kuberlab url should be a string.')

        if not kuberlab_url:
            kuberlab_url = _DEFAULT_KUBERLAB_URL

        http_client = httpclient.HTTPClient(
            kuberlab_url,
            session=session,
            **req
        )

        # Create all resource managers.

        self.apps = apps.AppManager(http_client)
        self.app_tasks = app_tasks.AppTaskManager(http_client)
        self.charts = charts.ChartManager(http_client)
        self.clusters = clusters.ClusterManager(http_client)
        self.datasets = datasets.DatasetManager(http_client)
        self.models = models.ModelManager(http_client)
        self.organizations = organizations.OrganizationManager(http_client)
        self.projects = projects.ProjectManager(http_client)
        self.sharedclusters = sharedclusters.SharedClusterManager(http_client)
        self.storage = storage.StorageManager(http_client)
        self.workspaces = workspaces.WorkspaceManager(http_client)


def create_session(base_url=_DEFAULT_KUBERLAB_URL, **kwargs):
    """Creates a new session for kuberlab client.

    :param base_url: kuberlab API base url.
    :param username: username
    :param password: password
    :param token: API token created via API
    :return: request.Session object.
    """
    username = kwargs.get('username')
    password = kwargs.get('password')
    token = kwargs.get('token')

    ses = requests.Session()
    if token:
        ses = requests.Session()
        ses.headers['Authorization'] = 'Bearer %s' % token
        return ses
    elif username and password:
        auth_url = '%s/auth/login' % base_url
        resp = ses.post(
            auth_url,
            json={'LoginOrEmail': username, 'Password': password},
            headers={'Content-Type': 'application/json'}
        )
        if resp.status_code != 200:
            raise exceptions.KuberlabClientException(
                'Invalid auth: %s.' % resp.content
            )
        return ses

    raise exceptions.KuberlabClientException(
        "Provide either token or username and password."
    )
