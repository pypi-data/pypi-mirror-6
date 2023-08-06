from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

## Default WebService
DEFAULT_WEBSERVICE = 'emailsys.webservice.activetrail.Activetrail'

## Default Sender (django, activetrail)
## django - the regular send_mail function send_mail (https://docs.djangoproject.com/en/dev/topics/email/)
DEFAULT_SENDER = 'emailsys.senders.ActivetrailSender'

# Default content type (HTML, TXT)
DEFAULT_CONTENT_TYPE = 'HTML'

# Default lang id (119 = Hebrew)
DEFAULT_LANGID = 119

USE_CELERY = getattr(settings, "EMAIL_SYS_USE_CELERY", True)
SENDER = getattr(settings, "EMAIL_SYS_SENDER", DEFAULT_SENDER)
WEBSERVICE = getattr(settings, "EMAIL_SYS_WEBSERVICE", DEFAULT_WEBSERVICE)
CONTENT_TYPE = getattr(settings, "EMAIL_SYS_CONTET_TYPE", DEFAULT_CONTENT_TYPE)
FROM_NAME = getattr(settings, "EMAIL_SYS_FROM_NAME", None)
FROM_ADDRESS = getattr(settings, "EMAIL_SYS_FROM_ADDRESS", None)
REPLAY_TO = getattr(settings, "EMAIL_SYS_REPLAY_TO", FROM_ADDRESS)
SMS_FROM_NUMBER = getattr(settings, "EMAIL_SYS_SMS_FROM_NUMBER", None)
SMS_FROM_NAME = getattr(settings, "EMAIL_SYS_SMS_FROM_NAME", None)

ACTIVETRAIL_USER = getattr(settings, "EMAIL_SYS_ACTIVETRAIL_USER", None)
ACTIVETRAIL_PASS = getattr(settings, "EMAIL_SYS_ACTIVETRAIL_PASS", None)
ACTIVETRAIL_LANGID = getattr(settings, "EMAIL_SYS_ACTIVETRAIL_LANGID", DEFAULT_LANGID)

if USE_CELERY:
    try:
        import celery
    except ImportError:
        raise ImproperlyConfigured("Could not import celery")
