from celery import task
from emailsys import default
from emailsys.models import Message

@task
def webservice_send_mail(subject, emails, content):
    """
    apply default.sender inside the task
    """

    msg = Message(subject)
    msg.emails = emails
    msg.content = content
    default.webservice.SendMessageToEmails(msg)

# @task
# def django_send_mail(subject, emails, content):
#     pass
