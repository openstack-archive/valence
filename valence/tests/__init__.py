from unittest import TestCase

from valence.api.route import app


class FunctionalTest(TestCase):

    def setUp(self):
        self.app = app.test_client()
