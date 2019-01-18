from django.conf.urls import *
from . import views

urlpatterns = [
    url('^logs/([-\w]+)/$', views.log_list),
]
