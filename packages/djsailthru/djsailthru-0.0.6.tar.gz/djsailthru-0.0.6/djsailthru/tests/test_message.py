import json

from djsailthru.mail.message import SailthruEmailMessage
from djsailthru.tests.mock_backend import SailthruBackendMockTestCase

from sailthru.sailthru_error import SailthruClientError


class TestSailthruEamilMessage(SailthruBackendMockTestCase):
    def setUp(self):
        super(TestSailthruEamilMessage, self).setUp()
        self.message = SailthruEmailMessage('foo@bar.com', 'Email Template')

    def test_send_mail_without_vars(self):
        self.message.send()
        self.assert_sailthru_called()
        data = self.get_api_call_data()
        self.assertEqual(data['template'], 'Email Template')
        self.assertEqual(data['email'], 'foo@bar.com')
        self.assertEqual(data['vars'], {})

    def test_send_email_with_vars(self):
        params = {'foo': 'bar'}
        message = SailthruEmailMessage('foo@bar.com', 'Email Template', vars=params)
        message.send()
        self.assert_sailthru_called()
        data = self.get_api_call_data()
        self.assertEqual(data['template'], 'Email Template')
        self.assertEqual(data['email'], 'foo@bar.com')
        self.assertEqual(data['vars'], {'vars': params})

    def test_send_email_bad_email(self):
        message = SailthruEmailMessage('foo@barcom', 'Email Template')
        self.mock_api_post.return_value = self.MockResponse(
            is_ok=False,
            json=json.dumps({'errormsg': 'Invalid email: foo@barcom', 'error': 11}))
        with self.assertRaises(SailthruClientError):
            message.send()
