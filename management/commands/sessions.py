from importlib import import_module

# Django Imports
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'List and manage ussd django db sessions'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(help='session commands')

        list_parser = subparsers.add_parser('list', cmd=parser.cmd, help='list ussd sessions')
        list_parser.set_defaults(action='list_sessions')

        clear_parser = subparsers.add_parser('clear', cmd=parser.cmd, help='delete ussd sessions')
        clear_parser.set_defaults(action='clear_sessions')

    def handle(self, *args, **options):

        self.options = options
        getattr(self, options['action'])()

    def list_sessions(self):
        from django.contrib.sessions.models import Session
        engine = import_module(settings.SESSION_ENGINE)
        sessions = []
        for session in Session.objects.all():
            store = engine.SessionStore(session.session_key)
            try:
                sessions.append( store['ussd'] )
            except KeyError as e:
                pass

        self.stdout.write( "Found {} Sessions\n".format(len(sessions)) )

        for session in sessions:
            self.stdout.write( "  {0.session_id} {0}\n".format(session) )

    def clear_sessions(self):
        from django.contrib.sessions.models import Session
        engine = import_module(settings.SESSION_ENGINE)

        count = 0
        for session in Session.objects.all():
            store = engine.SessionStore(session.session_key)
            if store.get('ussd') is not None:
                store.delete()
                count += 1

        self.stdout.write( "Deleted {} Sessions\n".format(count) )
