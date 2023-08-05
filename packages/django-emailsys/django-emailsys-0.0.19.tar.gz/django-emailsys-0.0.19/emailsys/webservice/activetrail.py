'''
Created on Dec 3, 2013

@author: Ron Sneh <me@ronsneh.com>
'''

from emailsys import settings
from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import 

class Activetrail(object):
    url = 'http://webapi.mymarketing.co.il/Messaging/MessagingService.asmx?WSDL'
    client = None
    session_id = None
    
    def __init__(self):
        self._login()

    def _connect(self):
        imp = Import('http://www.w3.org/2001/XMLSchema') # the schema to import.
        imp.filter.add('http://tempuri.org/') # the schema to import into.
        d = ImportDoctor(imp)
        
        self.client = Client(self.url, doctor=d)

    def _login(self):
        self._connect()
        self._authHeader()
        
        login_result = self.client.service.Login()
        
        if login_result is None:
            # Maybe we need to connect again ?
            raise Exception('Do something?')
        
        self.session_id = login_result
        
    def _authHeader(self):
        auth_header = self.client.factory.create('AuthHeader')
        auth_header.Username = settings.ACTIVETRAIL_USER
        auth_header.Password = settings.ACTIVETRAIL_PASS
        auth_header.Token = self.session_id
        
        self.client.set_options(soapheaders=auth_header)
        
    def SendMessageToEmails(self, Message):
        self._connect()
        self._authHeader()

        # from address for webMessage
        address = self.client.factory.create('Address')
        # Should be taken from settings
        address.FromName = Message.from_name
        address.FromEmail = Message.from_addr
        
        
        webMessage = self.client.factory.create('WebMessage')
        webMessage.Subject = Message.subject
        webMessage.From = address
        webMessage.ExternalMessageId = '15' # Unknown
        webMessage.LanguageId = settings.ACTIVETRAIL_LANGID;
        webMessage.UserPlaceholders = False;
        webMessage.AddStatistics = False;
        webMessage.AddAdvertisement = False;
        webMessage.SignMessage = False;
        webMessage.AddUnsubscribeLink = False;
        webMessage.AddPrintButton = False;
        
        # This name is the campign name
        # webMessage.Name = "";

        # Need to know what this priority means
        webMessage.Priority = '1';
        
        arrayOfBodyParts = self.client.factory.create('ArrayOfBodyPart')
        bodyParts = self.client.factory.create('BodyPart')
#         bodyPartFormat = self.client.factory.create('BodyPartFormat')

        bodyParts.BodyPartEncoding = Message.encoding
        bodyParts.BodyPartFormat = Message.content_type
        bodyParts.Body = Message.content

        arrayOfBodyParts.BodyPart = bodyParts        
        webMessage.BodyParts = arrayOfBodyParts

        emails = self.client.factory.create('ArrayOfString')

        for email in Message.emails:
            emails.string.append(email)

        try:        
            # We should get the number of the total sent amount
            response = self.client.service.SendMessageToEmails(webMessage, emails)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

    def SendSMSCampaignToMobiles(self, SmsCampaign):
        self._connect()
        self._authHeader()
        
        webSmsCampaign = self.client.factory.create('WebSmsCampaign')
        webSmsCampaign.Name = SmsCampaign.from_name
        webSmsCampaign.FromNumber = SmsCampaign.from_number
        webSmsCampaign.Content = SmsCampaign.content
        
        to_numbers = self.client.factory.create('ArrayOfString')
        
        for number in SmsCampaign.to_numbers:
            to_numbers.string.append(number)

        try:        
            # We should get the number of the total sent amount
            response = self.client.service.SendSMSCampaignToMobiles(webSmsCampaign, to_numbers)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            