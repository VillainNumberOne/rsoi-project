from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'frontend/index.html')

def profile(request):
    return render(request, 'frontend/profile.html')

def libraries(request, city=None):
    return render(request, 'frontend/libraries.html')

def books(request, library_uid=None, library_name=None):
    return render(request, 'frontend/books.html')

@csrf_exempt
def authorize(request):
    if request.method == 'POST':
        id_token = request.POST.get('id_token', None)
        refresh_token = request.POST.get('refresh_token', None)

        if id_token and refresh_token:
            response = HttpResponseRedirect('/profile/')
            response.set_cookie('id_token', id_token, path='/')
            response.set_cookie('refresh_token', refresh_token, path='/')
            return response

    return HttpResponseRedirect('/')