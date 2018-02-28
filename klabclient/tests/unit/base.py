
import mock
from oslotest import base
import requests
from requests_mock.contrib import fixture

from klabclient.api import client


class BaseClientTest(base.BaseTestCase):
    _client = None
    TEST_URL = 'http://dealer.example.com:8082/api/v0.2'

    def setUp(self):
        super(BaseClientTest, self).setUp()

        self._client = client.Client(
            session=requests,
            username="test",
            password="test",
            kuberlab_url=self.TEST_URL
        )

        self.workspaces = self._client.workspaces
        self.requests_mock = self.useFixture(fixture.Fixture())


class BaseCommandTest(base.BaseTestCase):
    def setUp(self):
        super(BaseCommandTest, self).setUp()
        self.app = mock.Mock()
        self.client = self.app.client

    def call(self, command, app_args=[], prog_name=''):
        cmd = command(self.app, app_args)

        parsed_args = cmd.get_parser(prog_name).parse_args(app_args)

        return cmd.take_action(parsed_args)
