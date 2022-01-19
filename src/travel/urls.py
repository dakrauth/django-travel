from django.urls import path, include
from vanilla import TemplateView

from . import views
from .api.urls import urlpatterns as api_urls


item_patterns = [
    path('', views.LocaleView.as_view(), name='by-locale'),
    path('<str:code>/', views.EntityView.as_view(), name='entity'),
    path(
        '<str:code>/<str:rel>/',
        views.EntityRelationshipsView.as_view(),
        name='entity-relationships'
    ),
]

profile_patterns = [
    path('', views.AllProfilesView.as_view(), name='profiles'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path(
        '<str:username>/calendar/',
        views.CalendarView.as_view(),
        name='calendar'
    ),
    path(
        '<str:username>/log/<int:pk>/',
        views.LogEntryView.as_view(),
        name='log-entry'
    ),
]

bucket_list_patterns = [
    path('', views.BucketListsView.as_view(), name='buckets'),
    path('<int:pk>/', views.BucketListView.as_view(), name='bucket'),
    path('<int:pk>/<str:username>/', views.BucketListView.as_view(), name='bucket'),
    path(
        '<int:pk>/<path:usernames>/',
        views.BucketListComparisonView.as_view(),
        name='bucket-comparison'
    ),
]

app_name = 'travel'

urlpatterns = [
    path('api/v1/', include(api_urls)),
    path('search', views.SearchView.as_view(), name='search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='search-advanced'),
    path('i/<str:ref>/', include(item_patterns)),
    path('profiles/', include(profile_patterns)),
    path('buckets/', include(bucket_list_patterns)),
    path('languages/', views.LanguagesView.as_view(), name='languages'),
    path('languages/<int:pk>/', views.LanguageView.as_view(), name='language'),
    path('flags/', views.FlagGameView.as_view(), name='flag-quiz'),
    path(
        'plugs/',
        TemplateView.as_view(template_name='travel/plugs.html'),
        name='plugs'
    ),
]
