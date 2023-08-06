from django.core.mail import EmailMessage


class SailthruEmailMessage(EmailMessage):
    def __init__(self, email_address, template_name, connection=None, **kwargs):
        self.template_name = template_name
        self.email_address = email_address
        self.vars = kwargs

        self.data = {
            "template": self.template_name,
            "email": self.email_address,
            "vars": self.vars
        }
        self.connection = connection

    def message(self):
        """
        This allows SailthruEmailMessage to function within Django's
        localmem EmailBackend when running tests
        """
        pass

    def recipients(self):
        return self.email_address
