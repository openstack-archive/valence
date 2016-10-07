import os
from pecan import set_config
from pecan.testing import load_test_app
from unittest import TestCase

__all__ = ['FunctionalTest']


class FunctionalTest(TestCase):
    """Functional Test Class

    Used for functional tests where you need to test your
    literal application and its integration with the framework.

    """

    def setUp(self):
        self.app = load_test_app(os.path.join(
            os.path.dirname(__file__),
            'config.py'
        ))

    def tearDown(self):
        set_config({}, overwrite=True)
