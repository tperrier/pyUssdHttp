''' Africa's Talking USSD API '''

import abc

#Local Imports
from .http import UssdHttpBase

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
        self.set_commands_and_input()

    def clean(self):
        self.clean_phone_number()

    def clean_phone_number(self):
        if self.phone_number.startswith('+254'):
            self.phone_number = '0' + self.phone_number[4:]
