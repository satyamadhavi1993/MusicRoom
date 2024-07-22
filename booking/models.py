from datetime import date, datetime, time, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Room(models.Model):
    date = models.DateField(timezone.now().date())
    time = models.TimeField(timezone.now().time())
    available_solo_rooms = models.IntegerField(default=30)
    available_duet_rooms = models.IntegerField(default=20)
    available_band_rooms = models.IntegerField(default=10)
    
    def __str__(self) -> str:
        return f'{self.date} - {self.time}'


class Reservation(models.Model):
    DEFAULT_ROOM_TYPE = 'Solo'
    ROOM_TYPES = {
    DEFAULT_ROOM_TYPE: 'Solo',
    'RoomType2': 'Duet',
    'RoomType3': 'Band'
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default=DEFAULT_ROOM_TYPE)
    
    def __str__(self):
        return f"{self.room.date} {self.room.time} - {self.room} - {self.room_type}"
