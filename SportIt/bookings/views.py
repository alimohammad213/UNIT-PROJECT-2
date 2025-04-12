from django.shortcuts import render, redirect
from django.http import HttpRequest
from datetime import datetime, timedelta, time
from .models import Booking, Venue
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from bookings.models import Review
from django.core.mail import send_mail
import stripe
from django.conf import settings
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
@login_required(login_url='users:login_page')
def book_venue(request: HttpRequest, venue_id: int):
    venue = Venue.objects.get(id=venue_id)
    now = timezone.localtime()
    today = now.date()
    max_day = today + timedelta(days=6)

    selected_date_str = request.POST.get('booking_date') or request.GET.get('booking_date') or ''
    selected_hour_str = request.POST.get('booking_hour') or ''
    duration = request.POST.get('duration') or ''

    base_hours = list(range(15, 24)) + list(range(0, 3))  
    available_hours: list[int] = []

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

            if selected_date == today:
                for h in base_hours:
                    booking_date = selected_date if h >= 3 else selected_date + timedelta(days=1)
                    booking_time = timezone.make_aware(datetime.combine(booking_date, time(h, 0)))
                    if booking_time > now:
                        available_hours.append(h)
            else:
                available_hours = base_hours

        except ValueError:
            available_hours = base_hours
    else:

        available_hours = base_hours

    if request.method == 'POST':
        if not selected_date_str or not selected_hour_str or not duration:
            return render(request, 'bookings/book_venue.html', {
                'venue': venue,
                'error': 'Please fill in all fields.',
                'available_hours': available_hours,
                'selected_date': selected_date_str,
                'selected_hour': selected_hour_str,
                'duration': duration,
                'min_date': today,
                'max_date': max_day
            })

        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            start_hour = int(selected_hour_str)
            duration_hours = int(duration)

            if duration_hours not in [1, 2]:
                raise ValueError("Invalid duration.")

            start_datetime = timezone.make_aware(datetime.combine(
            selected_date if start_hour >= 3 else selected_date + timedelta(days=1),
            time(start_hour, 0)
            ))
            end_datetime = start_datetime + timedelta(hours=duration_hours)


            if selected_date < today or selected_date > max_day:
                raise ValueError("Date must be from today to the next 6 days.")

            if start_datetime <= now:
                raise ValueError("You can't book past hours.")

            if Booking.objects.filter(
                venue=venue,
                status='confirmed',
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            ).exists():
                raise ValueError("This time slot is already booked.")

            total_price = venue.price_per_hour * Decimal(str(duration_hours))

            booking = Booking.objects.create(
                user=request.user,
                venue=venue,
                start_time=start_datetime,
                end_time=end_datetime,
                total_price=total_price,
                status='pending'
            )
            booking.save()

            stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'sar',
                        'unit_amount': int(total_price * 100),  
                        'product_data': {
                            'name': f"{venue.name} Booking",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment/success'),
                cancel_url=request.build_absolute_uri('/payment/cancel/'),
            )
            return redirect('bookings:booking_summary', booking_id=booking.id)

        except ValueError as e:
            return render(request, 'bookings/book_venue.html', {
                'venue': venue,
                'error': str(e),
                'available_hours': available_hours,
                'selected_date': selected_date_str,
                'selected_hour': selected_hour_str,
                'duration': duration,
                'min_date': today,
                'max_date': max_day
            })
        
    if not available_hours:
        available_hours = base_hours
    return render(request, 'bookings/book_venue.html', {
        'venue': venue,
        'available_hours': available_hours,
        'selected_date': selected_date_str,
        'selected_hour': selected_hour_str,
        'duration': duration,
        'min_date': today,
        'max_date': max_day
    })

@login_required
def booking_summary(request : HttpRequest, booking_id : int):
    booking = Booking.objects.get(id=booking_id, user=request.user)

    duration = booking.end_time - booking.start_time

    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    if hours and minutes:
        duration_display = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minutes"
    elif hours:
        duration_display = f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes:
        duration_display = f"{minutes} minutes"
    else:
        duration_display = "Less than a minute"

    if booking.status != 'pending':
        return redirect('home')  

    return render(request, 'bookings/booking_summary.html', {
        'booking': booking, 
        'duration_display': duration_display

    })

@login_required
def confirm_payment(request : HttpRequest, booking_id : int):

    booking = Booking.objects.get(id=booking_id, user=request.user)

    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'sar',
                    'unit_amount': int(booking.total_price * 100),
                    'product_data': {
                        'name': f"{booking.venue.name} Booking",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payment/success?booking_id={booking.id}'),
            cancel_url=request.build_absolute_uri('/payment/cancel/'),
        )
        return redirect(session.url)
    return redirect('home')

    
def send_booking_confirmation(booking: Booking):
    subject = f'Booking Confirmation for {booking.venue.name}'
    message = f'Your booking from {booking.start_time} to {booking.end_time} is confirmed!'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [booking.user.email])


def payment_success(request: HttpRequest):
    
    booking_id = request.GET.get('booking_id')
    if booking_id:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'confirmed'
        booking.save()
        
        subject = f"Booking Confirmation - {booking.venue.name}"
        local_start = timezone.localtime(booking.start_time)
        local_end = timezone.localtime(booking.end_time)
        message = (
            f"Hi {booking.user.username},\n\n"
            f"Your booking for {booking.venue.name} has been confirmed! 🎉\n\n"
            f"📍 Details:\n"
            f"- Sport: {booking.venue.sport_type}\n"
            f"- Location: {booking.venue.location}, {booking.venue.city}\n"
            f"- Date: {local_start.strftime('%A, %B %d, %Y')}\n"
            f"- Time: {local_start.strftime('%I:%M %p')} - {local_end.strftime('%I:%M %p')}\n"
            f"- Duration: {int((booking.end_time - booking.start_time).total_seconds() // 3600)} hour(s)\n"
            f"- Total Price: ﷼ {booking.total_price}\n\n"
            f"Thanks for using Sport It! ⚽️🏀🎾\n"
            f"Enjoy your game! 💪"
            f"\n\nIf you have any questions, feel free to contact us.\n\n"
            f"Best,\nSport It Team\n"
)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            fail_silently=False,
        )
    return render(request, 'bookings/payment_success.html')

def payment_cancel(request: HttpRequest):
    return render(request, 'bookings/payment_cancel.html')


@login_required
def add_review(request: HttpRequest, booking_id: int):
    booking = Booking.objects.get(id=booking_id)
    
    if Review.objects.filter(booking=booking).exists():
        return redirect('users:profile')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            review = Review(
                user=request.user,
                venue=booking.venue,
                booking=booking,
                rating=int(rating),
                comment=comment
            )
            review.save()
            return redirect('users:profile')
        else:
            return render(request, 'bookings/add_review.html', {
                'booking': booking,
                'error': 'Please select a valid rating (1-5).'
            })
    
    return render(request, 'bookings/add_review.html', {'booking': booking})