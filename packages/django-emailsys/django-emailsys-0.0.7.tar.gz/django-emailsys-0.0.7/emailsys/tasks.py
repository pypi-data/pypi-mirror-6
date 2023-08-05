from celery import task
from emailsys import default

@task
def send_mail(Message):
    """
    apply default.sender inside the task
    """
    webservice = default.webservice
    webservice.SendMessageToEmails(Message)
