from datetime import datetime, timedelta
from dateutil import parser

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

import json

from .models import Reservation, Room

from .utils import convert_timeformat

from django.http import HttpResponse

from pycountry import countries

def calendar(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        selected_time_slot = request.POST.get('time_slot')
        selected_room_type = request.POST.get('room_type')
        
        context = {'date': selected_date, 'time': selected_time, 'time_slot': selected_time_slot, 'room_type': selected_room_type}
        print('Calendar post context ', context)
        
        selected_date = parser.parse(selected_date).date()
        selected_time = parser.parse(selected_time).time()
        
        now = timezone.now()
    
        if selected_date < now.date() or (selected_date == now.date() and selected_time < now.time()):
            print(f'Current date: {now.date()}, Reserve date: {selected_date}, Current time: {now.time()}, Reserve time: {selected_time}')
            context.update({'error_message': 'Cannot book/cancel a studio from a past date or time.'})
            return render(request, 'booking/reserve.html', context)
        
        if request.user.is_authenticated:
            reservation = Reservation.objects.filter(user=request.user, room__date=selected_date, room__time=selected_time, room_type=selected_room_type)
            if reservation:
                return redirect(reverse('booking:cancel_reservation') + 
                                f'?date={selected_date.strftime("%B %d, %Y")}&time_slot={selected_time_slot}&time={selected_time.strftime("%I:%M %p")}&room_type={selected_room_type}')
        else:
            return redirect('user:login')
        
        return redirect(reverse('booking:reserve') + 
                        f'?date={selected_date}&time_slot={selected_time_slot}&time={selected_time}&room_type={selected_room_type}')
    
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = parser.parse(date_str).date()
        except ValueError:
            current_date = timezone.now().date()
    else:
        current_date = timezone.now().date()
        
    current_day = current_date.strftime('%A')
    
    # Get the room data for the specified date
    times_list = list(Room.objects.filter(date=current_date).values_list('time', flat=True))
    time_slot_data = {}
    room_types = ['Solo', 'Duet', 'Band']
    
    for time in times_list:
        datetime_obj = datetime.combine(current_date, time)
        end_time = (datetime_obj + timedelta(hours=1)).time()

        room = Room.objects.get(date=current_date, time=time)
        start_time, end_time = convert_timeformat(time, end_time)
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
            'previous_date': previous_date,
            'next_date': next_date,
            'time_slot_data': time_slot_data,
            'room_types': room_types
        }
    
    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(user=request.user, room__date=current_date)
        reservation_data = []
        for reservation in reservations:
            reservation_data.append({
                'time': reservation.room.time.strftime('%I:%M %p'),
                'room_type': reservation.room_type
            })
        context.update({'reservations': json.dumps(reservation_data)})
    
    return render(request, 'booking/calendar.html', context)


@login_required
def reserve(request):
    user = request.user
    if request.method == 'POST':
        reserve_date = request.POST.get('date')
        reserve_time = request.POST.get('time')
        reserve_time_slot = request.POST.get('time_slot')
        reserve_room_type = request.POST.get('room_type')
        
        print(f'POST reserve data {user}, {reserve_date}, {reserve_time}, {reserve_time_slot}, {reserve_room_type}')
        
        reserve_date = parser.parse(reserve_date).date()
        reserve_time = parser.parse(reserve_time).time()
        
        room = Room.objects.filter(date=reserve_date, time=reserve_time).first()
        if reserve_room_type == 'Solo' and room.available_solo_rooms > 0:
            room.available_solo_rooms -= 1
        elif reserve_room_type == 'Duet' and room.available_duet_rooms > 0:
            room.available_duet_rooms -= 1
        elif reserve_room_type == 'Band' and room.available_band_rooms > 0:
            room.available_band_rooms -= 1
        
        room.save()
        
        reservation = Reservation.objects.create(user=user, room=room, room_type=reserve_room_type)
        reservation.save()
        
        return redirect(reverse('booking:calendar') + f'?date={reserve_date.strftime("%Y-%m-%d")}')
    
    
    reserve_date = request.GET.get('date')
    reserve_time = request.GET.get('time')
    reserve_time_slot = request.GET.get('time_slot')
    reserve_room_type = request.GET.get('room_type')
    
    reserve_date = parser.parse(reserve_date).date()
    reserve_time = parser.parse(reserve_time).time()
    
    room = Room.objects.filter(date=reserve_date, time=reserve_time).first()
    context = {
        'date': reserve_date.strftime("%B %d, %Y"),
        'time': reserve_time.strftime("%I:%M %p"),
        'time_slot': reserve_time_slot,
        'room_type': reserve_room_type,
        'user': request.user,
        'solo': room.available_solo_rooms,
        'duet': room.available_duet_rooms,
        'band': room.available_band_rooms
    }
    
    now = timezone.now()
    
    if reserve_date < now.date() or (reserve_date == now.date() and reserve_time < now.time()):
        print(f'Current date: {now.date()}, Reserve date: {reserve_date}, Current time: {now.time()}, Reserve time: {reserve_time}')
        context.update({'error_message': 'Cannot book/cancel a studio from a past date or time.'})
        return render(request, 'booking/reserve.html', context)
    

    if room:
        attribute_name = f'available_{reserve_room_type.lower()}_rooms'
        if getattr(room, attribute_name) == 0:
            context.update({'error_message': 'All studios are fully booked for the selected time. Please choose a different time or studio.'})
            return render(request, 'booking/reserve.html', context)
    
    if request.user.is_authenticated:
        reservations_count = Reservation.objects.filter(user=user, room__date=reserve_date).count()
        if reservations_count >= 2:
            context.update({'error_message': 'Cannot book more than two studios per day.'})
            return render(request, 'booking/reserve.html', context)
    else:
        return redirect('user:login')   
    
    print(f'GET reserve - {context}')
    return render(request, 'booking/reserve.html', context)


@login_required
def reservations(request):
    if request.method == 'POST':
        user = request.user
        reservation_date = request.POST.get('date')
        reservation_time = request.POST.get('time')
        reservation_room_type = request.POST.get('room_type')
        
        parsed_date = parser.parse(reservation_date).date()
        parsed_time = parser.parse(reservation_time).time()
        date_object = datetime.combine(parsed_date, parsed_time)
        reservation_time = parsed_time.strftime('%I:%M %p')
        reservation_end_time = (date_object + timedelta(hours=1)).time().strftime('%I:%M %p')
        reservation_time_slot = f'{reservation_time} - {reservation_end_time}'
        return redirect(reverse('booking:cancel_reservation') + 
                        f'?date={reservation_date}&time={reservation_time}&time_slot={reservation_time_slot}&room_type={reservation_room_type}')
    
    today = timezone.now().date()
    upcoming_reservations = Reservation.objects.filter(user=request.user, room__date__gte=today).order_by('room__date', 'room__time')
    print(upcoming_reservations)
    past_reservations = Reservation.objects.filter(user=request.user, room__date__lt=today).order_by('-room__date', '-room__time')
    return render(request, 'booking/reservations.html', 
                  {'upcoming_reservations': upcoming_reservations, 'past_reservations': past_reservations})


@login_required
def cancel_reservation(request):
    if request.method == 'POST':
        user = request.user
        cancel_date = request.POST.get('date')
        cancel_time = request.POST.get('time')
        time_slot = request.POST.get('time_slot')
        cancel_room_type = request.POST.get('room_type')
        print(f'POST cancel data {user}, {cancel_date}, {cancel_time}, {cancel_room_type}')
        
        cancel_date = parser.parse(cancel_date).date()
        cancel_time = parser.parse(cancel_time).time()
        
        room = Room.objects.filter(date=cancel_date, time=cancel_time).first()
        if cancel_room_type == 'Solo' and room.available_solo_rooms < 30:
            room.available_solo_rooms += 1
        elif cancel_room_type == 'Duet' and room.available_duet_rooms < 20:
            room.available_duet_rooms += 1
        elif cancel_room_type == 'Band' and room.available_band_rooms < 10:
            room.available_band_rooms += 1
        room.save()
        
        reservation = Reservation.objects.get(user=user, room=room, room_type=cancel_room_type)
        reservation.delete()
        
        return redirect(reverse('booking:calendar') + f'?date={cancel_date.strftime("%Y-%m-%d")}')
    
    cancel_date = request.GET.get('date')
    cancel_time = request.GET.get('time')
    cancel_time_slot = request.GET.get('time_slot')
    # cancel_time_slot = f"{request.GET.get('time')} - {request.GET.get('endtime')}"
    cancel_room_type = request.GET.get('room_type')
    
    room = Room.objects.filter(date=parser.parse(cancel_date).date(), time=parser.parse(cancel_time).time()).first()
    
    context = {
        'date': cancel_date,
        'time': cancel_time,
        'time_slot': cancel_time_slot,
        'room_type': cancel_room_type,
        'user': request.user,
        'solo': room.available_solo_rooms,
        'duet': room.available_duet_rooms,
        'band': room.available_band_rooms
    }
    print(f'GET cancel - {context}')
    return render(request, 'booking/cancel_reservation.html', context)


@login_required
def my_profile(request):
    user = request.user
    if request.method == 'POST':
        print('POST My Profile')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        country = request.POST.get('country')
        
        user = User.objects.get(username=user.username)
        
        return render('booking/my_profile.html')
        
        
    print('GET My Profile')
    context = {
        'user': user,
        'countries': countries
    }
    if user.is_authenticated:
        return render(request, 'booking/my_profile.html', context)
    else:
        return redirect('user:login')


def home(request):
    return render(request, 'booking/home.html')


@login_required
def deactivate_account(request):
    return render(request, 'registration/deactivate_account.html')

