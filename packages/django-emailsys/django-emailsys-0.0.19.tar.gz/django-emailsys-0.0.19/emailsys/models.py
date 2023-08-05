from emailsys.settings import FROM_ADDRESS, FROM_NAME, REPLAY_TO, CONTENT_TYPE, SMS_FROM_NUMBER
from emailsys.helpers import get_message_template 

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
    
    def use_template(self, template, context):
        self.content = get_message_template(template, context)
    
class SmsCampaign(object):
    from_number = SMS_FROM_NUMBER
    from_name = FROM_NAME
    
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