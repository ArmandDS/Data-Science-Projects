from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.main, name='index'),
	url(r'get_decada/$', views.get_decada, name='get_decada'),
	url(r'codigo$', views.codigo, name='codigo'),
    url(r'proceso$', views.proceso, name='proceso')
]