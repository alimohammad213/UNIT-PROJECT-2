from django.forms import ModelForm
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from venues.models import Venue
from bookings.models import Review
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required for booking notifications")
    phone_number = forms.CharField(max_length=15, required=False, help_text="Optional phone number")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')

class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'sport_type', 'location', 'price_per_hour', 'amenities']

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']