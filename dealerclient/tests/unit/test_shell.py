
import mock

import dealerclient.tests.unit.base_shell_test as base


class TestShell(base.BaseShellTests):

    @mock.patch('dealerclient.api.client.Client')
    @mock.patch('dealerclient.api.client.create_session')
    def test_command_no_dealer_url(self, session_mock, client_mock):
        self.shell(
            'workspace-list --config wrong'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertIsNone(params[1]['dealer_url'])

    @mock.patch('dealerclient.api.client.Client')
    @mock.patch('dealerclient.api.client.create_session')
    def test_command_with_dealer_url(self, session_mock, client_mock):
        self.shell(
            '--dealer-url=http://localhost:8082/api/v0.2 workspace-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args

        self.assertEqual('http://localhost:8082/api/v0.2',
                         params[1]['dealer_url'])
