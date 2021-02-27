from django.urls import re_path
from . import views

urlpatterns = [
    re_path('^logs/([-\w]+)/$', views.LogListView.as_view(), name='user_log_api'),
    re_path('^flag-game/$', views.FlagGameView.as_view(), name='flag_game_api'),
]
