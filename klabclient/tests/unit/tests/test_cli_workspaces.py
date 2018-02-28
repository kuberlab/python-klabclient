
import mock

from klabclient.api import workspaces
from klabclient.commands import workspaces as workspace_cmd
from klabclient.tests.unit import base


WORKSPACE_DICT = {
    'Type': 'private',
    'Name': 'my',
    'DisplayName': 'my',
    'Picture': 'url',
    'Can': ['read', 'manage']
}

WORKSPACE = workspaces.Workspace(mock, WORKSPACE_DICT)


class TestCLIWorkspaces(base.BaseCommandTest):
    def test_list(self):
        self.client.workspaces.list.return_value = [WORKSPACE]

        result = self.call(workspace_cmd.List)

        self.assertEqual(
            [('my', 'private', 'my', 'url')],
            result[1]
        )

    def test_get(self):
        self.client.workspaces.get.return_value = WORKSPACE

        result = self.call(workspace_cmd.Get, app_args=['name'])

        self.assertEqual(
            ('my', 'private', 'my', 'url', '[\n    "read", \n    "manage"\n]'),
            result[1]
        )
