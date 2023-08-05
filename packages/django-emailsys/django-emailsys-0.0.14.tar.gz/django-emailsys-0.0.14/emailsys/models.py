from emailsys.settings import FROM_ADDRESS, FROM_NAME, REPLAY_TO, CONTENT_TYPE
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

    template = None
    
    emails = []
    
    def __init__(self, subject, emails=None, content=None):
        self.subject = subject
        self.content = content
        self.emails = emails

    def __unicode__(self):
        return self.emails

    def add_email(self, _email):
        self.emails.append(_email)
    
    def use_template(self, template, context):
        # need to know what to pass with context
        self.content = get_message_template(template, context)
        pass