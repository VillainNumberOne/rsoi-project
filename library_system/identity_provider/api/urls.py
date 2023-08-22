from django.urls import re_path
from api import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^api/v1/signup$', views.signup),
    re_path(r'^api/v1/login$', views.login),
    re_path(r'^api/v1/validate$', views.validate_id_token),
    re_path(r'^api/v1/refresh$', views.refresh),
    re_path(r'^api/v1/.well-known/jwks.json$', views.get_jwks),
    re_path('^signin/', views.signin_page, name='signin'),
    re_path('^signup/', views.signup_page, name='signup'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)