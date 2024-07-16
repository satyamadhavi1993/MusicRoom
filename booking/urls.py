from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("reservations/", views.reservations, name="reservations"),
    path("calendar/", views.calendar, name="calendar"),
    path("reserve/", views.reserve, name="reserve"),
]