from datetime import date, datetime, time, timedelta

from django.db import models
from django.utils import timezone

# Create your models here.
class Room(models.Model):
    date = models.DateField(timezone.now().date())
    time = models.TimeField(timezone.now().time())
    available_single_rooms = models.IntegerField(default=10)
    available_double_rooms = models.IntegerField(default=10)
    available_family_rooms = models.IntegerField(default=10)
    
    def __str__(self) -> str:
        return f'{self.date} - {self.time}'


class Reservation(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(timezone.now().date())
    time = models.TimeField(timezone.now().time())
    
    def __str__(self):
        return f"{self.date} {self.time} - {self.room}"
