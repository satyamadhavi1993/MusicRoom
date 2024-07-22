from datetime import datetime, time, timedelta, date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
import json
from .models import Reservation, Room


def calendar(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        selected_time_slot = request.POST.get('time_slot')
        selected_room_type = request.POST.get('room_type')
        context = {'date': selected_date, 'time': selected_time, 'time_slot': selected_time_slot, 'room_type': selected_room_type}
        print('Calendar post context ', context)
        return redirect(reverse('booking:reserve') + f'?date={selected_date}&time_slot={selected_time_slot}&time={selected_time}&room_type={selected_room_type}')
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
    room_types = ['Solo', 'Duet', 'Band']
    
    reservations = Reservation.objects.filter(room__date=current_date)
    reservation_data = []
    for reservation in reservations:
        reservation_data.append({
            'time': reservation.room.time.strftime('%I:%M %p'),
            'room_type': reservation.room_type
        })
    
    
    
    for time in times_list:
        datetime_obj = datetime.combine(current_date, time)
        end_time = (datetime_obj + timedelta(hours=1)).time()

        room = Room.objects.get(date=current_date, time=time)
        start_time, end_time = get_timeslots(time, end_time)
        time_slot_data[time] = {
                'start_time': start_time,
                'end_time': end_time,
                'available_solo_rooms': room.available_solo_rooms,
                'available_duet_rooms': room.available_duet_rooms,
                'available_band_rooms': room.available_band_rooms,
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
            'reservations': json.dumps(reservation_data)
        }
    return render(request, 'booking/calendar.html', context)


@login_required
def reserve(request):
    if request.method == 'POST':
        user = request.user
        date = request.POST.get('date')
        time = request.POST.get('time')
        time_slot = request.POST.get('time_slot')
        room_type = request.POST.get('room_type')
        print(f'POST reserve data {user}, {date}, {time}, {time_slot}, {room_type}')
        
        date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
        time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M')
        
        room = Room.objects.filter(date=date, time=time).first()
        if room_type == 'Solo':
            room.available_solo_rooms -= 1
        elif room_type == 'Duet':
            room.available_duet_rooms -= 1
        elif room_type == 'Band':
            room.available_band_rooms -= 1
        room.save()
        
        reservation = Reservation.objects.create(user=user, room=room, room_type=room_type)
        reservation.save()
        
        return redirect('booking:calendar')
    
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    selected_time_slot = request.GET.get('time_slot')
    selected_room_type = request.GET.get('room_type')
    
    context = {
        'date': selected_date,
        'time': selected_time,
        'time_slot': selected_time_slot,
        'room_type': selected_room_type,
        'user': request.user,
    }
    print(f'GET reserve - {context}')
    return render(request, 'booking/reserve.html', context)


@login_required
def reservations(request):
    today = date.today()
    upcoming_reservations = Reservation.objects.filter(room__date__gte=today).order_by('room__date', 'room__time')
    past_reservations = Reservation.objects.filter(room__date__lt=today).order_by('-room__date', '-room__time')
    return render(request, 'booking/reservations.html', 
                  {'upcoming_reservations': upcoming_reservations, 'past_reservations': past_reservations})


def get_timeslots(start_time, end_time):
    return (start_time.strftime('%I:%M %p'), end_time.strftime('%I:%M %p'))
