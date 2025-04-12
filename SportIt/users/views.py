from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.utils import timezone
from bookings.models import Booking
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Create your views here.

def signup(request: HttpRequest):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_page(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get('username')  
        password = request.POST.get('password')
        if username and password:  
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully", "success")
                return redirect('home')  
            else:
                messages.error(request, "Invalid username or password", "error")
        else:
            messages.error(request, "Please provide both username and password", "error")
    return render(request, "users/login.html")

@login_required
def logout_page(request: HttpRequest):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'users/logout.html')



@login_required
def profile(request: HttpRequest):
    filter_type = request.GET.get('filter', 'all')
    bookings = Booking.objects.filter(user=request.user)
    
    if filter_type == 'upcoming':
        bookings = bookings.filter(start_time__gte=timezone.now())
    elif filter_type == 'past':
        bookings = bookings.filter(end_time__lt=timezone.now())
    
    bookings = bookings.order_by('-start_time')
    return render(request, 'users/profile.html', {
        'bookings': bookings,
        'filter_type': filter_type,
        'user': request.user,
        'now': timezone.now()  
    })


