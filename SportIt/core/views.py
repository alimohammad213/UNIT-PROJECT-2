from django.shortcuts import render
from django.http import HttpRequest
from django.db.models import Avg, Q
from  venues.models import Venue
# Create your views here.


def home_page(request : HttpRequest): 
    query = request.GET.get('q', '').strip()
    sport_query = request.GET.get('sport', '').strip()
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    sort_query = request.GET.get('sort_by', '')

    venues = Venue.objects.all()

    if query:
        venues = venues.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )

    if sport_query:
        venues = venues.filter(sport_type=sport_query)

    if sort_query == "price_low":
        venues = venues.order_by("price_per_hour")
    elif sort_query == "price_high":
        venues = venues.order_by("-price_per_hour")

    featured_venues = Venue.objects.filter(image__isnull=False).annotate(
        avg_rating=Avg('review__rating')
    ).order_by('-avg_rating')[:3]

    field = Venue._meta.get_field('sport_type')
    raw_sport_choices = list(Venue._meta.get_field('sport_type').choices)

    sport_icon_map = {
        'padel': 'sports_tennis',
        'tennis': 'sports_tennis',
        'football': 'sports_soccer',
        'basketball': 'sports_basketball',
    }

    sport_choices = [
        ('', 'All Sports', 'sports')  
    ] + [
        (value, label, sport_icon_map.get(value, 'sports'))
        for value, label in raw_sport_choices
    ]

    return render(request, 'core/home.html', {
        'venues': venues,
        'featured_venues': featured_venues,
        'query': query,
        'sport_query': sport_query,
        'start_time': start_time,
        'end_time': end_time,
        'sort_query': sort_query,
        'sport_choices': sport_choices,
    })