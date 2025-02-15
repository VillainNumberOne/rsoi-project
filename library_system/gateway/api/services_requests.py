import requests
import json
from datetime import datetime

LIBRARY_SYSTEM = "http://librarysystem:8060"
RATING_SYSTEM = "http://ratingsystem:8050"
RESERVATION_SYSTEM = "http://reservationsystem:8070"
STATISTICS_SYSTEM = "http://stats:8020"


def get_city_libraries(city, page=None, size=None):
    data = {"city": city, "page": page, "size": size}
    response = requests.get(
        f"{LIBRARY_SYSTEM}/api/v1/libraries", data=json.dumps(data)
    ).text
    return json.loads(response)

def get_statistics():
    response = requests.get(
        f"{STATISTICS_SYSTEM}/api/v1/stats"
    ).text
    return json.loads(response)

def get_library_books(library_uid, page=None, size=None, show_all=None):
    data = {
        "library_uid": library_uid,
        "page": page,
        "size": size,
        "show_all": show_all,
    }
    response = requests.get(
        f"{LIBRARY_SYSTEM}/api/v1/librarybooks", data=json.dumps(data)
    ).text
    return json.loads(response)


def create_rating(username, stars):
    data = {
        "username": username,
        "stars": stars,
    }
    response_status = requests.post(
        f"{RATING_SYSTEM}/api/v1/ratings", data=json.dumps(data)
    ).status_code
    return response_status


def get_user_reservations(username):
    reservations = json.loads(
        requests.get(f"{RESERVATION_SYSTEM}/api/v1/reservations/{username}").text
    )
    libraries_list = [reservation["library_uid"] for reservation in reservations]
    books_list = [reservation["book_uid"] for reservation in reservations]

    libraryes_info_data = {"libraries_list": libraries_list}
    books_info_data = {"books_list": books_list}

    libraries_info = json.loads(
        requests.get(
            f"{LIBRARY_SYSTEM}/api/v1/libraries/info",
            data=json.dumps(libraryes_info_data),
        ).text
    )
    books_info = json.loads(
        requests.get(
            f"{LIBRARY_SYSTEM}/api/v1/books/info", data=json.dumps(books_info_data)
        ).text
    )

    libraries = {
        library_uid: {
            "libraryUid": library_uid,
            "name": library_info["name"],
            "address": library_info["address"],
            "city": library_info["city"],
        }
        for library_uid, library_info in libraries_info.items()
    }

    books = {
        book_uid: {
            "bookUid": book_uid,
            "name": book_info["name"],
            "author": book_info["author"],
            "genre": book_info["genre"],
        }
        for book_uid, book_info in books_info.items()
    }

    result = [
        {
            "reservationUid": reservation["reservation_uid"],
            "status": reservation["status"],
            "startDate": reservation["start_date"],
            "tillDate": reservation["till_date"],
            "book": books[reservation["book_uid"]],
            "library": libraries[reservation["library_uid"]],
        }
        for reservation in reservations
    ]

    return result

def get_user_rating(username):
    response = requests.get(f"{RATING_SYSTEM}/api/v1/ratings/{username}")
    if response.status_code != 200:
        return None, response.status_code
    else:
        user_stars = json.loads(response.text)
        return user_stars, None

def make_reservation(username, book_uid, library_uid, till_date):
    # CHECKS ##################################
    try:
        till_date = datetime.strptime(till_date, "%Y-%m-%d")
    except Exception as ex:
        return None, str(ex)
    start_date = datetime.today()  # .strftime('%Y-%m-%d')
    # print(start_date, till_date)
    # if till_date <= start_date:
    #     return None, "Wrong tillDate"

    available_count_data = {"library_uid": library_uid, "book_uid": book_uid}
    available_count = json.loads(
        requests.get(
            f"{LIBRARY_SYSTEM}/api/v1/books/available",
            data=json.dumps(available_count_data),
        ).text
    )
    if not (available_count != 0):
        return None, "Not available"

    user_rented = json.loads(
        requests.get(f"{RESERVATION_SYSTEM}/api/v1/reservations/{username}/rented").text
    )
    user_stars = json.loads(
        requests.get(f"{RATING_SYSTEM}/api/v1/ratings/{username}").text
    )

    if user_stars - user_rented <= 0:
        return None, "Insufficient rating"

    # SAFE PREPARE #############################

    libraryes_info_data = {"libraries_list": [library_uid]}
    books_info_data = {"books_list": [book_uid]}

    libraries_info = json.loads(
        requests.get(
            f"{LIBRARY_SYSTEM}/api/v1/libraries/info",
            data=json.dumps(libraryes_info_data),
        ).text
    )
    books_info = json.loads(
        requests.get(
            f"{LIBRARY_SYSTEM}/api/v1/books/info", data=json.dumps(books_info_data)
        ).text
    )

    # RESERVATION ##############################
    reservation_data = {
        "username": username,
        "book_uid": book_uid,
        "library_uid": library_uid,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "till_date": till_date.strftime("%Y-%m-%d"),
    }

    available_count_data = {"book_uid": book_uid, "library_uid": library_uid, "mode": 0}
    status_code = requests.post(
        f"{LIBRARY_SYSTEM}/api/v1/books/available",
        data=json.dumps(available_count_data),
    ).status_code
    if status_code != 202:
        return None, "Not available"

    reservation_response = requests.post(
        f"{RESERVATION_SYSTEM}/api/v1/reservation", data=json.dumps(reservation_data)
    )
    if reservation_response.status_code != 201:
        return None, "Not available"

    reservation = json.loads(reservation_response.text)

    # RESULT ###################################

    libraries = {
        library_uid: {
            "libraryUid": library_uid,
            "name": library_info["name"],
            "address": library_info["address"],
            "city": library_info["city"],
        }
        for library_uid, library_info in libraries_info.items()
    }

    books = {
        book_uid: {
            "bookUid": book_uid,
            "name": book_info["name"],
            "author": book_info["author"],
            "genre": book_info["genre"],
        }
        for book_uid, book_info in books_info.items()
    }

    result = {
        **reservation,
        "book": books[book_uid],
        "library": libraries[library_uid],
        "rating": {"stars": user_stars},
    }

    return result, None


def return_book(username, reservation_uid, condition, date):
    # При возврате книги в Rented System изменяется статус на:
    #   EXPIRED если дата возврата больше till_date в записи о резерве;
    #   RETURNED если книгу сдали в срок.
    return_data = {
        "username": username,
        "reservation_uid": reservation_uid,
        "date": date,
    }
    return_response = requests.patch(
        f"{RESERVATION_SYSTEM}/api/v1/reservation",
        data=json.dumps(return_data),
    )
    if return_response.status_code == 404:
        return None, 404
    if return_response.status_code != 202:
        return None, "Not available"

    reservation_info = json.loads(return_response.text)
    book_uid = reservation_info['book_uid']
    library_uid = reservation_info['library_uid']
    status = reservation_info['status']

    # Выполняется запрос в Library Service для увеличения счетчика доступных книг (поле available_count).
    available_count_data = {"book_uid": book_uid, "library_uid": library_uid, "mode": 1}
    status_code = requests.post(
        f"{LIBRARY_SYSTEM}/api/v1/books/available",
        data=json.dumps(available_count_data),
    ).status_code
    if status_code != 202:
        return None, "Unavailable to update available_count"
    
    # Update book condition
    update_condition_data = {
        "book_uid": book_uid,
        "condition": condition
    }
    update_condition_response = requests.patch(
        f"{LIBRARY_SYSTEM}/api/v1/books/return",
        data=json.dumps(update_condition_data),
    )
    if update_condition_response.status_code != 202:
        return None, "Unavailable to update book condition"
    
    conditions = json.loads(update_condition_response.text)

    stars = 0
    # Если книгу вернули позднее срока или ее состояние на момент выдачи (запись в Reservation System)
    # отличается от состояния, в котором ее вернули, то у пользователя уменьшается количество звезд на
    # 10 за каждое условие (сдача позднее срока и в плохом состоянии).
    if status == 'EXPIRED':
        stars -= 10

    condition_values = {
        "EXCELLENT": 0,
        "GOOD": 1,
        "BAD": 2 
    }
    if condition_values[conditions["new_condition"]] > condition_values[conditions["old_condition"]]:
        stars -= 10
    
    update_stars_data = {
        "mode": 1 if stars >= 0 else 0,
        "amount": abs(stars) if stars < 0 else 1
    }
    update_stars_response = requests.patch(
        f"{RATING_SYSTEM}/api/v1/ratings/{username}",
        data=json.dumps(update_stars_data),
    )
    if update_stars_response.status_code != 202:
        return None, "Unavailable to update user rating"

    return True, None
