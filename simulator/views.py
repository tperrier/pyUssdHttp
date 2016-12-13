from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests, json, code

class IndexView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        # do something
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get(self,request):
        return render(request,'index.html')

    def post(self,request):
        data = json.loads(request.body)
        url = data.get('url')
        payload = {
            'sessionId':data.get('sessionId',''),
            'serviceCode':data.get('serviceCode',''),
            'phoneNumber':data.get('phoneNumber',''),
            'text':data.get('text','')
        }
        action , text = post_at_ussd(url,payload)
        return HttpResponse(json.dumps({'action':action,'text':text}))

########################################
# Utility Functions
########################################

def post_at_ussd(url,payload):
    ''' Use requests library to make a post request to an Africa's Talking USSD Gateway
        - return: action (con , end) , text
    '''
    response = requests.post(url,data=payload)
    action = response.text[:3]
    text = response.text[4:]
    return action , text
