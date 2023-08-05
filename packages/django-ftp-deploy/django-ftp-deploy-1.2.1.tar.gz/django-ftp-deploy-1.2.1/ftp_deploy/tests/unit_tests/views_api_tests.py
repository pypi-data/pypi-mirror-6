from django.test import TestCase, RequestFactory

from mock import MagicMock
from mock import patch
from mock import call


from ftp_deploy.conf import *
from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import BitbucketAPIView
from ftp_deploy.tests.utils.factories import ServiceFactory


class BitbucketAPIViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()

    def test_bitbucket_api_dispatch_set_password_and_username_self_attributer(self):
        post_request = RequestFactory().post('/request')
        view = setup_view(BitbucketAPIView(), post_request)

        view.dispatch(MagicMock(name='request'))

        self.assertEqual(view.bitbucket_username, BITBUCKET_SETTINGS['username'])
        self.assertEqual(view.bitbucket_password, BITBUCKET_SETTINGS['password'])

    @patch('ftp_deploy.server.views.api.curl_connection')
    def test_bitbucket_api_POST_repositories_data_return_json_list_of_repositories(self, mock_curl_connection):
        post_request = RequestFactory().post('/request', {'data': 'respositories'})
        view = setup_view(BitbucketAPIView(), post_request)

        curl = MagicMock(name='curl')
        curl.perform = MagicMock('curl_perform', return_value=dict())
        mock_curl_connection.return_value = curl
        view.bitbucket_username = BITBUCKET_SETTINGS['username']
        view.bitbucket_password = BITBUCKET_SETTINGS['password']

        view.post(view.request)

        mock_curl_connection.assert_called_once_with(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'])
        calls = [call.authenticate(), call.perform('https://bitbucket.org/api/1.0/user/repositories'), call.close()]
        curl.assert_has_calls(calls)

    @patch('ftp_deploy.server.views.api.curl_connection')
    def test_bitbucket_api_POST_add_hook_data_perform_adding_hook_to_repository(self, mock_curl_connection):

        post_request = RequestFactory().post('/request', {'data': 'addhook'})
        view = setup_view(BitbucketAPIView(), post_request)
        view.get_object = lambda: self.service
        view.bitbucket_username = BITBUCKET_SETTINGS['username']
        view.bitbucket_password = BITBUCKET_SETTINGS['password']

        curl = MagicMock(name='curl')
        curl.perform_post = MagicMock('curl_perform', return_value=dict())
        mock_curl_connection.return_value = curl

        view.post(view.request)

        mock_curl_connection.assert_called_once_with(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'])
        calls = [call.authenticate(), call.perform_post('https://api.bitbucket.org/1.0/repositories/%s/%s/services/ ' %
                                                        (BITBUCKET_SETTINGS['username'], self.service.repo_slug_name), 'type=POST&URL=http://testserver%s' % (self.service.hook_url())), call.close()]
        curl.assert_has_calls(calls)
