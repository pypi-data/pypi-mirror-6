from celery import task

@task
def send_mail(webservice, Message):
    """
    apply default.sender inside the task
    """
    webservice.SendMessageToEmails(Message)
