
import abc
from .. import utils

class UssdHttpBase(object):
    """ Base class to define the USSD HTTP Python Object

        Attributes:

            session_id (int,str): USSD session id for lookup in Session Cache
            service_code (str): USSD call code
            phone_number (str): phonenumber initiating USSD session

            input (str): last text sent over session
    """

    __metaclass__ = abc.ABCMeta

    session_id = utils.abstract_attribute()
    service_code = utils.abstract_attribute()
    phone_number = utils.abstract_attribute()
    commands = utils.abstract_attribute()
    input = utils.abstract_attribute()

    @abc.abstractmethod
    def __init__(self,http_post):
        """ Create a USSD ojbect from HTTTP Post request

            Arguments:

                http_post (dict): map of HTTP Post variables
        """
        pass

    def set_commands_and_input(self):
        """ Split text on * and set input to last command """
        self.commands = self.text.split('*')
        if self.commands == ['']:
            self.commands = []
            self.input = ''
        else:
            self.input = self.commands[-1]

    def send(self,text,has_next=False):
        """ Send USSD screen text to transport """
        return text

    def __len__(self):
        return len(self.commands)

    def __str__(self):
        return "{0.service_code} on {0.phone_number} id {0.session_id}".format(self)

class TextTransportUssd(UssdHttpBase):

    def __init__(self,**kwargs):

        self.session_id = kwargs.get('session_id','tmp_000')
        self.service_code = kwargs.get('service_code','1234')
        self.phone_number = kwargs.get('phone_number','1234')
        self.text = kwargs.get('text','')
        self.set_commands_and_input()
