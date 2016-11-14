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
        self.text = post.get('text')

        # Get array of all commands sent to far
        self.commands = self.text.split('*')
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

    @abc.abstractmethod
    def response(self,prefix,text):
        pass
