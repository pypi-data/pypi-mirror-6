from django_coverage.coverage_runner import CoverageRunner
from django_nose import NoseTestSuiteRunner

import logging
selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
selenium_logger.setLevel(logging.ERROR)


class NoseCoverageTestRunner(CoverageRunner, NoseTestSuiteRunner):

    """Custom test runner that uses nose and coverage"""
    pass
