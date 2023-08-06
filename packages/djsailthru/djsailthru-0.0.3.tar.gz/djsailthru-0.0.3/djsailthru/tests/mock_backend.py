from mock import patch

from django.test import TestCase
from .utils import override_settings


@override_settings(SAILTHRU_API_KEY="FAKE_API_KEY_FOR_TESTING",
                   SAILTHRU_API_SECRET="FAKE_API_SECRET_FOR_TESTING",
                   EMAIL_BACKEND="djsailthru.mail.backends.base.SailthruEmailBackend")
class SailthruBackendMockTestCase(TestCase):

    class MockResponse:
        """requests.post return value mock sufficient for SailthruEmailBackend"""
        def __init__(self, is_ok=True, get_status_code=200, json=None):
            self._status_code = get_status_code
            self._json = json if json is not None else ['']
            self._is_ok = is_ok

        def json(self):
            return self._json

        def is_ok(self):
            return self._is_ok

        def get_body(self):
            return self._json

        def get_status_code(self):
            return self._get_status_code

    def setUp(self):
        self.patch = patch('sailthru.sailthru_client.SailthruClient.api_post', autospec=True)
        self.mock_api_post = self.patch.start()
        self.mock_api_post.return_value = self.MockResponse()

    def assert_sailthru_called(self):
        if self.mock_api_post.call_args is None:
            raise AssertionError("Sailthru API was not called")

        (args, kwargs) = self.mock_api_post.call_args
        if args[1] != 'send':
            raise AssertionError('sailthru api was not called with `send` method')
        if not isinstance(args[2], dict):
            raise AssertionError('sailthru was called with out vars')

    def get_api_call_data(self):
        """Returns the data posted to the Sailthru API.

        Fails test if API wasn't called.
        """
        if self.mock_api_post.call_args is None:
            raise AssertionError("Sailthru API was not called")
        (args, kwargs) = self.mock_api_post.call_args
        try:
            post_data = args[2]
        except IndexError:
            raise AssertionError('sailthru was called with out vars')
        return post_data
