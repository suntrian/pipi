# coding:utf-8
from django.shortcuts import render

# Create your views here.
from datetime import datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import Config
from . import requestsubserver


def index(request):
    # return HttpResponse(u'hello django')
    a = request.GET.get('a', 0)
    b = request.GET.get('b', 1)
    return render(request, 'home.html', {'a': a, 'b': b})


def add(request):
    a = request.GET['a']
    b = request.GET['b']
    c = int(a) + int(b)
    return HttpResponse(str(c))


def add2(request, a, b):
    c = int(a) + int(b)
    return HttpResponse(str(c))


def setconfig(request):
    if request.method == 'POST':
        request.GET = request.POST
    key = request.GET.get('k', request.GET.get('key', ''))
    value = request.GET.get('v', request.GET.get('value', ''))
    comment = request.GET.get('c', request.GET.get('comment', ''))
    if key == '':
        return HttpResponse('hello ya')
    else:
        try:
            conf = Config.objects.get(key=key)
            if conf.value != value and value != '':
                conf.value = value
            if conf.comment != comment and comment != '':
                conf.comment = comment
            conf.moditime = datetime.now()
            conf.save()
            return JsonResponse(model_to_dict(conf))
        except:
            if value != '':
                conf = Config(key=key, value=value)
                if comment != '':
                    conf.comment = comment
                conf.moditime = datetime.now()
                conf.save()
            return JsonResponse(model_to_dict(conf))


def fromdesktop(request):
    if request.method == 'POST':
        request.GET = request.POST

    config = request.GET
    forwarder = requestsubserver.reqforward()
    d = forwarder.forward(config)

    return HttpResponse(d)
