from django.conf.urls import url
from . import views as lean_views

urlpatterns = [
    url(r'^$',lean_views.index, name='home'),
    url(r'^add/$',lean_views.add, name='add'),
    url(r'^add/(\d+)/(\d+)/?$',lean_views.add2,name='add2'),
    url(r'^desk/$', lean_views.fromdesktop),
    url(r'^config/?$',lean_views.setconfig,name='config'),
]
