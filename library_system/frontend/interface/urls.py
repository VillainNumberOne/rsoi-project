from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urls = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('libraries/', views.libraries, name='libraries'),
    re_path(r'^libraries/(?P<city>[\-a-zA-Zа-яА-ЯёЁ\s]+)$', views.libraries),
    path('authorize/', views.authorize),
    path('books/', views.books, name='books'),
    re_path(r'^books/(?P<library_uid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(&P<library_name>.+)$', views.books),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)