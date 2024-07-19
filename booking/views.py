from datetime import datetime, time, timedelta, date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse

from .models import Reservation, Room


@login_required
def calendar(request):
    if request.method == 'POST':
        print('POST Calendar')
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        selected_room_type = request.POST.get('room_type')
        context = {'date': selected_date, 'time': selected_time, 'room_type': selected_room_type}
        print(f'{selected_date}, {selected_time}, {selected_room_type}')
        return redirect(reverse('booking:reserve') + f'?date={selected_date}&time={selected_time}&room_type={selected_room_type}')
    elif request.method == "GET":
        print('GET Calendar')
        date_str = request.GET.get('date')
        if date_str:
            try:
                current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                current_date = date.today()
        else:
            current_date = date.today()
        
        current_day = current_date.strftime('%A')
        # Get the room data for the specified date
        times_list = list(Room.objects.filter(date=current_date).values_list('time', flat=True))
        time_slot_data = {}
        room_types = ['Single', 'Double', 'Family']

        for time in times_list:
            datetime_obj = datetime.combine(current_date, time)
            end_time = (datetime_obj + timedelta(hours=1)).time()

            room = Room.objects.get(date=current_date, time=time)
            start_time, end_time = get_timeslots(time, end_time)
            time_slot_data[time] = {
                'start_time': start_time,
                'end_time': end_time,
                'available_single_rooms': room.available_single_rooms,
                'available_double_rooms': room.available_double_rooms,
                'available_family_rooms': room.available_family_rooms,
            }

            # Calculate previous and next dates
        previous_date = current_date - timedelta(days=1)
        next_date = current_date + timedelta(days=1)

        context = {
            'current_day': current_day,
            'current_date': current_date,
            'time_slot_data': time_slot_data,
            'room_types': room_types,
            'previous_date': previous_date,
            'next_date': next_date,
            }
        return render(request, 'booking/calendar.html', context)


@login_required
def reservations(request):
    upcoming_reservations = Reservation.objects.filter(date__gte=now().date()).order_by('date', 'time')
    last_30_reservations = Reservation.objects.all().order_by('-date', '-time')[:30]
    return render(request, 'booking/reservations.html', {'upcoming_reservations': upcoming_reservations, 'last_30_reservations': last_30_reservations})


@login_required
def reserve(request):
    if request.method == "POST":
        print('POST reserve')
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        selected_room_type = request.POST.get('room_type')
        context = {
        'date': selected_date,
        'time': selected_time,
        'room_type': selected_room_type,
        # 'user': request.user,
        }
        return HttpResponse('Thank you booking')
    print('GET reserve')
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    selected_room_type = request.GET.get('room_type')
    
    context = {
        'date': selected_date,
        'time': selected_time,
        'room_type': selected_room_type,
        # 'user': request.user,
    }
    print(f'{selected_date}, {selected_time}, {selected_room_type} ')
    return render(request, 'booking/reserve.html', context)



def get_timeslots(start_time, end_time):
    return (start_time.strftime('%I:%M %p'), end_time.strftime('%I:%M %p'))
