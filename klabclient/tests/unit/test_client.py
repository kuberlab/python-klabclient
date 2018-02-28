
import os
import tempfile

import mock
from oslotest import base

from klabclient.api import client

DEALER_HTTP_URL = 'https://go.kuberlab.io/api/v0.2'
DEALER_HTTPS_URL = DEALER_HTTP_URL.replace('http', 'https')


class BaseClientTests(base.BaseTestCase):

    @mock.patch('klabclient.api.httpclient.HTTPClient')
    def test_dealer_url_default(self, http_client_mock):
        client.Client(
            username='dealer',
            password='dealer',
        )

        self.assertTrue(http_client_mock.called)
        dealer_url_for_http = http_client_mock.call_args[0][0]
        self.assertEqual(DEALER_HTTP_URL, dealer_url_for_http)

    @mock.patch('klabclient.api.httpclient.HTTPClient')
    def test_dealer_url_https_insecure(self, http_client_mock):
        expected_args = (
            DEALER_HTTPS_URL,
        )

        client.Client(
            kuberlab_url=DEALER_HTTPS_URL,
            username='dealer',
            project_name='dealer',
            cacert=None,
            insecure=True
        )

        self.assertTrue(http_client_mock.called)
        self.assertEqual(http_client_mock.call_args[0], expected_args)
        self.assertEqual(http_client_mock.call_args[1]['insecure'], True)

    @mock.patch('klabclient.api.httpclient.HTTPClient')
    def test_dealer_url_https_secure(self, http_client_mock):
        fd, cert_path = tempfile.mkstemp(suffix='.pem')

        expected_args = (
            DEALER_HTTPS_URL,
        )

        try:
            client.Client(
                kuberlab_url=DEALER_HTTPS_URL,
                username='dealer',
                password='dealer',
                cacert=cert_path,
                insecure=False
            )
        finally:
            os.close(fd)
            os.unlink(cert_path)

        self.assertTrue(http_client_mock.called)
        self.assertEqual(http_client_mock.call_args[0], expected_args)
        self.assertEqual(http_client_mock.call_args[1]['cacert'], cert_path)

    def test_dealer_url_https_bad_cacert(self):

        self.assertRaises(
            ValueError,
            client.Client,
            kuberlab_url=DEALER_HTTPS_URL,
            username='dealer',
            password='dealer',
            cacert='/path/to/foobar',
            insecure=False
        )

    @mock.patch('logging.Logger.warning')
    def test_dealer_url_https_bad_insecure(self, log_warning_mock):
        fd, path = tempfile.mkstemp(suffix='.pem')

        try:
            client.Client(
                kuberlab_url=DEALER_HTTPS_URL,
                cacert=path,
                insecure=True
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(log_warning_mock.called)
