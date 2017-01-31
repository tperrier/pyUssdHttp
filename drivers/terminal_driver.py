#!/usr/bin/python
import sys

from ..transports.http import TextTransportUssd
from .. import sessions
from .. import utils

class TerminalDriver(object):
    """ Terminal Drive Using TextTransport """

    def __init__(self,start_app,stdout=None,session_id=None,service_code=None,phone_number=None,text='',**kwargs):

        self.stdout = stdout if stdout is not None else sys.stdout
        self.start_app = start_app

        # Clean TextTrasport Settings and create session
        kwargs = { 'session_id':session_id, 'service_code':service_code, 'phone_number':phone_number, 'text':text }
        for key , value in kwargs.items():
            if value is None:
                del kwargs[key]
        ussd = TextTransportUssd(**kwargs)
        self.session = sessions.Session(self.start_app,ussd.session_id,ussd.phone_number,ussd.service_code)
        if ussd.input != "":
            self.session.render() # Fake initial render if there are start commands
        self.input(ussd.commands)

    def input(self,commands):
        self.session.input_all(commands,pos=0)
        self.render()

    def render(self):

        self.stdout.write( self.session.render() )
        self.stdout.write( "\n" )

        if self.session.has_next:
            next_input = raw_input("Response: ")
            self.input(next_input)

class TestDriver(TerminalDriver):

    def input(self,commands):
        self.session.input_all(commands,pos=0)

    def render(self):

        self.stdout.write( self.session.render() )
