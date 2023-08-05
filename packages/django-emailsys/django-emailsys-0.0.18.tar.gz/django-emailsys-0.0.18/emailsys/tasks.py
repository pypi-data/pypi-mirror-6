from celery import task
from emailsys import default
from emailsys.models import Message, SmsCampaign

@task
def webservice_send_mail(subject, emails, content):
    """
    apply default.sender inside the task
    """

    msg = Message(subject)
    msg.emails = emails
    msg.content = content
    default.webservice.SendMessageToEmails(msg)

@task
def webservice_send_sms(to_numbers, content):
    """
    apply default.sender inside the task
    """

    sms = SmsCampaign(content)
    sms.to_numbers = to_numbers
    sms.content = content
    default.webservice.SendSMSCampaignToMobiles(sms)
