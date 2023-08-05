"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from emailsys import default
from emailsys.models import SmsCampaign

class SimpleTest(TestCase):
    def test_send_sms(self):
        content = 'english content'
        
        default_sender = default.sender
        sms = SmsCampaign(content)
        sms.add_number('0525308278')
        default_sender.sms(sms)