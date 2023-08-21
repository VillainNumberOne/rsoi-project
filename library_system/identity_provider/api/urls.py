from django.urls import re_path
from api import views

urlpatterns = [
    re_path(r'^api/v1/signup$', views.signup),
    re_path(r'^api/v1/login$', views.login),
    re_path(r'^api/v1/validate$', views.validate_id_token),
    re_path(r'^api/v1/refresh$', views.refresh),
    re_path(r'^api/v1/.well-known/jwks.json$', views.get_jwks),
]