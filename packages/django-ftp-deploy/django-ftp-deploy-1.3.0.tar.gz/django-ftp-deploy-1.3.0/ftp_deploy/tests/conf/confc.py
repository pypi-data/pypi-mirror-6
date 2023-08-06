"""Conf file implemented coverage report """

from conf import *

TEST_RUNNER = 'ftp_deploy.tests.conf.testrunner.NoseCoverageTestRunner'
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'urls$', 'migrations', 'admin$', 'conf$', '__init__'
]

COVERAGE_MODULE_EXCLUDES += DJANGO_APPS + THIRD_PARTY_APPS
COVERAGE_REPORT_HTML_OUTPUT_DIR = join(dirname(dirname(__file__)), 'coverage')
