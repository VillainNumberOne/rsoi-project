from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from django.db import connection
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

import api.utils

@csrf_exempt
def stats_api(request):
    if request.method == "GET":
        start_timestamp = request.GET.get('start_timestamp', None)
        end_timestamp = request.GET.get('end_timestamp', None)

        try:
            with connection.cursor() as cursor:
                if start_timestamp:
                    start_datetime = timezone.datetime.strptime(start_timestamp, '%Y-%m-%d %H:%M:%S')
                else:
                    start_datetime = timezone.now() - timedelta(days=1)
                
                if end_timestamp:
                    end_datetime = timezone.datetime.strptime(end_timestamp, '%Y-%m-%d %H:%M:%S')
                else:
                    end_datetime = timezone.now()

                query = """
                    SELECT *
                    FROM stats
                    WHERE timestamp >= %s AND timestamp <= %s
                """
                cursor.execute(query, [start_datetime, end_datetime])
                rows = cursor.fetchall()
        except Exception:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        results = []
        for row in rows:
            entry = {
                'id': row[0],
                'topic': row[1],
                'message_value': row[2],
                'username': row[3],
                'key': row[4],
                'timestamp': row[5].strftime('%Y-%m-%d %H:%M:%S')
            }
            results.append(entry)

        return JsonResponse(results, safe=False, status=status.HTTP_200_OK)
    
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

