
from klabclient.api import workspaces
from klabclient.tests.unit import base


WORKSPACE = {
    'Type': 'private',
    'Name': 'my',
    'DisplayName': 'my',
    'Picture': 'url',
    'Can': ['read', 'manage']
}

URL_TEMPLATE = '/workspace'
URL_TEMPLATE_NAME = '/workspace/%s'


class TestWorkspaces(base.BaseClientTest):
    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json=[WORKSPACE])

        workspace_list = self.workspaces.list()

        self.assertEqual(1, len(workspace_list))

        wf = workspace_list[0]

        self.assertEqual(
            workspaces.Workspace(self.workspaces, WORKSPACE).to_dict(),
            wf.to_dict()
        )

    def test_get(self):
        url = self.TEST_URL + URL_TEMPLATE_NAME % 'my'
        self.requests_mock.get(url, json=WORKSPACE)

        wf = self.workspaces.get('my')

        self.assertIsNotNone(wf)
        self.assertEqual(
            workspaces.Workspace(self.workspaces, WORKSPACE).to_dict(),
            wf.to_dict()
        )
