''' Africa's Talking USSD API '''

#Local Imports
from .http import UssdHttpBase

class AfricasTalkingUssd(UssdHttpBase):

    def send(self,text,has_next=False):
        """ Send a ussd screen over transport """
        if has_next:
            return self.response('CON',text)
        else:
            return self.response('END',text)

    def response(self,prefix,text):
        return u'{0} {1}'.format(prefix,text)

    def clean(self):
        self.clean_phone_number()

    def clean_phone_number(self):
        if self.phone_number.startswith('+254'):
            self.phone_number = '0' + self.phone_number[4:]
