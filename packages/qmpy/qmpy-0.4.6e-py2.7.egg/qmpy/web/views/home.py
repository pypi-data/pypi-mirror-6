import os.path

from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from django.template import RequestContext
from qmpy.models import Entry, Task, Calculation

def home_page(request):
    static = Calculation.objects.filter(label='static', converged=True)
    standard = Calculation.objects.filter(label='standard', converged=True)
    data = {'done':Entry.objects.filter(calculation__in=(static | standard)),
            'entries':Entry.objects.filter(duplicate_of=None),
            'running':Task.objects.filter(state=1),
            'recent':Calculation.objects.filter(label='static',
                converged=True).order_by('-id')[:5],
            'jobserver':os.path.exists('/tmp/jobserver.pid'),
            'taskserver':os.path.exists('/tmp/taskserver.pid')}
    request.session.set_test_cookie()

    return render_to_response('index.html',
            data,
            RequestContext(request))

def construction_page(request):
    return render_to_response('construction.html',
            {},
            RequestContext(request))

def faq_view(request):
    return render_to_response('faq.html')

def play_view(request):
    return render_to_response('play.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                pass
        else:
            pass

def logout(request):
    logout(request)
    # redirect to success
