from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from interface.utils import send_message

def index(request):
    return render(request, 'frontend/index.html')

def profile(request):
    return render(request, 'frontend/profile.html')

def admin_profile(request):
    return render(request, 'frontend/admin_profile.html')

def libraries(request, city=None):
    return render(request, 'frontend/libraries.html')

def books(request, library_uid=None, library_name=None):
    return render(request, 'frontend/books.html')

def stats(request, library_uid=None, library_name=None):
    return render(request, 'frontend/stats.html')

@csrf_exempt
def authorize(request):
    if request.method == 'POST':
        id_token = request.POST.get('id_token', None)
        refresh_token = request.POST.get('refresh_token', None)
        username = request.POST.get('username', None)

        if id_token and refresh_token and username:
            try:
                response = HttpResponseRedirect('/profile/')
                response.set_cookie('id_token', id_token, path='/')
                response.set_cookie('refresh_token', refresh_token, path='/')
                send_message(username, f"{username} signed in")
                return response
            except ValueError:
                return HttpResponseRedirect('/')

    return HttpResponseRedirect('/')