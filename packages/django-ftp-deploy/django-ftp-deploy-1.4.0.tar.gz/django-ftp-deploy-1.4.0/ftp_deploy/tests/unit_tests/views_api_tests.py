from django.test import TestCase, RequestFactory

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call


from ftp_deploy.conf import *
from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import RepoAPIView
from ftp_deploy.tests.utils.factories import ServiceFactory


class RepoAPIViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()

    @patch('ftp_deploy.server.views.api.repository_api')
    def test_repo_api_dispatch_initialize_repository_api(self, mock_respository_api):
        get_request = RequestFactory().get('/request')
        view = setup_view(RepoAPIView(), get_request)
        view.dispatch(MagicMock(), 'xx')

        mock_respository_api.assert_called_once_with('xx')

    def test_repo_api_POST_repositories_data_perform_repositories_call(self):
        post_request = RequestFactory().post('/request', {'data': 'respositories'})
        view = setup_view(RepoAPIView(), post_request)
        view.repo_api = MagicMock(name='repo_api')
        view.repo_api.repositories = MagicMock(return_value="")
        view.post(view.request, 'bb')

        view.repo_api.assert_has_calls([call.repositories()])

    def test_repo_api_POST_add_hook_data_perform_add_hook_call(self):
        post_request = RequestFactory().post('/request', {'data': 'addhook'})
        view = setup_view(RepoAPIView(), post_request)
        view.get_object = lambda: self.service
        view.repo_api = MagicMock(name='repo_api')
        view.repo_api.add_hook = MagicMock(return_value="")
        view.post('request', 'bb')

        view.repo_api.assert_has_calls([call.add_hook(self.service, 'request')])
