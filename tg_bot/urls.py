from django.urls import path
from . import views

urlpatterns = [
    path('flights/', views.flight_list, name='flight-list'),
    path('search/', views.save_search, name='save-search'),
]
