''' Africa's Talking USSD API '''

import abc

#Local Imports
from UssdHttp.transports.http import UssdHttpBase

class AfricasTalkingUssd(UssdHttpBase):

    __metaclass__ = abc.ABCMeta

    def __init__(self,post):
        """
        Creates and AfricasTalkingUssd object from  POST response.

        Request object defined in the Africas Talking USSD documentation.
        http://docs.africastalking.com/ussd
        """

        self.session_id = post.get('sessionId')
        self.service_code = post.get('serviceCode')
        self.phone_number = post.get('phoneNumber')
        self.text = post.get('text','')

        self.clean()

        # Get array of all commands sent to far
        self.commands = self.text.split('*')
        if self.commands == ['']:
            self.commands = []
            self.input = ''
        else:
            self.input = self.commands[-1]

    def send(self,text,has_next=False):
        """ Send a ussd screen over transport """
        if has_next:
            return self.con(text)
        else:
            return self.end(text)

    def con(self,text):
        return self.response('CON',text)

    def end(self,text):
        return self.response('END',text)

    def __len__(self):
        return len(self.commands)

    def clean(self):
        self.clean_phone_number()

    def clean_phone_number(self):
        if self.phone_number.startswith('+254'):
            self.phone_number = '0' + self.phone_number[4:]

    def __str__(self):
        return "{0.service_code} on {0.phone_number} id {0.session_id}".format(self)

    @abc.abstractmethod
    def response(self,prefix,text):
        pass
