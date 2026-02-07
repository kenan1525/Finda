from django.urls import path
from .views import flight_search

urlpatterns = [
    # This file is included under project urls at path 'fly/',
    # so use empty string here so final route becomes '/fly/'.
    path("", flight_search, name="flight_search"),
]
