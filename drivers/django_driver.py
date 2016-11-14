import abc

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import UssdHttp

session_cache = UssdHttp.sessions.SessionCache()

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
        # session.screen.get_next(ussd.text,request)
        session = session_cache.get(at_ussd.session_id)
        if session is None:
            # if not in session start one with the new app and render first screen
            session = session_cache.create_session(at_ussd, self.start_app)
            return at_ussd.send( session.render() , session.has_next)
        else:
            session.input(at_ussd.input)
            if session.has_next is False:
                # Remove from session cache
                del session_cache[session.session_id]
            return at_ussd.send( session.render() , session.has_next )


def session_list_view(request):
        return render(request,'driver/sessions.html',{'sessions':session_cache})
