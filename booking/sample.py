from datetime import date, timedelta, datetime
from django.utils import timezone


def populate_room_table():
    # slot_times = [datetime.strptime(f"{hour}:00", "%H:%M").time() for hour in range(8, 23)]
    # print(timezone.now().date())
    # current_datetime = timezone.now()
    # start_date = current_datetime.date()
    # days_until_sunday = (6 - start_date.weekday()) % 7
    # end_date = start_date + timedelta(days=days_until_sunday)
    # print(end_date)
    # current_date = start_date
    # while current_date <= end_date:
    #     print(current_date)
    #     for slot_time in slot_times:
    #         pass
    #     current_date += timedelta(days=1)
    print(date.today())
    

if __name__ == "__main__":
    populate_room_table()