import datetime
import collections

# Local Imports
import screens

class Session(object):

    def __init__(self,start_screen,session_id,phone_number,service_code=""):
        self.history = [ResultNode(start_screen,"")]
        self.session_id = session_id
        self.phone_number = phone_number
        self.service_code = service_code

        self.vars = {}
        self.created = datetime.datetime.now()

    @property
    def current_screen(self):
        return self.history[-1].next_screen

    @property
    def last(self):
        return self.history[-1].input

    @property
    def has_next(self):
        return self.current_screen.has_next(self)

    def render(self,context=None):
        """ Pass through to current screen render function """
        return self.current_screen.render(session=self,context=context)

    def input(self,input,context=None):
        """ Send input to current screen and create new history node """
        next_screen = self.current_screen.input(input,session=self,context=context)
        self.history.append( ResultNode(next_screen,input) )
        return next_screen

    @property
    def commands(self):
        return ( node.input for node in self.history )

    @property
    def text(self):
        return '*'.join(self.commands)

    def __getitem__(self,key):
        try:
            return self.vars[key]
        except KeyError as e:
            return None

    def __setitem__(self,key,value):
        self.vars[key] = value

    def __delitem__(self,key):
        try:
            del self.vars[key]
        except KeyError as e:
            pass

    def __contains__(self,item):
        return item in self.vars

    def __len__(self):
        return len(self.history) - 1

    def __str__(self):
        return "<Session: {0.phone_number} on {0.service_code} ({1})>".format(self,len(self))

ResultNode = collections.namedtuple('ResultNode',['next_screen','input'])

class SessionCache(dict):

    def create_session(self,ussd,start_screen):
        if ussd.session_id in self:
            return self[ussd.session_id]
        new_session = Session(start_screen,ussd.session_id,ussd.phone_number,ussd.service_code)

        # Add any initial commands to the session
        if ussd.input != '':
            new_session.render() #fake inital render
            if len(ussd) > 1:
                for input in ussd.commands[0:-1]:
                    new_session.input(input)
                    new_session.render()
                    if not new_session.has_next:
                        break
            if new_session.has_next:
                # Run last input with no render if no break
                new_session.input(ussd.input)

        self[ussd.session_id] = new_session
        return new_session
