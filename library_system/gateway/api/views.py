from hashlib import new
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
import requests
import json

# from api.serializers import PersonSerializer
from api.messages import *

import api.services_requests
import api.utils.utils as utils
import api.errors as errors

@csrf_exempt
def test_auth(request):
    return JsonResponse({"result": utils.authorize_request(request)}, status=200)

@csrf_exempt
def statistics(request):
    if not utils.authorize_request(request, admin=True):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "GET":
        try:
            data = api.services_requests.get_statistics()
            return JsonResponse(data=data, status=status.HTTP_200_OK, safe=False)
        except Exception as ex:
            return JsonResponse(data={"error": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def libraries(request, library_uid=None):
    if not utils.authorize_request(request):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "GET":
        if library_uid is None:
            try:
                page = 1
                size = 1
                city = None
                if "size" in request.GET:
                    size = request.GET["size"]
                if "page" in request.GET:
                    page = request.GET["page"]
                if page is None or size is None:
                    page = None
                    size = None

                if "city" in request.GET:
                    city = request.GET["city"]
                    try:
                        libraries_data = api.services_requests.get_city_libraries(
                            city, page, size
                        )
                        return JsonResponse(
                            libraries_data, safe=False, status=status.HTTP_200_OK
                        )
                    except Exception as ex:
                        print(ex)
                        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                else:
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            except:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            page = 1
            size = 1
            show_all = True
            if "size" in request.GET:
                size = request.GET["size"]
            if "page" in request.GET:
                page = request.GET["page"]
            if "showAll" in request.GET:
                show_all = request.GET["showAll"]

            try:
                librarybooks = api.services_requests.get_library_books(
                    library_uid, page, size, show_all
                )
                return JsonResponse(librarybooks, safe=False, status=status.HTTP_200_OK)
            except Exception as ex:
                print(ex)
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def reservations(request):
    if not utils.authorize_request(request):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "GET":
        headers = utils.get_http_headers(request)
        if "X_USER_NAME" in headers.keys():
            username = headers["X_USER_NAME"]
            reservations = api.services_requests.get_user_reservations(username)
            return JsonResponse(reservations, safe=False, status=status.HTTP_200_OK)

    elif request.method == "POST":
        headers = utils.get_http_headers(request)
        if "X_USER_NAME" in headers.keys():
            username = headers["X_USER_NAME"]
        else:
            return JsonResponse(
                errors.reservations_no_username(), status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = JSONParser().parse(request)
            if all(k in data for k in ["bookUid", "libraryUid", "tillDate"]):
                book_uid = data["bookUid"]
                library_uid = data["libraryUid"]
                till_date = data["tillDate"]
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            result, error = api.services_requests.make_reservation(
                username, book_uid, library_uid, till_date
            )
        except Exception as ex:
            print(ex)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if result is not None:
            utils.send_message(username, f"{username} made a reservation, book uid: {book_uid}")
            return JsonResponse(result, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                errors.reservations_error(error),
                safe=False,
                status=status.HTTP_400_BAD_REQUEST,
            )

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def return_book(request, reservation_uid=None):
    if not utils.authorize_request(request):
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == "POST":
        if reservation_uid is None:
            HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        headers = utils.get_http_headers(request)
        if "X_USER_NAME" in headers.keys():
            username = headers["X_USER_NAME"]
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            data = JSONParser().parse(request)
            if all(k in data for k in ["condition", "date"]):
                condition = data["condition"]
                date = data["date"]
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            if condition not in ["BAD", "GOOD", "EXCELLENT"]:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            result, error = api.services_requests.return_book(
                username, reservation_uid, condition, date
            )
        except Exception as ex:
            print(ex)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if result:
            utils.send_message(username, f"{username} returned book with reservation uid: {reservation_uid}")
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        else:
            if error == 404:
                return JsonResponse(
                    errors.return_error("Not found"),
                    safe=False,
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                return JsonResponse(
                    errors.return_error(error),
                    safe=False,
                    status=status.HTTP_400_BAD_REQUEST,
                )

    HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def rating(request):
    if request.method == "GET":
        if not utils.authorize_request(request):
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    
        headers = utils.get_http_headers(request)
        if "X_USER_NAME" in headers.keys():
            username = headers["X_USER_NAME"]
            try:
                rating, error = api.services_requests.get_user_rating(username)
                if error:
                    if error == 404:
                        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
                else:
                    result = {"stars": rating}
                    return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

            except Exception as ex:
                print(ex)
                return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if request.method == "POST":
        jwt_payload = utils.authorize_request(request, admin=True) 
        if not jwt_payload:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        
        body = json.loads(request.body)
        username = body.get("username", None)
        stars = body.get("stars", 0)

        if username is not None:
            try:
                response_status = api.services_requests.create_rating(username, stars)
                if response_status == 201:
                    utils.send_message(
                        "Admin" + jwt_payload['username'], 
                        f"Admin {jwt_payload['username']} created a user with username: {username}, stars: {stars}"
                    )
                    return HttpResponse(status=status.HTTP_201_CREATED)
            except Exception as ex:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
