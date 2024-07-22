from django.core.management.base import BaseCommand
from datetime import date, timedelta, datetime
from booking.models import Room
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the Room table with initial data'

    def handle(self, *args, **kwargs):
        slot_times = [datetime.strptime(f"{hour}:00", "%H:%M").time() for hour in range(8, 23)]
        start_date = date.today() + timedelta(days=1)
        days_until_sunday = (6 - start_date.weekday()) % 7
        end_date = start_date + timedelta(days=days_until_sunday)
        
        current_date = start_date
        while current_date <= end_date:
            for slot_time in slot_times:
                room = Room.objects.create(
                    date=current_date,
                    time=slot_time,
                    available_solo_rooms=30,
                    available_duet_rooms=20,
                    available_band_rooms=10,
                )
                room.save()
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully populated Room table'))