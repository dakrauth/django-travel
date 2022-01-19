from django.urls import path, include
from vanilla  import TemplateView

from . import views
from .api.urls import urlpatterns as api_urls


item_patterns = [
    path('', views.LocaleView.as_view(), name='travel-by-locale'),
    path('<str:code>/', views.EntityView.as_view(), name='travel-entity'),
    path(
        '<str:code>/<str:rel>/',
        views.EntityRelationshipsView.as_view(),
        name='travel-entity-relationships'
    ),
]

profile_patterns = [
    path('', views.AllProfilesView.as_view(), name='travel-profiles'),
    path('<str:username>/', views.ProfileView.as_view(), name='travel-profile'),
    path(
        '<str:username>/calendar/',
        views.CalendarView.as_view(),
        name='travel-calendar'
    ),
    path(
        '<str:username>/log/<int:pk>/',
        views.LogEntryView.as_view(),
        name='travel-log-entry'
    ),
]

bucket_list_patterns = [
    path('', views.BucketListsView.as_view(), name='travel-buckets'),
    path('<int:pk>/', views.BucketListView.as_view(), name='travel-bucket'),
    path('<int:pk>/<str:username>/', views.BucketListView.as_view(), name='travel-bucket'),
    path(
        '<int:pk>/<path:usernames>/',
        views.BucketListComparisonView.as_view(),
        name='travel-bucket-comparison'
    ),
]


urlpatterns = [
    path('api/v1/', include(api_urls)),
    path('search', views.SearchView.as_view(), name='travel-search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='travel-search-advanced'),
    path('i/<str:ref>/', include(item_patterns)),
    path('profiles/', include(profile_patterns)),
    path('buckets/', include(bucket_list_patterns)),
    path('languages/', views.LanguagesView.as_view(), name='travel-languages'),
    path('languages/<int:pk>/', views.LanguageView.as_view(), name='travel-language'),
    path('flags/', views.FlagGameView.as_view(), name='travel-flag-quiz'),
    path(
        'plugs/',
        TemplateView.as_view(template_name='travel/plugs.html'),
        name='travel-plugs'
    ),
]
