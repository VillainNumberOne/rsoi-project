from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from django.shortcuts import render, redirect

from api.utils import (
    custom_authenticate, 
    create_new_user,
    build_jwk,
    generate_id_token,
    generate_refresh_token,
    validate_jwt_signature
)
import json
import re

USERNAME_REGEX = r'^[a-zA-Z0-9_]+$'

def signup_page(request):
    return render(request, "identity_provider/signup.html")

def signin_page(request):
    return render(request, "identity_provider/signin.html")

@csrf_exempt
def signup(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username', None)
        password = body.get('password', None)

        if username is None or password is None:
            return JsonResponse({'error': 'Invalid input'}, status=400)
        
        if not re.match(USERNAME_REGEX, username):
            return JsonResponse({'error': 'Invalid username format'}, status=400)

        new_user = create_new_user(username, password)

        if new_user is None:
            return JsonResponse({'error': 'Username already exists'}, status=409)
        else:
            id_token = generate_id_token(new_user)
            refresh_token = generate_refresh_token(new_user)

            tokens = {
                'id_token': id_token,
                'refresh_token': refresh_token
            }

            return JsonResponse(tokens, status=201)

    return JsonResponse({'error': 'Bad request'}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username', None)
        password = body.get('password', None)

        if username is None or password is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        user = custom_authenticate(username, password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        id_token = generate_id_token(user)
        refresh_token = generate_refresh_token(user)

        tokens = {
            'id_token': id_token,
            'refresh_token': refresh_token
        }

        return JsonResponse(tokens, status=200)

    return JsonResponse({'error': 'Bad request'}, status=400)

@csrf_exempt
def refresh(request):
    if request.method == "POST":
        return HttpResponse(status=status.HTTP_200_OK)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST) 

@csrf_exempt
def get_jwks(request):
    if request.method == "GET":
        jwk = build_jwk()
        jwks = {
            "keys": [jwk]
        }

        return JsonResponse(jwks, status=200)

    return JsonResponse({'error': 'Bad request'}, status=400)

@csrf_exempt
def validate_id_token(request):
    if request.method == "POST":
        body = json.loads(request.body)
        id_token = body.get('id_token', None)

        try:
            jwt_payload = validate_jwt_signature(id_token)
            return JsonResponse({'payload': jwt_payload}, status=200)
        except ValueError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Invalid ID token'}, status=401)

    return JsonResponse({'error': 'Bad request'}, status=400)

