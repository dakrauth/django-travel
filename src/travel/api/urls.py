from django.conf.urls import *
from . import views

urlpatterns = [
    url('^logs/([-\w]+)/$', views.LogListView.as_view(), name='user_log_api'),
    url('^flag-game/$', views.FlagGameView.as_view(), name='flag_game_api'),
]
