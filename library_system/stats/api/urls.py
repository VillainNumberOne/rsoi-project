from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^api/v1/stats$', views.stats_api),
    re_path(r'^api/v1/stats/$', views.stats_api)
]