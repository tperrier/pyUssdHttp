from importlib import import_module
from django.conf import settings

import datetime
import collections

# Local Imports
from . import screens

back_key = '99'

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
        """ Send input to current screen and create new history node
            If the input is equal to the back key, instead go to the
            previous history node"""
        if input == back_key and len(self.history) > 1:
            del self.history[-1]

            return self.history[-1].next_screen

        else:
            next_screen = self.current_screen.input(input,session=self,context=context)
            self.history.append( ResultNode(next_screen,input) )
            return next_screen

    def input_all(self,commands,context=None,pos=None):
        """ Run all new commands from the ussd object
            commands (str, or str_list) : command or list of commands to input
            context : dictionary context object to render response with
            pos (int or None) : position to start commands from. None = len(self)
        """
        if isinstance(commands,basestring):
            commands = commands.split('*')
            if commands == ['']:
                commands = []
        window_index = len(self) if pos is None else pos
        command_window = commands[window_index:]
        if 1 < len(command_window):
            for input in command_window[:-1]:
                self.input(input,context)
                self.render()
                if not self.has_next:
                    break
        if 0 < len(command_window) and self.has_next:
            # Run last input with no render if no break or if len(ussd) == 1
            self.input(command_window[-1])

    def delete(self):
        store = self.get_store()
        store.delete()

    def save(self):
        store = self.get_store()
        store['ussd'] = self
        store.save()

    def get_store(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore(self.session_id)
        return store

    @property
    def commands(self):
        return [ node.input for node in self.history ]

    @property
    def text(self):
        return '*'.join(self.commands[1:])

    @property
    def age(self):
        td = datetime.datetime.now() - self.created
        hours , min_seconds = divmod(td.seconds,3600)
        min , seconds = divmod(min_seconds,60)
        return "{}d {}h {}m".format(td.days,hours,min)

    def __getitem__(self,key):
        try:
            return self.vars[key]
        except KeyError as e:
            try:
                return getattr(self,key)
            except AttributeError as e:
                return None

    def get(self,key,default=None):
        return self.vars.get(key,default)

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
        return "<Session: {0.phone_number} on {0.service_code} ({1}) - {2}>".format(self,len(self),self.age)

ResultNode = collections.namedtuple('ResultNode',['next_screen','input'])
