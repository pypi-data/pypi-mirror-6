from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

from sailthru import sailthru_client as sc
from sailthru.sailthru_error import SailthruClientError

from djsailthru.mail.message import SailthruEmailMessage


class SailthruEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super(SailthruEmailBackend, self).__init__(*args, **kwargs)

        self.sailthru_client = sc.SailthruClient(
            settings.SAILTHRU_API_KEY,
            settings.SAILTHRU_API_SECRET,
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1

    def _send(self, email_message):
        if not isinstance(email_message, SailthruEmailMessage):
            raise TypeError('`email_message is not of type `SailthruEmailMessage')

        response = self.sailthru_client.api_post("send", email_message.data)
        email_message.sailthru_response = None
        if response.is_ok():
            email_message.sailthru_response = response.get_body()
            return True
        else:
            if not self.fail_silently:
                raise SailthruClientError(response.get_body())
            else:
                return False
