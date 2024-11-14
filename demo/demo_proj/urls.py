from django.urls import re_path, include
from django.contrib.auth import urls as auth_urls
from django.contrib.auth import logout as auth_logout
from django import http
from django.contrib import admin
from django.views.generic import TemplateView


def logout(request):
    auth_logout(request)
    return http.HttpResponseRedirect("/")


urlpatterns = [
    re_path(r"^$", TemplateView.as_view(template_name="home.html"), name="home"),
    re_path(r"^account/logout/$", logout, name="demo-logout"),
    re_path(r"^account/", include(auth_urls)),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("travel.urls")),
]
