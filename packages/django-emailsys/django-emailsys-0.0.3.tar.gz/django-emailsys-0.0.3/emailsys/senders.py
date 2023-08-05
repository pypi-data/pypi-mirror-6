from os.path import basename
from emailsys import settings, default, tasks
from django.core.mail.message import EmailMultiAlternatives

class DjangoSender(object):
    def send(self, Message):
        fail_silently = False

        Message.add_email("me@ronsneh.com")
        
        # Load attachments and create name/data tuples.
        # Not supported yet
        attachments = None
        attachments_parts = []
        if attachments is not None:
            for attachment in attachments:
                # Attachments can be pairs of name/data, or filesystem paths.
                if not hasattr(attachment, "__iter__"):
                    with open(attachment, "rb") as f:
                        attachments_parts.append((basename(attachment), f.read()))
                else:
                    attachments_parts.append(attachment)
    
        # Send emails.
        for addr in Message.emails:
            msg = EmailMultiAlternatives(Message.subject, Message.content_txt, Message.from_addr, [addr])
            if msg.content_html is not None:
                msg.attach_alternative(msg.content_html, "text/html")
            for parts in attachments_parts:
                name = parts[0]
                msg.attach(name, parts[1])
            
            msg.send(fail_silently=fail_silently)
    pass

class ActivetrailSender(object):
    def send(self, Message):
        
        if Message is None:
            # die?
            pass
        
        webservice = default.webservice
        # Check if USE_CELERY
        if settings.USE_CELERY:
            tasks.send_mail(Message)
        else:
            webservice.SendMessageToEmails(Message)
    pass