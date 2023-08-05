from django.contrib import admin
from emailsys.models import EmailLog

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'time', 'to_email' ,'command', 'error' )
    list_filter = ['message_id', 'to_email', 'command',]

admin.site.register(EmailLog, EmailMessageAdmin)