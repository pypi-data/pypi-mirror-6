from django.contrib import admin
from emailsys.models import EmailLog, SmsLog

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'time', 'to_email' ,'command', 'error' )
    list_filter = ['message_id', 'to_email', 'command',]

class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'time', 'to_number', 'error' )
    list_filter = ['message_id', 'to_number',]

admin.site.register(EmailLog, EmailMessageAdmin)
admin.site.register(SmsLog, SmsMessageAdmin)