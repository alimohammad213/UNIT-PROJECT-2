from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('manage/', views.manage_venues, name='manage_venues'),
    path('add/', views.add_venue, name='add_venue'),
    path('edit/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('delete/<int:venue_id>/', views.delete_venue, name='delete_venue'),
]