from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("calendar/", views.calendar, name="calendar"),
    path("cancel_reservation/", views.cancel_reservation, name="cancel_reservation"),
    path("deactivate_account/", views.deactivate_account, name="deactivate_account"),
    path("", views.home, name="home"),
    path("my_profile/", views.my_profile, name="my_profile"),
    path("reservations/", views.reservations, name="reservations"),
    path("reserve/", views.reserve, name="reserve"),
]