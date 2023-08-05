""" Django email backend which behaves just like the default SMTP backend
except that it only sends messages to a select set of addresses.

Use the setting EMAIL_ALLOWED_RECIPIENTS to specify allowed addresses as
regular expressions. The filter uses the Python 'match' method to check
the regular expressions against the email recipients.

It only matches the email addresses and not the optional 'name' part of
recipients. All addresses are lowercased before matching.

Example settings:

    EMAIL_BACKEND = 'django_filtered_mail.mail.EmailBackend'

    EMAIL_ALLOWED_RECIPIENTS = (
        r'*.@dreamsolution.nl$',
        r'^some.one@gmail.com$',
    )

"""
import re
import logging
from email.utils import parseaddr

from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.core.mail.message import sanitize_address
from django.conf import settings


logger = logging.getLogger(__name__)


assert hasattr(settings, 'EMAIL_ALLOWED_RECIPIENTS'), (
    'Django settings is missing the EMAIL_ALLOWED_RECIPIENTS setting.')


def filter_recipients(recipients, patterns, encoding):
    """Filter out recipients not allowed in 'staging' environments
    Only looks at email addresses and not the 'name' part of recipients.
    """
    filtered = []
    for recip in recipients:
        recip = sanitize_address(recip, encoding)
        nm, addr = parseaddr(recip.lower())
        for pattern in patterns:
            if pattern.match(addr) is not None:
                filtered.append(recip)
                break
        else:
            logger.debug(u'Removed {0} from EmailMessage'.format(recip))

    return filtered


def filter_message(email_message, patterns):
    """Filter out recipients in to, cc and bcc of EmailMessage
    """
    for attr in ('to', 'cc', 'bcc'):
        recipients = getattr(email_message, attr, [])
        if recipients:
            recipients = filter_recipients(recipients, patterns,
                                           email_message.encoding)
            setattr(email_message, attr, recipients)
    return email_message


class EmailBackend(SMTPBackend):
    """ Django email backend which behaves just like the default SMTP backend
    except that it only sends messages to a filtered list of addresses.
    """
    def set_allowed_recipients(self, patterns):
        self._allowed_recipients = []
        for recip in patterns:
            self._allowed_recipients.append(re.compile(recip))

    def _send(self, email_message):
        if not getattr(self, '_allowed_recipients'):
            self.set_allowed_recipients(settings.EMAIL_ALLOWED_RECIPIENTS)

        email_message = filter_message(email_message, self._allowed_recipients)
        return super(EmailBackend, self)._send(email_message)
