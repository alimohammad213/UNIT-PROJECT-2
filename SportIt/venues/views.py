from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import Venue
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from bookings.models import Review
from django.db.models import Q, Avg
# Create your views here.

@login_required
def add_venue(request: HttpRequest):
    sport_choices = Venue._meta.get_field('sport_type').choices
    if request.method == 'POST':
        name = request.POST.get('name')
        sport_type = request.POST.get('sport_type')
        city = request.POST.get('city')
        location = request.POST.get('location')
        price_per_hour = request.POST.get('price_per_hour')
        amenities = request.POST.get('amenities', '')
        image = request.FILES.get('image')  
        
        if name and sport_type and location and price_per_hour:
            try:
                venue = Venue(
                    owner=request.user,
                    name=name,
                    sport_type=sport_type,
                    city=city,
                    location=location,
                    price_per_hour=Decimal(price_per_hour),
                    amenities=amenities,
                    image=image
                )
                venue.save()
                return redirect('venues:manage_venues')
            except ValueError:
                return render(request, 'venues/add_venue.html', {'error': 'Invalid price format.'})
        else:
            return render(request, 'venues/add_venue.html', {'error': 'All fields are required.'})
    
    sport_choices = Venue._meta.get_field('sport_type').choices
    return render(request, 'venues/add_venue.html', {'sport_choices': sport_choices})


@login_required
def edit_venue(request: HttpRequest, venue_id: int):
    try:
        venue = Venue.objects.get(id=venue_id, owner=request.user)
        sport_choices = Venue._meta.get_field('sport_type').choices
    except Venue.DoesNotExist:
        return redirect('venues:manage_venues')  

    if request.method == 'POST':
        name = request.POST.get('name')
        sport_type = request.POST.get('sport_type')
        city = request.POST.get('city')
        location = request.POST.get('location')
        price_per_hour = request.POST.get('price_per_hour')
        amenities = request.POST.get('amenities', '')
        image = request.FILES.get('image')
        
        if name and sport_type and location and price_per_hour:
            try:
                venue.name = name
                venue.sport_type = sport_type
                venue.city = city if city is not None else ''
                venue.location = location
                venue.price_per_hour = Decimal(price_per_hour)
                venue.amenities = amenities
                if image:
                    venue.image.save(image.name, image)
                venue.save()
                return redirect('venues:manage_venues')
            except ValueError:
                return render(request, 'venues/edit_venue.html', {
                    'venue': venue,
                    'error': 'Invalid price format.'
                })
        else:
            return render(request, 'venues/edit_venue.html', {
                'venue': venue,
                'error': 'All fields are required.'
            })
    
    sport_choices = Venue._meta.get_field('sport_type').choices
    return render(request, 'venues/edit_venue.html', {
        'venue': venue,
        'sport_choices': sport_choices
    })



@login_required
def delete_venue(request: HttpRequest, venue_id: int):
    venue = Venue.objects.get(id=venue_id, owner=request.user)
    if request.method == 'POST':
        venue.delete()
        return redirect('venues:manage_venues')
    
    return render(request, 'venues/delete_venue.html', {'venue': venue})


def venue_detail(request: HttpRequest, venue_id: int):
    venue = Venue.objects.get(id=venue_id)
    reviews = Review.objects.filter(venue=venue).order_by('-created_at')
    return render(request, 'venues/venue_detail.html', {
        'venue': venue,
        'reviews': reviews
    })


@login_required
def manage_venues(request: HttpRequest):
    venues = Venue.objects.filter(owner=request.user)
    return render(request, 'venues/manage_venues.html', {'venues': venues})


def search_venues(request : HttpRequest):
    query = request.GET.get('q', '').strip()
    sport_query = request.GET.get('sport', '').strip()

    venues = Venue.objects.all()

    if query:
        venues = venues.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )

    if sport_query:
        venues = venues.filter(sport_type=sport_query)

    
    featured_venues = Venue.objects.filter(image__isnull=False).annotate(
        avg_rating=Avg('review__rating')
    ).order_by('-avg_rating')[:3]

    raw_choices = Venue._meta.get_field('sport_type').choices

    sport_icon_map = {
    'padel': 'sports_tennis',
    'tennis': 'sports_tennis',
    'football': 'sports_soccer',
    'basketball': 'sports_basketball',
}
    
    raw_choices = list(Venue._meta.get_field('sport_type').get_choices(include_blank=False))
    sport_choices = [(val, label, sport_icon_map.get(val, 'sports')) for val, label in raw_choices]
            
    return render(request, 'core/home.html', {
        'venues': venues,
        'featured_venues': featured_venues,
        'query': query,
        'sport_query': sport_query,
        'sport_choices': sport_choices
    })