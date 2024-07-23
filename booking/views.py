from datetime import datetime, time, timedelta, date
from dateutil import parser

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

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
        
        selected_date = datetime.strptime(selected_date, "%B %d, %Y").strftime("%Y-%m-%d")
        selected_time = datetime.strptime(selected_time, '%I:%M %p').strftime('%H:%M')
        
        reservation = Reservation.objects.filter(user=request.user, room__date=selected_date, room__time=selected_time, room_type=selected_room_type)
        if reservation:
            return redirect(reverse('booking:cancel_reservation') + f'?date={date}&time={time}&room_type={selected_room_type}')
        
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
    
    reservations = Reservation.objects.filter(user=request.user).filter(room__date=current_date)
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
    parsed_date = parser.parse(selected_date).date()
    parsed_time = parser.parse(selected_time).time()
    # date = datetime.strptime(selected_date, "%B %d, %Y").date()
    # time = datetime.strptime(selected_time, '%I:%M %p').time()
    now = timezone.now()
    
    if parsed_date < now.date() or (parsed_date == now.date() and parsed_time < now.time()):
        context.update({'error_message': 'Cannot book a room for a past date or time.'})
        return render(request, 'booking/reserve.html', context)
    
    print(f'GET reserve - {context}')
    return render(request, 'booking/reserve.html', context)


@login_required
def reservations(request):
    if request.method == 'POST':
        user = request.user
        reservation_date = request.POST.get('date')
        reservation_time = request.POST.get('time')
        room_type = request.POST.get('room_type')
        return redirect(reverse('booking:cancel_reservation') + f'?date={reservation_date}&time={reservation_time}&room_type={room_type}')
    
    today = date.today()
    upcoming_reservations = Reservation.objects.filter(user=request.user).filter(room__date__gte=today).order_by('room__date', 'room__time')
    print(upcoming_reservations)
    past_reservations = Reservation.objects.filter(user=request.user).filter(room__date__lt=today).order_by('-room__date', '-room__time')
    return render(request, 'booking/reservations.html', 
                  {'upcoming_reservations': upcoming_reservations, 'past_reservations': past_reservations})


@login_required
def cancel_reservation(request):
    if request.method == 'POST':
        user = request.user
        date = request.POST.get('date')
        time = request.POST.get('time')
        # time_slot = request.POST.get('time_slot')
        room_type = request.POST.get('room_type')
        print(f'POST cancel data {user}, {date}, {time}, {room_type}')
        
        date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
        time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M')
        
        room = Room.objects.filter(date=date, time=time).first()
        if room_type == 'Solo':
            room.available_solo_rooms += 1
        elif room_type == 'Duet':
            room.available_duet_rooms += 1
        elif room_type == 'Band':
            room.available_band_rooms += 1
        room.save()
        
        reservation = Reservation.objects.get(user=user, room=room, room_type=room_type)
        reservation.delete()
        
        return redirect('booking:calendar')
    
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    # selected_time_slot = request.GET.get('time_slot')
    selected_room_type = request.GET.get('room_type')
    
    context = {
        'date': selected_date,
        'time': selected_time,
        # 'time_slot': selected_time_slot,
        'room_type': selected_room_type,
        'user': request.user,
    }
    print(f'GET cancel - {context}')
    return render(request, 'booking/cancel_reservation.html', context)


def get_timeslots(start_time, end_time):
    return (start_time.strftime('%I:%M %p'), end_time.strftime('%I:%M %p'))
