from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests, json, code

@method_decorator(csrf_exempt,name='dispatch')
class AfricasTalkingView(View):


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

@method_decorator(csrf_exempt,name='dispatch')
class NiafikraView(View):


    def get(self,request):
        return render(request,'index.html')

    def post(self,request):
        data = json.loads(request.body)
        url = data.get('url')
        payload = {
            'sessionid':data.get('sessionId',''),
            'msisdn':data.get('phoneNumber',''),
            'input':data.get('text','')
        }
        action , text = post_nf_ussd(url,payload)
        return HttpResponse(json.dumps({'action':action,'text':text}))

########################################
# Utility Functions
########################################

def post_nf_ussd(url,payload):
    ''' Use requests library to make a post request to an Niafikra USSD Gateway
        - return: action (con , end) , text
    '''
    response = requests.get(url,params=payload)
    action = 'con' if response.headers.get('Session','Q') == 'C' else 'end'
    text = response.text
    return action , text


def post_at_ussd(url,payload):
    ''' Use requests library to make a post request to an Africa's Talking USSD Gateway
        - return: action (con , end) , text
    '''
    response = requests.post(url,data=payload)
    action = response.text[:3]
    text = response.text[4:]
    return action , text
