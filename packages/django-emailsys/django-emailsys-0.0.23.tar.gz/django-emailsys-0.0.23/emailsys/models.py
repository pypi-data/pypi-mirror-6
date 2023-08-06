from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy  as _
from emailsys.settings import FROM_ADDRESS, FROM_NAME, REPLAY_TO, CONTENT_TYPE, SMS_FROM_NUMBER,\
    SMS_FROM_NAME
from emailsys.helpers import get_message_template

class EmailLog(models.Model):
    message_id = models.CharField(_('Message Id'), max_length=10)
    to_email = models.EmailField(_('To Email'), max_length=254)
    time = models.DateTimeField(_('Sent At'), default=timezone.now())
    subject = models.CharField(_('Subject'),max_length=150,null=True)
    command = models.CharField(_('Command'),max_length=50)
    response = models.TextField(_('Response'),max_length=50)
    error = models.SmallIntegerField(_('Error'),default=0)
    
    def __unicode__(self):
        return self.to_email

    class Meta:
        verbose_name = _('Email Logs')
        verbose_name_plural = _('Email Logs')


'''
Message and SMS object (not models)
'''
class Message(object):
    # settings
    from_addr = FROM_ADDRESS
    from_name = FROM_NAME
    reply_to = REPLAY_TO
    encoding = 'utf-8'
    content_type = CONTENT_TYPE
    
    subject = None
    content = None
    emails = None
    template = None
    command = None
    
    def __init__(self, subject, emails=None, content=None):
        self.subject = subject
        self.content = content
        self.emails = emails

    def __unicode__(self):
        return self.emails

    def add_email(self, _email):
        if self.emails is None:
            self.emails = []
            
        self.emails.append(_email)
    
    def set_command(self, command):
        self.command = command

    def use_template(self, template, context):
        self.content = get_message_template(template, context)
    
class SmsCampaign(object):
    from_number = SMS_FROM_NUMBER
    from_name = SMS_FROM_NAME
    
    content = None
    
    to_numbers = None
    
    def __init__(self, content=None, to_numbers=None):
        self.content = content
        self.to_numbers = to_numbers
        
    def __unicode__(self):
        return self.to_numbers
    
    def add_number(self, _number):
        if self.to_numbers is None:
            self.to_numbers = []
            
        self.to_numbers.append(_number)
        
    def validate(self):
        # need to validate the campaign before sending
        pass
