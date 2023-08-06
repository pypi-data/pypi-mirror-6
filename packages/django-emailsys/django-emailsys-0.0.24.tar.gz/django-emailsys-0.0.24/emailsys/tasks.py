from emailsys import default
from emailsys.models import Message, SmsCampaign

import celery

class SendMail(celery.Task):
    name = 'emailsys.webservice_send_mail'
    
    def run(self, subject, emails, content, command):
        """
        apply default.sender inside the task
        """
    
        msg = Message(subject)
        msg.emails = emails
        msg.content = content
        msg.command = command
        default.webservice.SendMessageToEmails(msg)

class SendSms(celery.Task):
    name = 'emailsys.webservice_send_sms'
    
    def run(self, to_numbers, content):
        """
        apply default.sender inside the task
        """
    
        sms = SmsCampaign(content)
        sms.to_numbers = to_numbers
        sms.content = content
        default.webservice.SendSMSCampaignToMobiles(sms)
