from django.contrib import admin

# Register your models here.
from .models import Reservation, Room

admin.site.register(Room)
admin.site.register(Reservation)