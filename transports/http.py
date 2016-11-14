
import abc
from UssdHttp import utils

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
    input = utils.abstract_attribute()

    @abc.abstractmethod
    def __init__(self,http_post):
        """ Create a USSD ojbect from HTTTP Post request

            Arguments:

                http_post (dict): map of HTTP Post variables
        """
        pass

    @abc.abstractmethod
    def send(self,text,has_next=False):
        """ Return text over an HTTP request to send back on the session

            Arguments:

                text (str): text to send
                has_next (bool): whether or not to keep the session open
        """
        pass
