from django.urls import path
from . import views

urlpatterns = [
    path('flights/', views.flight_list, name='flight-list'),
    path('search-history/', views.search_history, name='searchhistory-list'),
    path('save-search/', views.save_search, name='save-search'),
]