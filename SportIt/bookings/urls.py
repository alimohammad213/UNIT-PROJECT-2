from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [ 
    path('book/<int:venue_id>/', views.book_venue, name='book_venue'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('review/<int:booking_id>/', views.add_review, name='add_review'),
    path('summary/<int:booking_id>/', views.booking_summary, name='booking_summary'),
    path('confirm-payment/<int:booking_id>/', views.confirm_payment, name='confirm_payment'),


]