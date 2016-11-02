from unittest import TestCase
from valence.api.route import app

__all__ = ['FunctionalTest']


class FunctionalTest(TestCase):
    """Functional Test Class

    Used for functional tests where you need to test your
    literal application and its integration with the framework.

    """

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass
