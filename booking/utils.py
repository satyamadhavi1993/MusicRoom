from datetime import date, timedelta, datetime
from .models import Room

def populate_room_table():
    # Define the slot times from 8:00 AM to 10:00 PM
    slot_times = [datetime.strptime(f"{hour}:00", "%H:%M").time() for hour in range(8, 23)]

    # Get today's date and calculate the end date (next Sunday)
    start_date = date.today()
    days_until_sunday = (6 - start_date.weekday()) % 7
    end_date = start_date + timedelta(days=days_until_sunday)

    current_date = start_date
    while current_date <= end_date:
        for slot_time in slot_times:
            # Create a Room object for each combination of date and slot_time
            room = Room.objects.create(
                date=current_date,
                time=slot_time,
                available_single_rooms=30,
                available_double_rooms=20,
                available_family_rooms=10,
            )
            room.save()

        current_date += timedelta(days=1)


def convert_timeformat(start_time, end_time):
    return (start_time.strftime('%I:%M %p'), end_time.strftime('%I:%M %p'))
