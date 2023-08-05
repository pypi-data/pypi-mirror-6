from django.utils.functional import LazyObject
from emailsys.helpers import get_module_class
from emailsys import settings

class WebService(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.WEBSERVICE)()

class Sender(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.SENDER)() 

webservice = WebService()
sender = Sender()