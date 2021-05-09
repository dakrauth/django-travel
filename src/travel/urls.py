from django.urls import re_path, include
from django.views.generic import TemplateView, RedirectView
from . import views
from .api.urls import urlpatterns as api_urls


search_patterns = [
    re_path(r'^$', views.search, name='travel-search'),
    re_path(r'^advanced/$', views.search_advanced, name='travel-search-advanced'),
]

item_patterns = [
    re_path(r'^$', views.by_locale, name='travel-by-locale'),
    re_path(r'^(?P<code>\w+)(?:-(?P<aux>\w+))?/$', views.entity, name='travel-entity'),
    re_path(r'^(?P<code>\w+)(?:-(?P<aux>\w+))?/(?P<rel>\w+)/$', views.entity_relationships, name='travel-entity-relationships'),
]

add_patterns = [
    re_path(r'^$', views.start_add_entity, name='travel-entity-start-add'),
    re_path(r'^co/$', views.add_entity_co, name='travel-entity-add-co'),
    re_path(r'^co/(\w+)/(\w+)/$', views.add_entity_by_co, name='travel-entity-add-by-co'),
]

profile_patterns = [
    re_path(r'^$', views.all_profiles, name='travel-profiles'),
    re_path(r'^([^/]+)/$', views.profile, name='travel-profile'),
    re_path(r'^([^/]+)/calendar/$', views.calendar, name='travel-calendar'),
    re_path(r'^([^/]+)/log/(\d+)/$', views.log_entry, name='travel-log-entry'),
]

bucket_list_patterns = [
    re_path(r'^$', views.bucket_lists, name='travel-buckets'),
    re_path(r'^(\d+)/$', views.bucket_list, name='travel-bucket'),
    re_path(r'^(\d+)/([^/]+)/$', views.bucket_list_for_user, name='travel-bucket-for_user'),
    re_path(r'^(\d+)/(.+)/$', views.bucket_list_comparison, name='travel-bucket-comparison'),
]

language_patterns = [
    re_path(r'^$', views.languages, name='travel-languages'),
    re_path(r'^(\d+)/$', views.language, name='travel-language'),
]

urlpatterns = [
    re_path(r'^api/v1/', include(api_urls)),
    re_path(r'^search/', include(search_patterns)),
    re_path(r'^i/(?P<ref>\w+)/', include(item_patterns)),
    re_path(r'^add/', include(add_patterns)),
    re_path(r'^profiles/', include(profile_patterns)),
    re_path(r'^buckets/', include(bucket_list_patterns)),
    re_path(r'^languages/', include(language_patterns)),
    re_path(r'^flags/$', views.flag_game, name='travel-flag-quiz'),
    re_path(
        r'^plugs/$',
        TemplateView.as_view(template_name='travel/plugs.html'),
        name='travel-plugs'
    ),
    re_path(
        r'^edit/i/(\w+)/(\w+)(?:-(\w+))?/$',
        views.entity_edit,
        name='travel-entity-edit'
    ),
]
