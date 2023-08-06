from mock import patch, call

from django.test import TestCase

from ftp_deploy.tasks import deploy_task

class TaskTest(TestCase):
	@patch('ftp_deploy.tasks.Deploy')
	def test_task_perform_deploy(self,mock_deploy):
		deploy_task('host','payload','service')
		mock_deploy.assert_has_calls([call('host', 'payload', 'service', None), call().perform()])

