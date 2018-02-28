
import copy

import mock
from six.moves.urllib import parse as urlparse

from oslo_utils import uuidutils

from klabclient.api import httpclient
from klabclient.tests.unit import base

API_BASE_URL = 'http://cloud-dealer:8082/api/v0.2'
API_URL = '/workspace'

EXPECTED_URL = API_BASE_URL + API_URL

AUTH_TOKEN = uuidutils.generate_uuid()

EXPECTED_AUTH_HEADERS = {
    'Token': AUTH_TOKEN,
}

EXPECTED_REQ_OPTIONS = {
    'headers': EXPECTED_AUTH_HEADERS
}

EXPECTED_BODY = {
    'k1': 'abc',
    'k2': 123,
    'k3': True
}


class HTTPClientTest(base.BaseClientTest):

    def setUp(self):
        super(HTTPClientTest, self).setUp()
        self.client = httpclient.HTTPClient(
            API_BASE_URL,
            username='dealer',
            password='dealer',
        )

    def assertExpectedBody(self):
        text = self.requests_mock.last_request.text
        form = urlparse.parse_qs(text, strict_parsing=True)

        self.assertEqual(len(EXPECTED_BODY), len(form))

        for k, v in EXPECTED_BODY.items():
            self.assertEqual([str(v)], form[k])

        return form

    def test_get_request_options(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')

        self.client.get(API_URL)

        self.assertTrue(m.called_once)

    def test_get_request_options_with_headers_for_post(self):
        m = self.requests_mock.post(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.post(API_URL, EXPECTED_BODY, headers=headers)

        self.assertTrue(m.called_once)
        self.assertEqual('bar', headers['foo'])
        self.assertExpectedBody()

    def test_get_request_options_with_headers_for_put(self):
        m = self.requests_mock.put(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.put(API_URL, EXPECTED_BODY, headers=headers)

        self.assertTrue(m.called_once)
        self.assertEqual('bar', headers['foo'])
        self.assertExpectedBody()

    def test_get_request_options_with_headers_for_delete(self):
        m = self.requests_mock.delete(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.delete(API_URL, headers=headers)

        self.assertTrue(m.called_once)
        self.assertEqual('bar', headers['foo'])

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_get(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')
        self.client.get(API_URL)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'get',
            None
        )
        self.assertTrue(m.called_once)

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_post(self):
        m = self.requests_mock.post(EXPECTED_URL, status_code=201, text='text')
        self.client.post(API_URL, EXPECTED_BODY)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'post',
            None
        )

        self.assertTrue(m.called_once)
        self.assertExpectedBody()

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_put(self):
        m = self.requests_mock.put(EXPECTED_URL, json={})
        self.client.put(API_URL, EXPECTED_BODY)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'put',
            None
        )

        self.assertTrue(m.called_once)
        self.assertExpectedBody()

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_delete(self):
        m = self.requests_mock.delete(EXPECTED_URL, text='text')
        self.client.delete(API_URL)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'delete',
            None
        )

        self.assertTrue(m.called_once)
