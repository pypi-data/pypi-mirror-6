from django.core.mail import EmailMessage


class SailthruEmailMessage(EmailMessage):
    def __init__(self, email_address, template_name, connection=None, **kwargs):
        self.data = {
            "template": template_name,
            "email": email_address,
            "vars": kwargs
        }
        self.connection = connection

    def send(self, fail_silently=False):
        """Sends the email message."""
        return self.get_connection(fail_silently).send_messages([self])
