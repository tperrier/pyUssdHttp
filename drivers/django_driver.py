from importlib import import_module
from django.conf import settings

import abc

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import UssdHttp

class AfricasTalkingUssd(UssdHttp.AfricasTalkingUssd):

    def response(self,prefix,text):
        return HttpResponse(u'{0} {1}'.format(prefix,text))

@method_decorator(csrf_exempt,name='dispatch')
class Driver(View):
    """ Demo USSD Django Driver """

    __metaclass__ = abc.ABCMeta

    start_app = UssdHttp.utils.abstract_attribute()

    def post(self,request):
        at_ussd = AfricasTalkingUssd(request.POST)

        # Get session from session cache Sessions.get_session(request,ussd)
        session = get_or_set_session(at_ussd, self.start_app)
        session.input_all(at_ussd)
        print session.text
        print at_ussd.text

        result = at_ussd.send( session.render() , session.has_next)
        if session.has_next is False:
            # Remove from session cache
            session.delete()
        else:
            session.save()
        return result

def get_or_set_session(ussd,start_screen):
    """ Factory method to get or set session in SESSION_ENGINE """

    engine = import_module(settings.SESSION_ENGINE)
    store = engine.SessionStore(ussd.session_id)
    if not store.exists(ussd.session_id):
        print 'Not Found',store.session_key
        store.save(must_create=True)
        # Create a new session
        store['ussd'] = UssdHttp.Session(start_screen,ussd.session_id,ussd.phone_number,ussd.service_code)
        if ussd.input != '':
            store['ussd'].render() # Fake initial render
    else:
        print 'FOUND',store.session_key
        print store['ussd']
    return store['ussd']

def session_list_view(request):
        from django.contrib.sessions.models import Session
        engine = import_module(settings.SESSION_ENGINE)
        sessions = []
        for session in Session.objects.all():
            store = engine.SessionStore(session.session_key)
            try:
                sessions.append( store['ussd'] )
            except KeyError as e:
                pass
        return render(request,'driver/sessions.html',{'sessions':sessions})
