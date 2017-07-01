from importlib import import_module
from django.conf import settings

import abc

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .. import transports
from .. import sessions
from .. import utils

class AfricasTalkingDjango(transports.AfricasTalkingUssd):

    def response(self,prefix,text):
        return HttpResponse( super(AfricasTalkingDjango,self).response(prefix,text) )

    @classmethod
    def from_request(cls,request):
        return cls(
            session_id = request.POST.get('sessionId'),
            service_code = request.POST.get('serviceCode'),
            phone_number = request.POST.get('phoneNumber'),
            text = request.POST.get('text','')
        )

class NiafikraDjango(transports.NiafikraUssd):

    def send(self,text,has_next=False):
        """ Create an HttpResponse and add the C or Q Session header """
        response = HttpResponse( text )
        if has_next is True:
            response['Session'] = 'C'
        else:
            response['Session'] = 'Q'
        return response

    @classmethod
    def from_request(cls,request):
        text = request.GET.get('input','')
        if text.startswith(settings.NIAFIKRA_SERVICE_CODE):
            # First time creating this session
            text = text[len(settings.NIAFIKRA_SERVICE_CODE):].lstrip('*')
        return cls(
            session_id = request.GET.get('sessionid'),
            service_code = settings.NIAFIKRA_SERVICE_CODE,
            phone_number = request.GET.get('msisdn'),
            text = text
        )

@method_decorator(csrf_exempt,name='dispatch')
class DjangoDriver(View):
    """ Demo USSD Django Driver """

    __metaclass__ = abc.ABCMeta

    start_app = utils.abstract_attribute()
    transport = "AfricasTalking"

    def __init__(self, **kwargs):
        super(DjangoDriver,self).__init__(**kwargs)

        self.transport_class = get_transport_class(self.transport)

    def post(self,request):
        ussd = self.transport_class.from_request(request)

        # Get session from session cache Sessions.get_session(request,ussd)
        session = get_or_set_session(ussd, self.start_app)
        session.input_all(ussd.commands)

        result = ussd.send( session.render() , session.has_next)
        if session.has_next is False:
            # Remove from session cache
            session.delete()
        else:
            session.save()
        return result

    def get(self,request):
        return self.post(request)

def get_transport_class(name):
    return globals().get("{}Django".format(name), AfricasTalkingDjango )

def get_or_set_session(ussd,start_screen):
    """ Factory method to get or set session in SESSION_ENGINE """

    print ussd
    engine = import_module(settings.SESSION_ENGINE)
    store = engine.SessionStore(session_key=ussd.session_id)
    if not store.exists(session_key=ussd.session_id):
        print 'Not Found',store.session_key , ussd.session_id
        store.save(must_create=True)
        # Create a new session
        store['ussd'] = sessions.Session(start_screen,ussd.session_id,ussd.phone_number,ussd.service_code)
        print store['ussd']
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
