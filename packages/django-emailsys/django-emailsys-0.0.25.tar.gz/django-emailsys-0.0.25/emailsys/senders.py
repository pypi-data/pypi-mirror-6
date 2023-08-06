from emailsys import settings, default
from django.core.mail.message import EmailMultiAlternatives
# from emailsys.tasks import webservice_send_mail, webservice_send_sms
from .tasks import SendSms, SendEmail

'''
TODO: Implement BaseSender for basic settings and functionality
''' 
class BaseSender(object):
    pass

class DjangoSender(BaseSender):
    def send(self, Message=None):
        fail_silently = False

        if Message is None:
            raise Exception("Cannot generate message to send")
    
        # Send emails.
        for addr in Message.emails:
            msg = EmailMultiAlternatives(Message.subject, Message.content_txt, Message.from_addr, [addr])
            if msg.content_html is not None:
                msg.attach_alternative(msg.content_html, "text/html")
            
            msg.send(fail_silently=fail_silently)
    pass

class ActivetrailSender(BaseSender):
    def send(self, Message=None):
        
        if Message is None:
            raise Exception("Cannot generate message to send")

        # Check if USE_CELERY
        if settings.USE_CELERY:
            SendEmail().delay(Message.subject, Message.emails, Message.content, Message.command)
        else:
            webservice = default.webservice
            webservice.SendMessageToEmails(Message)
            
    def sms(self, SmsCampaign=None):
        
        if SmsCampaign is None:
            raise Exception("Cannot generate message to send")

        # Check if USE_CELERY
        if settings.USE_CELERY:
            SendSms().delay(SmsCampaign.to_numbers, SmsCampaign.content)
        else:
            webservice = default.webservice
            webservice.SendSMSCampaignToMobiles(SmsCampaign)
