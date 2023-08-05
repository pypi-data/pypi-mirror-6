from celery import task
from emailsys import default
from emailsys.models import Message

@task
def send_mail(Message):
    """
    apply default.sender inside the task
    """
    c = default.sender
    c.send(Message)
