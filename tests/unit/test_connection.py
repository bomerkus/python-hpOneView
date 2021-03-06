# -*- coding: utf-8 -*-
###
# (C) Copyright (2016) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
import json
import mock
import unittest

from http.client import HTTPSConnection
from hpOneView.connection import connection
from hpOneView.exceptions import HPOneViewException
from mock import call


class ConnectionTest(unittest.TestCase):

    def setUp(self):
        self.host = '127.0.0.1'
        self.connection = connection(self.host)
        self.accept_language_header = {
            'Accept-Language': 'en_US'
        }
        self.default_headers = {
            'X-API-Version': 200,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.merged_headers = {
            'X-API-Version': 200,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'en_US'
        }
        self.request_body = {"request body": "content"}
        self.response_body = {"response body": "content"}
        self.dumped_request_body = json.dumps(self.request_body.copy())
        self.expected_response_body = self.response_body.copy()

    def __make_http_response(self, status):
        mock_response = mock.Mock(status=status)
        mock_response.read.return_value = json.dumps(self.response_body).encode('utf-8')
        if status == 200 or status == 202:
            mock_response.getheader.return_value = '/task/uri'
        return mock_response

    def test_default_headers(self):
        self.assertEqual(self.default_headers, self.connection._headers)

    def test_headers_with_api_version_300(self):
        self.connection = connection(self.host, 300)

        expected_headers = self.default_headers.copy()
        expected_headers['X-API-Version'] = 300
        self.assertEqual(expected_headers, self.connection._headers)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_do_rest_call_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        self.connection.post('/path', self.request_body)

        mock_request.assert_called_once_with('POST', '/path', self.dumped_request_body, self.default_headers)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_do_rest_calls_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.post('/path', self.request_body)

        expected_calls = [call('POST', '/path', self.dumped_request_body, self.default_headers),
                          call('GET', '/task/uri', '', self.default_headers)]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_send_merged_headers_when_headers_provided(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.post('/path', self.request_body, custom_headers=self.accept_language_header)

        expected_calls = [call('POST', mock.ANY, mock.ANY, self.merged_headers), mock.ANY]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_return_body_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        result = self.connection.post('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (None, self.expected_response_body)
        self.assertEqual(expected_result, result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_return_tuple_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        result = self.connection.post('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (self.expected_response_body, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_raise_exception_when_status_internal_error(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=400)

        try:
            self.connection.post('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_post_should_raise_exception_when_status_not_found(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=404)

        try:
            self.connection.post('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_do_rest_call_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        self.connection.put('/path', self.request_body)

        mock_request.assert_called_once_with('PUT', '/path', self.dumped_request_body, self.default_headers)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_do_rest_calls_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.put('/path', self.request_body)

        expected_calls = [call('PUT', '/path', self.dumped_request_body, self.default_headers),
                          call('GET', '/task/uri', '', self.default_headers)]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_send_merged_headers_when_headers_provided(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.put('/path', self.request_body, custom_headers=self.accept_language_header)

        expected_calls = [call('PUT', mock.ANY, mock.ANY, self.merged_headers), mock.ANY]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_return_body_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        result = self.connection.put('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (None, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_return_tuple_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        result = self.connection.put('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (self.expected_response_body, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_raise_exception_when_status_internal_error(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=400)

        try:
            self.connection.put('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_put_should_raise_exception_when_status_not_found(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=404)

        try:
            self.connection.put('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_do_rest_call_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        self.connection.patch('/path', self.request_body)

        mock_request.assert_called_once_with('PATCH', '/path', self.dumped_request_body, self.default_headers)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_do_rest_calls_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.patch('/path', self.request_body)

        expected_calls = [call('PATCH', '/path', self.dumped_request_body, self.default_headers),
                          call('GET', '/task/uri', '', self.default_headers)]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_send_merged_headers_when_headers_provided(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.patch('/path', self.request_body, custom_headers=self.accept_language_header)

        expected_calls = [call('PATCH', mock.ANY, mock.ANY, self.merged_headers), mock.ANY]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_return_body_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        result = self.connection.patch('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (None, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_return_tuple_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        result = self.connection.patch('/path', self.response_body, custom_headers=self.accept_language_header)

        expected_result = (self.expected_response_body, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_raise_exception_when_status_internal_error(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=400)

        try:
            self.connection.patch('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_patch_should_raise_exception_when_status_not_found(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=404)

        try:
            self.connection.patch('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_do_rest_calls_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        self.connection.delete('/path')

        mock_request.assert_called_once_with('DELETE', '/path', json.dumps(''), self.default_headers)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_do_rest_calls_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.delete('/path')

        expected_calls = [call('DELETE', '/path', json.dumps(''), self.default_headers),
                          call('GET', '/task/uri', '', self.default_headers)]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_send_merged_headers_when_headers_provided(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        self.connection.delete('/path', custom_headers=self.accept_language_header)

        expected_calls = [call('DELETE', mock.ANY, mock.ANY, self.merged_headers), mock.ANY]
        self.assertEqual(expected_calls, mock_request.call_args_list)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_return_body_when_status_ok(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=200)

        result = self.connection.delete('/path', custom_headers=self.accept_language_header)

        expected_result = (None, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_return_tuple_when_status_accepted(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=202)

        result = self.connection.delete('/path', custom_headers=self.accept_language_header)

        expected_result = (self.expected_response_body, self.expected_response_body)
        self.assertEqual(result, expected_result)

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_raise_exception_when_status_internal_error(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=400)

        try:
            self.connection.delete('/path')
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()

    @mock.patch.object(HTTPSConnection, 'request')
    @mock.patch.object(HTTPSConnection, 'getresponse')
    def test_delete_should_raise_exception_when_status_not_found(self, mock_response, mock_request):
        mock_request.return_value = {}
        mock_response.return_value = self.__make_http_response(status=404)

        try:
            self.connection.delete('/path', self.request_body)
        except HPOneViewException as e:
            self.assertEqual(e.msg, self.expected_response_body)
        else:
            self.fail()
