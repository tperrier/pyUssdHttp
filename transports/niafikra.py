''' Niafikra USSD API '''

#Local Imports
from .http import UssdHttpBase

class NiafikraUssd(UssdHttpBase):
        """ Creates a USSD object from  POST response coming from Niafikra """

        INPUT_APPEND = False
